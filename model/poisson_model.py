"""
poisson_model.py — xG-based Poisson model with Dixon-Coles correction.
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.stats import poisson
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
RAW_MATCHES_DIR = ROOT / "data" / "raw" / "matches"
RAW_XG_DIR = ROOT / "data" / "raw" / "xg"
PROCESSED_DIR = ROOT / "data" / "processed"
TEAM_RATINGS_PATH = PROCESSED_DIR / "team_ratings.json"

DIXON_COLES_RHO = -0.13
MAX_GOALS = 7  # compute scoreline probs for 0-0 through 6-6


def _load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ── Rating Computation ─────────────────────────────────────────────────────────

def compute_team_ratings(
    matches_dir: Path = RAW_MATCHES_DIR,
    xg_dir: Path = RAW_XG_DIR,
) -> dict:
    """
    Load cached match + xG data, apply exponential time-decay weighting,
    and compute attack/defense strength ratings per team via MLE.

    Returns ratings dict and saves to data/processed/team_ratings.json.
    """
    today = datetime.now(timezone.utc).date()

    # Build xG lookup: match_id -> {"home_xg": float, "away_xg": float}
    xg_lookup: dict[str, dict] = {}
    for xg_file in xg_dir.glob("*.json"):
        data = _load_json(xg_file)
        if not data:
            continue
        match_id = xg_file.stem
        home_xg = None
        away_xg = None
        # TheStatsAPI returns stats as a list or dict depending on endpoint
        if isinstance(data, dict):
            stats = data.get("data", data)
        else:
            stats = data
        if isinstance(stats, list):
            for entry in stats:
                side = entry.get("side", "").lower()
                val = entry.get("xg") or entry.get("expected_goals")
                if val is not None:
                    if side == "home":
                        home_xg = float(val)
                    elif side == "away":
                        away_xg = float(val)
        xg_lookup[match_id] = {"home_xg": home_xg, "away_xg": away_xg}

    # Collect all match records
    records: list[dict] = []
    for match_file in matches_dir.glob("*.json"):
        data = _load_json(match_file)
        if not data:
            continue
        match_id = match_file.stem
        try:
            match_date_str = (
                data.get("date") or data.get("match_date") or data.get("fixture", {}).get("date", "")
            )
            if not match_date_str:
                continue
            match_date = datetime.fromisoformat(match_date_str.replace("Z", "+00:00")).date()
            days_ago = (today - match_date).days
            if days_ago < 0:
                continue
            weight = math.exp(-0.005 * days_ago)

            home_team = (
                data.get("home_team")
                or data.get("teams", {}).get("home", {}).get("name", "")
            )
            away_team = (
                data.get("away_team")
                or data.get("teams", {}).get("away", {}).get("name", "")
            )
            if not home_team or not away_team:
                continue

            home_goals = data.get("home_goals") or data.get("goals", {}).get("home")
            away_goals = data.get("away_goals") or data.get("goals", {}).get("away")

            xg = xg_lookup.get(match_id, {})
            home_xg = xg.get("home_xg")
            away_xg = xg.get("away_xg")

            # Fall back to actual goals if xG unavailable
            if home_xg is None and home_goals is not None:
                home_xg = float(home_goals)
            if away_xg is None and away_goals is not None:
                away_xg = float(away_goals)

            if home_xg is None or away_xg is None:
                continue

            records.append({
                "home_team": home_team,
                "away_team": away_team,
                "home_xg": home_xg,
                "away_xg": away_xg,
                "weight": weight,
                "days_ago": days_ago,
            })
        except (ValueError, KeyError, TypeError):
            continue

    if not records:
        print("[WARN] No match records found. Run data_collector.py first.")
        return {}

    # Gather all teams and compute weighted league averages
    teams: set[str] = set()
    for r in records:
        teams.add(r["home_team"])
        teams.add(r["away_team"])

    total_weight = sum(r["weight"] for r in records)
    avg_home_xg = sum(r["home_xg"] * r["weight"] for r in records) / total_weight
    avg_away_xg = sum(r["away_xg"] * r["weight"] for r in records) / total_weight
    avg_xg = (avg_home_xg + avg_away_xg) / 2

    # Iterative MLE: attack and defense strengths
    # attack_i * defense_j * avg_xg = expected_xg for team i vs team j
    attack: dict[str, float] = {t: 1.0 for t in teams}
    defense: dict[str, float] = {t: 1.0 for t in teams}

    for _ in range(100):  # iterate to convergence
        # Update attack strengths
        for team in teams:
            home_records = [r for r in records if r["home_team"] == team]
            away_records = [r for r in records if r["away_team"] == team]
            numerator = (
                sum(r["home_xg"] * r["weight"] for r in home_records)
                + sum(r["away_xg"] * r["weight"] for r in away_records)
            )
            denominator = (
                sum(defense[r["away_team"]] * avg_home_xg * r["weight"] for r in home_records)
                + sum(defense[r["home_team"]] * avg_away_xg * r["weight"] for r in away_records)
            )
            if denominator > 0:
                attack[team] = numerator / denominator

        # Update defense strengths
        for team in teams:
            home_records = [r for r in records if r["home_team"] == team]
            away_records = [r for r in records if r["away_team"] == team]
            numerator = (
                sum(r["away_xg"] * r["weight"] for r in home_records)
                + sum(r["home_xg"] * r["weight"] for r in away_records)
            )
            denominator = (
                sum(attack[r["away_team"]] * avg_away_xg * r["weight"] for r in home_records)
                + sum(attack[r["home_team"]] * avg_home_xg * r["weight"] for r in away_records)
            )
            if denominator > 0:
                defense[team] = numerator / denominator

        # Normalize so mean attack = mean defense = 1
        mean_attack = np.mean(list(attack.values()))
        mean_defense = np.mean(list(defense.values()))
        attack = {t: v / mean_attack for t, v in attack.items()}
        defense = {t: v / mean_defense for t, v in defense.items()}

    # Match counts per team for confidence flagging
    match_counts: dict[str, int] = {}
    for r in records:
        match_counts[r["home_team"]] = match_counts.get(r["home_team"], 0) + 1
        match_counts[r["away_team"]] = match_counts.get(r["away_team"], 0) + 1

    ratings = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "avg_home_xg": round(avg_home_xg, 4),
        "avg_away_xg": round(avg_away_xg, 4),
        "avg_xg": round(avg_xg, 4),
        "teams": {
            t: {
                "attack_strength": round(attack[t], 4),
                "defense_strength": round(defense[t], 4),
                "match_count": match_counts.get(t, 0),
                "low_sample_warning": match_counts.get(t, 0) < 5,
            }
            for t in sorted(teams)
        },
    }

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TEAM_RATINGS_PATH.write_text(json.dumps(ratings, indent=2), encoding="utf-8")
    print(f"[OK] Team ratings saved ({len(teams)} teams, {len(records)} weighted matches)")
    return ratings


def load_ratings() -> dict:
    """Load team ratings from disk."""
    if not TEAM_RATINGS_PATH.exists():
        return {}
    data = _load_json(TEAM_RATINGS_PATH)
    return data if isinstance(data, dict) else {}


# ── Dixon-Coles Correction ─────────────────────────────────────────────────────

def dixon_coles_correction(home_goals: int, away_goals: int, rho: float = DIXON_COLES_RHO) -> float:
    """
    Correction factor for low-score outcomes (Dixon & Coles 1997).
    Only applies when both scores are 0 or 1.
    """
    if home_goals == 0 and away_goals == 0:
        return 1 - rho
    elif home_goals == 1 and away_goals == 0:
        return 1 + rho
    elif home_goals == 0 and away_goals == 1:
        return 1 + rho
    elif home_goals == 1 and away_goals == 1:
        return 1 - rho
    else:
        return 1.0


# ── Match Prediction ───────────────────────────────────────────────────────────

def predict_match(home_team: str, away_team: str, ratings: dict) -> dict:
    """
    Predict match outcome probabilities using Poisson model with Dixon-Coles correction.
    """
    teams = ratings.get("teams", {})
    avg_home_xg = ratings.get("avg_home_xg", 1.35)
    avg_away_xg = ratings.get("avg_away_xg", 1.05)

    home_data = teams.get(home_team, {"attack_strength": 1.0, "defense_strength": 1.0})
    away_data = teams.get(away_team, {"attack_strength": 1.0, "defense_strength": 1.0})

    # Expected goals using Dixon-Coles MLE formula
    home_xg = home_data["attack_strength"] * away_data["defense_strength"] * avg_home_xg
    away_xg = away_data["attack_strength"] * home_data["defense_strength"] * avg_away_xg

    warnings = []
    if home_data.get("low_sample_warning"):
        warnings.append(f"{home_team}: <5 matches in ratings data")
    if away_data.get("low_sample_warning"):
        warnings.append(f"{away_team}: <5 matches in ratings data")
    if home_team not in teams:
        warnings.append(f"{home_team}: not in ratings — using league average")
    if away_team not in teams:
        warnings.append(f"{away_team}: not in ratings — using league average")

    # Build scoreline probability matrix
    score_probs: dict[tuple[int, int], float] = {}
    total_mass = 0.0
    for h in range(MAX_GOALS):
        for a in range(MAX_GOALS):
            p = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
            correction = dixon_coles_correction(h, a)
            p *= correction
            score_probs[(h, a)] = p
            total_mass += p

    # Normalize (correction shifts probabilities slightly off 1.0)
    score_probs = {k: v / total_mass for k, v in score_probs.items()}

    # Aggregate markets
    home_win = sum(p for (h, a), p in score_probs.items() if h > a)
    draw = sum(p for (h, a), p in score_probs.items() if h == a)
    away_win = sum(p for (h, a), p in score_probs.items() if a > h)

    over_25 = sum(p for (h, a), p in score_probs.items() if h + a > 2)
    under_25 = 1 - over_25
    over_15 = sum(p for (h, a), p in score_probs.items() if h + a > 1)
    under_15 = 1 - over_15
    btts_yes = sum(p for (h, a), p in score_probs.items() if h > 0 and a > 0)
    btts_no = 1 - btts_yes
    home_cs = sum(p for (h, a), p in score_probs.items() if a == 0)
    away_cs = sum(p for (h, a), p in score_probs.items() if h == 0)

    # Top scorelines
    top_scorelines = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)[:5]
    top_scorelines_fmt = [
        {"score": f"{h}-{a}", "pct": round(p * 100, 1)}
        for (h, a), p in top_scorelines
    ]

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_xg_pred": round(home_xg, 2),
        "away_xg_pred": round(away_xg, 2),
        "home_win_pct": round(home_win * 100, 1),
        "draw_pct": round(draw * 100, 1),
        "away_win_pct": round(away_win * 100, 1),
        "over_2_5_pct": round(over_25 * 100, 1),
        "under_2_5_pct": round(under_25 * 100, 1),
        "over_1_5_pct": round(over_15 * 100, 1),
        "under_1_5_pct": round(under_15 * 100, 1),
        "btts_yes_pct": round(btts_yes * 100, 1),
        "btts_no_pct": round(btts_no * 100, 1),
        "home_clean_sheet_pct": round(home_cs * 100, 1),
        "away_clean_sheet_pct": round(away_cs * 100, 1),
        "top_scorelines": top_scorelines_fmt,
        "warnings": warnings,
    }


def generate_all_predictions(upcoming_fixtures: list, ratings: dict | None = None) -> list:
    """Run predict_match for every fixture. Save to model_predictions.json."""
    if ratings is None:
        ratings = load_ratings()
    if not ratings:
        print("[WARN] No ratings available — run compute_team_ratings() first")
        return []

    predictions = []
    for fixture in upcoming_fixtures:
        try:
            home = fixture.get("home_team") or fixture.get("teams", {}).get("home", {}).get("name")
            away = fixture.get("away_team") or fixture.get("teams", {}).get("away", {}).get("name")
            if home and away:
                pred = predict_match(home, away, ratings)
                predictions.append(pred)
        except Exception as e:
            print(f"[WARN] Prediction failed for fixture {fixture}: {e}")

    return predictions


def compute_edge(model_pct: float, american_odds: int) -> float:
    """
    Edge = model probability - market implied probability (percentage points).
    Positive = model thinks market is underpricing this outcome.
    """
    if american_odds > 0:
        implied = 100 / (american_odds + 100)
    else:
        implied = (-american_odds) / (-american_odds + 100)
    return round(model_pct / 100 - implied, 4) * 100  # return as percentage points


if __name__ == "__main__":
    print("Computing team ratings from cached data...")
    ratings = compute_team_ratings()
    if ratings:
        print(f"Ratings computed for {len(ratings.get('teams', {}))} teams.")
        # Quick smoke test
        teams = list(ratings.get("teams", {}).keys())
        if len(teams) >= 2:
            pred = predict_match(teams[0], teams[1], ratings)
            print(f"\nSample prediction: {pred['home_team']} vs {pred['away_team']}")
            print(f"  xG: {pred['home_xg_pred']} — {pred['away_xg_pred']}")
            print(f"  Win %: {pred['home_win_pct']} | {pred['draw_pct']} | {pred['away_win_pct']}")
