"""
player_props.py — Player prop prediction model (scorer, shots on target, corners).
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path

from scipy.stats import poisson
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
RAW_PLAYERS_DIR = ROOT / "data" / "raw" / "player_stats"
PROCESSED_DIR = ROOT / "data" / "processed"
PLAYER_PROFILES_PATH = PROCESSED_DIR / "player_profiles.json"

DECAY_RATE = 0.005  # same as poisson_model
EXPECTED_MINUTES = 90.0


def _load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _per_90(value: float | None, minutes: float) -> float | None:
    if value is None or minutes is None or minutes < 1:
        return None
    return value / minutes * 90


def _decay_weight(days_ago: int) -> float:
    return math.exp(-DECAY_RATE * days_ago)


# ── Player Profile Computation ─────────────────────────────────────────────────

def compute_player_profiles(player_stats_dir: Path = RAW_PLAYERS_DIR) -> dict:
    """
    Load all cached player stats, compute per-90 rates with decay weighting.
    Saves to data/processed/player_profiles.json and returns the dict.
    """
    today = datetime.now(timezone.utc).date()
    profiles: dict[str, dict] = {}

    for pf in player_stats_dir.glob("*.json"):
        data = _load_json(pf)
        if not data:
            continue

        name = data.get("name", pf.stem)
        player_id = data.get("player_id", pf.stem)
        stats_raw = data.get("stats", {})

        # Handle both list-of-season-objects and dict formats
        if isinstance(stats_raw, dict):
            stat_entries = stats_raw.get("data", [stats_raw])
        elif isinstance(stats_raw, list):
            stat_entries = stats_raw
        else:
            continue

        # Aggregate across seasons/competitions with decay weighting
        totals: dict[str, float] = {}
        total_minutes = 0.0
        total_weight = 0.0

        for entry in stat_entries:
            season_str = str(entry.get("season", ""))
            # Estimate recency: 2025 season ~0 days ago, 2024 ~365 days ago
            if "2025" in season_str:
                days_ago = 0
            elif "2024" in season_str:
                days_ago = 200
            else:
                days_ago = 400
            w = _decay_weight(days_ago)

            minutes = float(entry.get("minutes_played") or entry.get("minutes") or 0)
            if minutes < 30:
                continue

            for stat_key in ["goals", "assists", "shots", "shots_on_target", "key_passes", "yellow_cards", "xg"]:
                val = entry.get(stat_key) or entry.get(stat_key.replace("_", ""))
                if val is not None:
                    totals[stat_key] = totals.get(stat_key, 0) + float(val) * w

            total_minutes += minutes * w
            total_weight += w

        if total_minutes < 30:
            continue

        profile = {
            "name": name,
            "player_id": player_id,
            "weighted_minutes": round(total_minutes, 1),
        }
        for stat_key in ["goals", "assists", "shots", "shots_on_target", "key_passes", "yellow_cards", "xg"]:
            if stat_key in totals:
                profile[f"{stat_key}_per_90"] = round(_per_90(totals[stat_key], total_minutes), 4)

        profiles[name] = profile

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "players": profiles,
    }
    PLAYER_PROFILES_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"[OK] Player profiles saved ({len(profiles)} players)")
    return output


def load_player_profiles() -> dict:
    if not PLAYER_PROFILES_PATH.exists():
        return {"players": {}}
    data = _load_json(PLAYER_PROFILES_PATH)
    return data if isinstance(data, dict) else {"players": {}}


# ── Anytime Scorer Prediction ──────────────────────────────────────────────────

def predict_anytime_scorer(
    player_name: str,
    home_team: str,
    away_team: str,
    team_ratings: dict,
    player_team: str = "",
    minutes_expected: float = EXPECTED_MINUTES,
    profiles: dict | None = None,
) -> dict:
    """
    P(player scores) using per-90 rate adjusted for opponent defense and match xG context.
    """
    if profiles is None:
        profiles = load_player_profiles()

    players = profiles.get("players", {})
    player = players.get(player_name)
    if not player:
        return {"player": player_name, "anytime_scorer_pct": None, "first_scorer_pct": None, "error": "not in profiles"}

    goals_per_90 = player.get("goals_per_90", 0.0) or 0.0
    if goals_per_90 == 0:
        return {"player": player_name, "anytime_scorer_pct": 0.0, "first_scorer_pct": 0.0}

    # Get opponent's defense strength
    teams = team_ratings.get("teams", {})
    avg_away_xg = team_ratings.get("avg_away_xg", 1.05)
    avg_home_xg = team_ratings.get("avg_home_xg", 1.35)

    # Determine if player is on home or away team
    is_home = player_team.lower() in home_team.lower() if player_team else True
    opponent = away_team if is_home else home_team
    opp_data = teams.get(opponent, {"defense_strength": 1.0})
    opp_defense = opp_data.get("defense_strength", 1.0)
    avg_xg_base = avg_home_xg if is_home else avg_away_xg

    # Adjust rate: stronger opponent defense = fewer goals expected
    adjusted_rate = goals_per_90 * (1 / opp_defense) if opp_defense > 0 else goals_per_90

    # Scale by match context (proportion of minutes played)
    lambda_val = adjusted_rate * (minutes_expected / 90)

    p_score = 1 - math.exp(-lambda_val)
    p_first = p_score / max(22 * p_score, 1)  # simplified: roughly 1/n_scorers

    return {
        "player": player_name,
        "anytime_scorer_pct": round(p_score * 100, 1),
        "first_scorer_pct": round(p_first * 100, 1),
        "goals_per_90": round(goals_per_90, 3),
        "adjusted_lambda": round(lambda_val, 3),
    }


# ── Shots on Target Prediction ─────────────────────────────────────────────────

def predict_shots_on_target(
    player_name: str,
    home_team: str,
    away_team: str,
    team_ratings: dict,
    player_team: str = "",
    minutes_expected: float = EXPECTED_MINUTES,
    profiles: dict | None = None,
) -> dict:
    """
    Over/under probabilities for DraftKings common SOT lines (0.5, 1.5, 2.5).
    """
    if profiles is None:
        profiles = load_player_profiles()

    players = profiles.get("players", {})
    player = players.get(player_name)
    if not player:
        return {"player": player_name, "error": "not in profiles"}

    sot_per_90 = player.get("shots_on_target_per_90") or player.get("shots_per_90", 0.0) * 0.4
    if not sot_per_90:
        return {"player": player_name, "error": "no shots data"}

    teams = team_ratings.get("teams", {})
    is_home = player_team.lower() in home_team.lower() if player_team else True
    opponent = away_team if is_home else home_team
    opp_data = teams.get(opponent, {"defense_strength": 1.0})
    opp_defense = opp_data.get("defense_strength", 1.0)
    adjusted_rate = sot_per_90 * (1 / opp_defense) if opp_defense > 0 else sot_per_90
    lambda_val = adjusted_rate * (minutes_expected / 90)

    result = {"player": player_name, "sot_per_90": round(sot_per_90, 3), "expected_sot": round(lambda_val, 2)}
    for line in [0.5, 1.5, 2.5]:
        k = int(line + 0.5)
        p_over = 1 - poisson.cdf(k - 1, lambda_val)
        p_under = 1 - p_over
        result[f"over_{line}_pct"] = round(p_over * 100, 1)
        result[f"under_{line}_pct"] = round(p_under * 100, 1)

    return result


# ── Team Corners Prediction ────────────────────────────────────────────────────

def predict_team_corners(
    home_team: str,
    away_team: str,
    team_ratings: dict,
    avg_total_corners: float = 9.8,
) -> dict:
    """
    Predict total corners over/under using attack strength as a proxy for corner generation.
    Returns probabilities for common lines (8.5, 9.5, 10.5).
    """
    teams = team_ratings.get("teams", {})
    home_data = teams.get(home_team, {"attack_strength": 1.0})
    away_data = teams.get(away_team, {"attack_strength": 1.0})

    # Higher attack strength → more possession/pressure → more corners
    home_attack = home_data.get("attack_strength", 1.0)
    away_attack = away_data.get("attack_strength", 1.0)
    combined_factor = (home_attack + away_attack) / 2
    expected_corners = avg_total_corners * combined_factor

    result = {
        "home_team": home_team,
        "away_team": away_team,
        "expected_total_corners": round(expected_corners, 1),
    }
    for line in [8.5, 9.5, 10.5]:
        k = int(line + 0.5)
        p_over = 1 - poisson.cdf(k - 1, expected_corners)
        result[f"over_{line}_pct"] = round(p_over * 100, 1)
        result[f"under_{line}_pct"] = round((1 - p_over) * 100, 1)

    return result


if __name__ == "__main__":
    print("Computing player profiles from cached data...")
    profiles = compute_player_profiles()
    print(f"Profiles built for {len(profiles.get('players', {}))} players.")
