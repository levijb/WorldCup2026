"""
data_collector.py — One-time bulk data pull from TheStatsAPI during trial period.

Usage:
    python model/data_collector.py --teams-only     # pull team match history first
    python model/data_collector.py --players         # add player stats
    python model/data_collector.py --historical      # add 2018/2022 WC data
    python model/data_collector.py --resume          # skip already-cached files
    python model/data_collector.py --dry-run         # print plan, no API calls
"""

import argparse
import json
import os
import sys
import time
import unicodedata
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
RAW_MATCHES_DIR = ROOT / "data" / "raw" / "matches"
RAW_XG_DIR = ROOT / "data" / "raw" / "xg"
RAW_PLAYERS_DIR = ROOT / "data" / "raw" / "player_stats"
RAW_HISTORICAL_DIR = ROOT / "data" / "raw" / "wc_historical"
PROCESSED_DIR = ROOT / "data" / "processed"
TEAM_ID_MAP_PATH = PROCESSED_DIR / "team_id_map.json"

STATS_API_KEY = os.getenv("STATS_API_KEY", "")
STATS_API_BASE = "https://api.thestatsapi.com/api"

# ── All 48 World Cup 2026 teams ────────────────────────────────────────────────
WC_2026_TEAMS = [
    # Group A
    "United States", "Panama", "Honduras", "Jamaica",
    # Group B
    "Mexico", "Ecuador", "Venezuela", "Bolivia",
    # Group C
    "Canada", "Uruguay", "Peru", "Chile",
    # Group D
    "Argentina", "Paraguay", "Colombia", "Costa Rica",
    # Group E
    "Brazil", "Trinidad and Tobago", "Suriname", "El Salvador",
    # Group F
    "Germany", "Austria", "Switzerland", "North Macedonia",
    # Group G
    "Spain", "Portugal", "Morocco", "Comoros",
    # Group H
    "France", "Belgium", "Tunisia", "Senegal",
    # Group I
    "England", "Netherlands", "Republic of Ireland", "Moldova",
    # Group J
    "Italy", "Croatia", "Albania", "Ukraine",
    # Group K
    "Norway", "Sweden", "Denmark", "Finland",
    # Group L
    "Japan", "South Korea", "Saudi Arabia", "Australia",
]

# ── Player metadata for identity validation during search ─────────────────────
# Keys are accent-free names used as both the search term and the display name.
# nationality must match result["nationality"]; age must fall within age_range.
PLAYER_METADATA: dict[str, dict] = {
    "Kylian Mbappe":         {"nationality": "France",      "age_range": (24, 28)},
    "Harry Kane":            {"nationality": "England",     "age_range": (30, 33)},
    "Erling Haaland":        {"nationality": "Norway",      "age_range": (23, 26)},
    "Lionel Messi":          {"nationality": "Argentina",   "age_range": (36, 39)},
    "Cristiano Ronaldo":     {"nationality": "Portugal",    "age_range": (39, 42)},
    "Vinicius Junior":       {"nationality": "Brazil",      "age_range": (23, 26)},
    "Raphinha":              {"nationality": "Brazil",      "age_range": (27, 30)},
    "Lamine Yamal":          {"nationality": "Spain",       "age_range": (16, 18)},
    "Pedri":                 {"nationality": "Spain",       "age_range": (21, 23)},
    "Mikel Oyarzabal":       {"nationality": "Spain",       "age_range": (26, 29)},
    "Julian Alvarez":        {"nationality": "Argentina",   "age_range": (24, 26)},
    "Jude Bellingham":       {"nationality": "England",     "age_range": (20, 22)},
    "Bukayo Saka":           {"nationality": "England",     "age_range": (22, 24)},
    "Mohamed Salah":         {"nationality": "Egypt",       "age_range": (31, 34)},
    "Ousmane Dembele":       {"nationality": "France",      "age_range": (26, 29)},
    "Michael Olise":         {"nationality": "France",      "age_range": (22, 24)},
    "Martin Odegaard":       {"nationality": "Norway",      "age_range": (25, 28)},
    "Luis Diaz":             {"nationality": "Colombia",    "age_range": (27, 29)},
    "Neymar":                {"nationality": "Brazil",      "age_range": (32, 35)},
    "Bruno Fernandes":       {"nationality": "Portugal",    "age_range": (29, 32)},
    "Cody Gakpo":            {"nationality": "Netherlands", "age_range": (24, 27)},
    "Memphis Depay":         {"nationality": "Netherlands", "age_range": (29, 32)},
    "Son Heung-min":         {"nationality": "South Korea", "age_range": (31, 34)},
    "Kaoru Mitoma":          {"nationality": "Japan",       "age_range": (26, 29)},
    "Sadio Mane":            {"nationality": "Senegal",     "age_range": (31, 34)},
    "Leroy Sane":            {"nationality": "Germany",     "age_range": (29, 31)},
    "Florian Wirtz":         {"nationality": "Germany",     "age_range": (20, 22)},
    "Serge Gnabry":          {"nationality": "Germany",     "age_range": (28, 31)},
    "Thomas Muller":         {"nationality": "Germany",     "age_range": (34, 37)},
    "Paulo Dybala":          {"nationality": "Argentina",   "age_range": (30, 33)},
    "Kevin De Bruyne":       {"nationality": "Belgium",     "age_range": (32, 35)},
    "Romelu Lukaku":         {"nationality": "Belgium",     "age_range": (30, 33)},
    "Charles De Ketelaere":  {"nationality": "Belgium",     "age_range": (23, 25)},
    "Marcelo Brozovic":      {"nationality": "Croatia",     "age_range": (31, 34)},
    "Luka Modric":           {"nationality": "Croatia",     "age_range": (38, 41)},
    "Ilkay Gundogan":        {"nationality": "Germany",     "age_range": (33, 36)},
    "Antoine Griezmann":     {"nationality": "France",      "age_range": (32, 35)},
    "Marcus Thuram":         {"nationality": "France",      "age_range": (26, 29)},
    "Jules Kounde":          {"nationality": "France",      "age_range": (25, 28)},
    "Alisson Becker":        {"nationality": "Brazil",      "age_range": (31, 34)},
    "Ederson":               {"nationality": "Brazil",      "age_range": (30, 33)},
    "Marc-Andre ter Stegen": {"nationality": "Germany",     "age_range": (33, 36)},
    "Thibaut Courtois":      {"nationality": "Belgium",     "age_range": (31, 34)},
}


# ── Request helper ────────────────────────────────────────────────────────────
# Simple timestamp-based throttle: guarantees ≥0.6s between every request.

_last_request_time = 0.0


def stats_api_get(path: str, params: dict | None = None) -> dict:
    """GET to TheStatsAPI with minimum 0.6s gap and 429-retry logic."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 0.6:
        time.sleep(0.6 - elapsed)
    _last_request_time = time.time()

    url = f"{STATS_API_BASE}{path}"
    headers = {"Authorization": f"Bearer {STATS_API_KEY}"}
    for attempt in range(3):
        resp = requests.get(url, headers=headers, params=params or {}, timeout=20)
        if resp.status_code == 429:
            if attempt < 2:
                print(f"  [WARN] 429 received, waiting 10s... (attempt {attempt + 1}/3)")
                time.sleep(10)
                continue
            resp.raise_for_status()
        resp.raise_for_status()
        return resp.json()
    return {}


def paginate_all(path: str, params: dict | None = None) -> list:
    """Fetch all pages for a paginated endpoint."""
    all_results = []
    page = 1
    while True:
        p = {**(params or {}), "page": page}
        data = stats_api_get(path, p)
        results = data.get("data", [])
        all_results.extend(results)
        meta = data.get("meta", {})
        total_pages = meta.get("total_pages", 1)
        if page >= total_pages:
            break
        page += 1
    return all_results


# ── Phase 1: Build team ID map ─────────────────────────────────────────────────

def build_team_id_map(dry_run: bool = False) -> dict:
    """Search for each WC team by name and return name→ID mapping."""
    if TEAM_ID_MAP_PATH.exists():
        existing = json.loads(TEAM_ID_MAP_PATH.read_text(encoding="utf-8"))
        print(f"[INFO] Loaded existing team_id_map with {len(existing)} entries.")
        return existing

    print(f"\n[PHASE 0] Building team ID map for {len(WC_2026_TEAMS)} teams...")
    if dry_run:
        print("[DRY RUN] Would search for team IDs via GET /football/teams?search=<name>")
        return {}

    team_map = {}
    for team_name in tqdm(WC_2026_TEAMS, desc="Team ID lookup"):
        try:
            # Try alternate search term first for known problem names
            search_names = ["USA", "United States"] if team_name == "United States" else [team_name]
            teams = []
            for search_name in search_names:
                results = stats_api_get("/football/teams", {"search": search_name})
                teams = results.get("data", [])
                if teams:
                    break
            if teams:
                team_map[team_name] = teams[0].get("id") or teams[0].get("team_id")
            else:
                print(f"  [WARN] No result for: {team_name}")
        except requests.RequestException as e:
            print(f"  [ERROR] {team_name}: {e}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    TEAM_ID_MAP_PATH.write_text(json.dumps(team_map, indent=2), encoding="utf-8")
    print(f"[OK] team_id_map.json saved ({len(team_map)} teams mapped)")
    return team_map


# ── Phase 2: Pull team match histories ────────────────────────────────────────

def pull_team_matches(team_map: dict, resume: bool = False, dry_run: bool = False) -> None:
    today = datetime.now(timezone.utc).date()
    from_date = (today - timedelta(days=365)).isoformat()
    to_date = today.isoformat()

    print(f"\n[PHASE 1] Pulling match history for {len(team_map)} teams ({from_date} to {to_date})...")

    if dry_run:
        total_est = len(team_map) * 30  # ~30 matches per team on average
        print(f"[DRY RUN] Would fetch ~{total_est} matches via GET /football/matches?team_id=<id>&from=&to=")
        print(f"  Estimated API calls: {len(team_map)} team queries + pagination")
        return

    RAW_MATCHES_DIR.mkdir(parents=True, exist_ok=True)
    match_ids_seen: set[str] = set()

    for team_name, team_id in tqdm(team_map.items(), desc="Team match histories"):
        if not team_id:
            continue
        try:
            matches = paginate_all(
                "/football/matches",
                {"team_id": team_id, "from": from_date, "to": to_date},
            )
            for match in matches:
                match_id = str(match.get("id") or match.get("match_id", ""))
                if not match_id:
                    continue
                if match_id in match_ids_seen:
                    continue
                match_ids_seen.add(match_id)
                out_path = RAW_MATCHES_DIR / f"{match_id}.json"
                if resume and out_path.exists():
                    continue
                out_path.write_text(json.dumps(match, indent=2), encoding="utf-8")
        except requests.RequestException as e:
            print(f"  [ERROR] Matches for {team_name}: {e}")

    print(f"[OK] Match history done. {len(list(RAW_MATCHES_DIR.glob('*.json')))} match files saved.")


# ── Phase 3: Pull xG for each match ──────────────────────────────────────────

def pull_xg_data(resume: bool = False, dry_run: bool = False) -> None:
    match_files = list(RAW_MATCHES_DIR.glob("*.json"))
    print(f"\n[PHASE 2] Checking xG availability for {len(match_files)} matches...")

    eligible = []
    for mf in match_files:
        try:
            match = json.loads(mf.read_text(encoding="utf-8"))
            if match.get("xg_available"):
                match_id = str(match.get("id") or match.get("match_id", ""))
                eligible.append(match_id)
        except (json.JSONDecodeError, OSError):
            pass

    print(f"  {len(eligible)} matches have xG available.")

    if dry_run:
        print(f"[DRY RUN] Would fetch xG stats for {len(eligible)} matches via GET /football/matches/<id>/stats")
        return

    RAW_XG_DIR.mkdir(parents=True, exist_ok=True)
    for match_id in tqdm(eligible, desc="xG data"):
        out_path = RAW_XG_DIR / f"{match_id}.json"
        if resume and out_path.exists():
            continue
        try:
            data = stats_api_get(f"/football/matches/{match_id}/stats")
            out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except requests.RequestException as e:
            print(f"  [ERROR] xG for match {match_id}: {e}")

    print(f"[OK] xG data done. {len(list(RAW_XG_DIR.glob('*.json')))} xG files saved.")


# ── Phase 4: Pull player stats ────────────────────────────────────────────────

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def pull_player_stats(resume: bool = False, dry_run: bool = False) -> None:
    print(f"\n[PHASE 3] Pulling player stats for {len(PLAYER_METADATA)} key players...")

    if dry_run:
        print(f"[DRY RUN] Would search player IDs then fetch stats for {len(PLAYER_METADATA)} players")
        print("  First: GET /football/players?search=<accent-stripped name>")
        print("  Then:  validate nationality + age, then GET /football/players/stats?player_id=<id>&season=2025")
        return

    RAW_PLAYERS_DIR.mkdir(parents=True, exist_ok=True)

    for player_name, meta in tqdm(PLAYER_METADATA.items(), desc="Player stats"):
        expected_nationality = meta["nationality"]
        age_lo, age_hi = meta["age_range"]

        try:
            search_result = stats_api_get("/football/players", {"search": _strip_accents(player_name)})
            players = search_result.get("data", [])
            if not players:
                print(f"  [WARN] No results for: {player_name}")
                continue

            # Log raw first result so we can verify exact field names from this API
            print(f"  [DEBUG] {player_name} → first result: {json.dumps(players[0], ensure_ascii=False)}")

            # Scan ALL results for the one matching nationality + age
            matched = None
            for candidate in players:
                nat = candidate.get("nationality", "")
                age = candidate.get("age")
                if nat == expected_nationality and age is not None and age_lo <= int(age) <= age_hi:
                    matched = candidate
                    break

            if matched is None:
                print(
                    f"  [WARN] No match for {player_name} "
                    f"(want nationality={expected_nationality!r}, age {age_lo}–{age_hi}) "
                    f"across {len(players)} result(s)"
                )
                continue

            player_id = matched.get("id") or matched.get("player_id")
            if not player_id:
                print(f"  [WARN] No ID field in matched result for: {player_name}")
                continue

            out_path = RAW_PLAYERS_DIR / f"{player_id}.json"
            if resume and out_path.exists():
                continue

            # Fetch 2025 season stats
            stats_data = stats_api_get(
                "/football/players/stats",
                {"player_id": player_id, "season": 2025},
            )
            out_data = {"name": player_name, "player_id": player_id, "stats": stats_data}
            out_path.write_text(json.dumps(out_data, indent=2), encoding="utf-8")

        except requests.RequestException as e:
            print(f"  [ERROR] {player_name}: {e}")

    print(f"[OK] Player stats done. {len(list(RAW_PLAYERS_DIR.glob('*.json')))} player files saved.")


# ── Phase 5: Historical WC data ───────────────────────────────────────────────

def pull_historical_wc(resume: bool = False, dry_run: bool = False) -> None:
    print("\n[PHASE 4] Pulling 2018 and 2022 World Cup historical data...")

    if dry_run:
        print("[DRY RUN] Steps:")
        print("  1. GET /football/competitions?search=world+cup to find competition IDs")
        print("  2. GET /football/matches?competition_id=<id>&season=2022 for WC matches")
        print("  3. GET /football/matches/<id>/stats for xG on each match")
        return

    RAW_HISTORICAL_DIR.mkdir(parents=True, exist_ok=True)

    # Find World Cup competition IDs
    try:
        comps_result = stats_api_get("/football/competitions", {"search": "world cup"})
        comps = comps_result.get("data", [])
        wc_ids = {}
        for comp in comps:
            name = comp.get("name", "").lower()
            season = str(comp.get("season", ""))
            if "world cup" in name and season in ("2018", "2022", "2026"):
                wc_ids[season] = comp.get("id") or comp.get("competition_id")
        print(f"  Found WC competition IDs: {wc_ids}")
    except requests.RequestException as e:
        print(f"  [ERROR] Competition search failed: {e}")
        return

    for season, comp_id in wc_ids.items():
        if not comp_id or season == "2026":
            continue
        try:
            matches = paginate_all("/football/matches", {"competition_id": comp_id, "season": season})
            print(f"  Found {len(matches)} matches for WC {season}")
            for match in tqdm(matches, desc=f"WC {season} matches"):
                match_id = str(match.get("id") or match.get("match_id", ""))
                if not match_id:
                    continue
                match_path = RAW_HISTORICAL_DIR / f"{season}_{match_id}.json"
                if not (resume and match_path.exists()):
                    match_path.write_text(json.dumps(match, indent=2), encoding="utf-8")

                if match.get("xg_available"):
                    xg_path = RAW_HISTORICAL_DIR / f"{season}_{match_id}_xg.json"
                    if not (resume and xg_path.exists()):
                        try:
                            xg_data = stats_api_get(f"/football/matches/{match_id}/stats")
                            xg_path.write_text(json.dumps(xg_data, indent=2), encoding="utf-8")
                        except requests.RequestException:
                            pass
        except requests.RequestException as e:
            print(f"  [ERROR] WC {season} pull failed: {e}")

    print(f"[OK] Historical data done. {len(list(RAW_HISTORICAL_DIR.glob('*.json')))} files saved.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="WC2026 Bulk Data Collector (TheStatsAPI)")
    parser.add_argument("--teams-only", action="store_true", help="Only pull team match history")
    parser.add_argument("--players", action="store_true", help="Also pull player stats")
    parser.add_argument("--historical", action="store_true", help="Also pull 2018/2022 WC historical data")
    parser.add_argument("--resume", action="store_true", help="Skip already-cached files")
    parser.add_argument("--dry-run", action="store_true", help="Print fetch plan without calling API")
    args = parser.parse_args()

    if not STATS_API_KEY and not args.dry_run:
        print("[ERROR] STATS_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    run_all = not args.teams_only and not args.players and not args.historical
    run_teams = run_all or args.teams_only
    run_players = run_all or args.players
    run_historical = run_all or args.historical

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN — Fetch Plan")
        print("=" * 60)
        print(f"Teams: {len(WC_2026_TEAMS)}")
        print(f"Key players: {len(PLAYER_METADATA)}")
        print(f"Phases to run: teams={run_teams}, players={run_players}, historical={run_historical}")
        print()

    # Always build team map first (needed for match pulls)
    team_map = build_team_id_map(dry_run=args.dry_run)

    if run_teams:
        pull_team_matches(team_map, resume=args.resume, dry_run=args.dry_run)
        if not args.dry_run:
            pull_xg_data(resume=args.resume, dry_run=args.dry_run)

    if run_players:
        pull_player_stats(resume=args.resume, dry_run=args.dry_run)

    if run_historical:
        pull_historical_wc(resume=args.resume, dry_run=args.dry_run)

    if args.dry_run:
        print("\n[DRY RUN COMPLETE] No API calls made.")
    else:
        print("\n[DONE] Data collection complete.")
        print(f"  Matches: {len(list(RAW_MATCHES_DIR.glob('*.json')))}")
        print(f"  xG:      {len(list(RAW_XG_DIR.glob('*.json')))}")
        print(f"  Players: {len(list(RAW_PLAYERS_DIR.glob('*.json')))}")
        print(f"  History: {len(list(RAW_HISTORICAL_DIR.glob('*.json')))}")


if __name__ == "__main__":
    main()
