"""
morning_report.py — Daily betting intelligence report generator.

Usage:
    python agent/morning_report.py                # generate report, save to reports/, no email
    python agent/morning_report.py --no-push      # generate, skip git commit/push
    python agent/morning_report.py --dry-run      # print prompt, no Claude call
    python agent/morning_report.py --send-email   # send today's saved report (review first!)
    python agent/morning_report.py --send-email --send-date 2026-06-14  # send a past report
    python agent/morning_report.py --no-email     # (accepted but ignored; email never auto-sends)
    python agent/morning_report.py --web-prompt   # build prompt file for Claude web (no API tokens)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = ROOT / "agent" / "system_prompt.md"
ODDS_CACHE_PATH = ROOT / "data" / "odds_cache.json"
BETS_PATH = ROOT / "data" / "bets.json"
SUBSCRIBERS_PATH = ROOT / "data" / "subscribers.json"
REPORTS_DIR = ROOT / "reports"

# ── Config ────────────────────────────────────────────────────────────────────
ODDS_API_KEY = os.getenv("THE_ODDS_API_KEY", "")
API_SPORTS_KEY = os.getenv("API_SPORTS_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
GMAIL_FROM = os.getenv("RESEND_TO_EMAIL", "")  # levijbdavis@gmail.com — reuses existing env var

MODEL = "claude-sonnet-4-6"
ET_OFFSET = timedelta(hours=-4)  # EDT (UTC-4)
OPENFOOTBALL_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
# Set this to wherever the dashboard is actually served. A local file path
# (dashboard/index.html) is NOT clickable in email — use a hosted URL.
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://levijb.github.io/WorldCup2026/dashboard/tournament.html")


def now_et() -> datetime:
    return datetime.now(timezone.utc).astimezone(timezone(ET_OFFSET))


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def today_date_str() -> str:
    return now_et().strftime("%Y-%m-%d")


def implied_prob(american_odds: int) -> float:
    """Convert American odds integer to implied probability (0.0–1.0)."""
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return (-american_odds) / (-american_odds + 100)


# ── Data Fetchers ─────────────────────────────────────────────────────────────

def fetch_odds() -> dict:
    """Fetch live DraftKings odds for WC 2026 from The Odds API."""
    try:
        url = "https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": "us",
            "markets": "h2h,totals,spreads",
            "oddsFormat": "american",
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        quota_remaining = resp.headers.get("x-requests-remaining", "unknown")
        quota_used = resp.headers.get("x-requests-used", "unknown")
        return {
            "data": resp.json(),
            "quota_remaining": quota_remaining,
            "quota_used": quota_used,
            "fetched_at": now_utc().isoformat(),
        }
    except requests.RequestException as e:
        print(f"[WARN] Odds API fetch failed: {e}", file=sys.stderr)
        return {"data": [], "quota_remaining": "unknown", "quota_used": "unknown", "fetched_at": now_utc().isoformat(), "error": str(e)}


def fetch_fixtures_today() -> list:
    """Derive today's WC fixtures from the odds cache.
    API-Sports free tier doesn't cover 2026 season data, so we use
    the already-fetched Odds API cache which has home_team, away_team,
    and commence_time for every match."""
    try:
        cache = json.loads(ODDS_CACHE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    today_et = now_et().date()
    fixtures = []
    for match in cache.get("matches", []):
        try:
            commence = match["commence_time"]
            kickoff_dt = datetime.fromisoformat(commence.replace("Z", "+00:00"))
            kickoff_et = kickoff_dt.astimezone(timezone(ET_OFFSET))
            is_today = kickoff_et.date() == today_et
            is_late_night = (
                kickoff_et.date() == today_et + timedelta(days=1)
                and kickoff_et.hour < 3
            )
            if not is_today and not is_late_night:
                continue
            fixtures.append({
                "teams": {
                    "home": {"name": match["home_team"]},
                    "away": {"name": match["away_team"]},
                },
                "fixture": {"date": commence},
            })
        except (KeyError, ValueError):
            continue
    return fixtures


def fetch_fixtures_tomorrow() -> list:
    """Fetch tomorrow's WC fixtures. Tries odds cache first, falls back to openfootball.

    The odds cache only pulls matches within a 3-day lookahead window and can lag or
    miss games when run at odd hours — if it has nothing for tomorrow, openfootball
    (the same feed the dashboard uses) gives Claude real venue/group data instead of
    letting it guess from web search.
    """
    tomorrow_et = now_et().date() + timedelta(days=1)

    # --- primary: odds cache ---
    try:
        cache = json.loads(ODDS_CACHE_PATH.read_text(encoding="utf-8"))
        fixtures = []
        for match in cache.get("matches", []):
            try:
                commence = match["commence_time"]
                kickoff_dt = datetime.fromisoformat(commence.replace("Z", "+00:00"))
                if kickoff_dt.astimezone(timezone(ET_OFFSET)).date() != tomorrow_et:
                    continue
                fixtures.append({
                    "home_team": match["home_team"],
                    "away_team": match["away_team"],
                    "commence_time": commence,
                })
            except (KeyError, ValueError):
                continue
        if fixtures:
            print(f"[FIXTURES] Tomorrow: {len(fixtures)} from odds cache")
            return fixtures[:8]
    except (json.JSONDecodeError, OSError):
        pass

    # --- fallback: openfootball ---
    print("[FIXTURES] Odds cache empty for tomorrow — falling back to openfootball")
    try:
        resp = requests.get(OPENFOOTBALL_URL, timeout=10)
        resp.raise_for_status()
        wc = resp.json()
        fixtures = []
        for m in wc.get("matches", []):
            try:
                match_date = m.get("date")
                if not match_date or datetime.strptime(match_date, "%Y-%m-%d").date() != tomorrow_et:
                    continue
                # Convert openfootball's "HH:MM UTC±N" venue-local time to a UTC commence_time string
                time_match = re.match(r"(\d{1,2}):(\d{2})\s*UTC([+-]\d+)", m.get("time", ""))
                if time_match:
                    hh, mm, offset = int(time_match.group(1)), int(time_match.group(2)), int(time_match.group(3))
                    utc_dt = datetime(tomorrow_et.year, tomorrow_et.month, tomorrow_et.day,
                                       hh - offset, mm, tzinfo=timezone.utc)
                    commence = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    commence = f"{match_date}T00:00:00Z"
                fixtures.append({
                    "home_team": m.get("team1", "TBD"),
                    "away_team": m.get("team2", "TBD"),
                    "commence_time": commence,
                    "ground": m.get("ground", ""),
                    "group": m.get("group", ""),
                })
            except (KeyError, ValueError):
                continue
        print(f"[FIXTURES] Tomorrow: {len(fixtures)} from openfootball fallback")
        return fixtures[:8]
    except Exception as e:
        print(f"[WARN] openfootball fallback failed: {e}")
        return []


def fetch_recent_results_via_search(client) -> str:
    """Search for recent WC 2026 match results via web search."""
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=600,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": (
                    "Search for World Cup 2026 match results from the last 2 days. "
                    "Return completed match results as bullet points, each prefixed with the match date. "
                    "Format: 'YYYY-MM-DD: Team A score-score Team B (Group X)'. "
                    "Separate yesterday's matches from the day before — label each day clearly. No commentary."
                ),
            }],
        )
        text_parts = [b.text for b in resp.content if hasattr(b, "text")]
        return "\n".join(text_parts) if text_parts else "  No recent results found."
    except Exception as e:
        print(f"[WARN] Recent results search failed: {e}", file=sys.stderr)
        return f"  (recent results unavailable: {e})"


def fetch_injuries() -> list:
    """Fetch live injury list for WC 2026."""
    try:
        url = "https://v3.football.api-sports.io/injuries"
        headers = {"x-apisports-key": API_SPORTS_KEY}
        params = {"league": 1, "season": 2026}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("response", [])
    except requests.RequestException as e:
        print(f"[WARN] API-Sports injuries fetch failed: {e}", file=sys.stderr)
        return []


def fetch_news_via_claude(client, today_str: str) -> str:
    """Search for match-relevant WC news: injuries, lineups, suspensions."""
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": (
                    f"Search for: '{today_str} World Cup 2026 news injuries lineup team form'. "
                    "Return a concise bullet-point summary focused on match-relevant news: "
                    "injuries, suspensions, confirmed lineups, and form heading into today's matches."
                ),
            }],
        )
        text_parts = [b.text for b in resp.content if hasattr(b, "text")]
        return "\n".join(text_parts) if text_parts else "(no news retrieved)"
    except Exception as e:
        print(f"[WARN] News search failed: {e}", file=sys.stderr)
        return f"(news search unavailable: {e})"


def fetch_atmosphere_via_claude(client, today_str: str) -> str:
    """Search for WC color stories, atmosphere, and tournament narrative beyond match results."""
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=800,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": (
                    f"Search for: 'World Cup 2026 stories atmosphere fans goals moments {today_str}'. "
                    "Return 3-5 bullet points covering: crowd atmosphere, VAR controversies, "
                    "surprising performances, player milestones, human interest angles, "
                    "memorable goals, coach quotes, venue conditions. "
                    "No match result summaries — only color and narrative."
                ),
            }],
        )
        text_parts = [b.text for b in resp.content if hasattr(b, "text")]
        return "\n".join(text_parts) if text_parts else "(no atmosphere stories retrieved)"
    except Exception as e:
        print(f"[WARN] Atmosphere search failed: {e}", file=sys.stderr)
        return f"(atmosphere search unavailable: {e})"


# ── Odds Cache ─────────────────────────────────────────────────────────────────

def load_odds_cache() -> dict:
    if ODDS_CACHE_PATH.exists():
        try:
            return json.loads(ODDS_CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_updated": None, "matches": []}


def save_odds_cache(odds_data: list) -> None:
    cache = {
        "last_updated": now_utc().isoformat(),
        "matches": odds_data,
    }
    ODDS_CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def compute_line_movements(current_odds: list, previous_cache: dict) -> str:
    """Compare current odds to yesterday's cache and describe notable movements."""
    prev_matches = {m.get("id"): m for m in previous_cache.get("matches", [])}
    movements = []
    for match in current_odds:
        match_id = match.get("id")
        home = match.get("home_team", "")
        away = match.get("away_team", "")
        prev = prev_matches.get(match_id)
        if not prev:
            continue
        for bm in match.get("bookmakers", []):
            if bm.get("key") != "draftkings":
                continue
            for mkt in bm.get("markets", []):
                if mkt.get("key") != "h2h":
                    continue
                cur_outcomes = {o["name"]: o["price"] for o in mkt.get("outcomes", [])}
                prev_bm = next((b for b in prev.get("bookmakers", []) if b.get("key") == "draftkings"), None)
                if not prev_bm:
                    continue
                prev_mkt = next((m for m in prev_bm.get("markets", []) if m.get("key") == "h2h"), None)
                if not prev_mkt:
                    continue
                prev_outcomes = {o["name"]: o["price"] for o in prev_mkt.get("outcomes", [])}
                for team, cur_price in cur_outcomes.items():
                    prev_price = prev_outcomes.get(team)
                    if prev_price is None:
                        continue
                    movement = cur_price - prev_price
                    if abs(movement) >= 15:
                        direction = "shortened" if movement < 0 else "drifted"
                        movements.append(
                            f"  • {home} vs {away}: {team} {direction} from {prev_price:+d} to {cur_price:+d} ({movement:+d})"
                        )
    if not movements:
        return "  No significant line movements vs yesterday's cache."
    return "\n".join(movements)


# ── Prompt Builder ─────────────────────────────────────────────────────────────

def build_static_context() -> str:
    """Static context block: never changes run to run (good candidate for caching)."""
    return """## STATIC CONTEXT (Pre-tournament baselines — loaded from system)

The Opta model win probabilities, pre-tournament odds snapshot, and key intelligence items
are detailed in the system prompt. Reference them for all baseline assessments.

Key sharp-money pre-tournament read:
- Spain and France: smart money handle far exceeds ticket share at current prices
- USA: massive public interest in home WC; expect significant overpricing throughout
- Brazil and Argentina: fade at current prices given underlying form
- Norway/Colombia/Japan/Morocco: value relative to Opta probabilities"""


def _fmt_kickoff_multi_tz(kickoff_dt: datetime) -> str:
    """Format a kickoff datetime across ET/CT/PT/BST for display."""
    def _t(hours_offset: int, label: str) -> str:
        t = kickoff_dt.astimezone(timezone(timedelta(hours=hours_offset)))
        return t.strftime("%I:%M %p").lstrip("0") + f" {label}"
    return f"{_t(-4, 'ET')} | {_t(-5, 'CT')} | {_t(-7, 'PT')} | {_t(1, 'BST')}"


def format_today_fixtures(fixtures: list) -> str:
    """Format today's fixtures with multi-timezone kickoff times."""
    fixture_lines = []
    for f in fixtures:
        try:
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            kickoff_utc = f["fixture"]["date"]
            kickoff_dt = datetime.fromisoformat(kickoff_utc.replace("Z", "+00:00"))
            times = _fmt_kickoff_multi_tz(kickoff_dt)
            venue = f["fixture"].get("venue", {}).get("name", "TBD")
            city = f["fixture"].get("venue", {}).get("city", "")
            fixture_lines.append(f"  • {home} vs {away} | {times} | {venue}, {city}")
        except (KeyError, ValueError):
            fixture_lines.append(f"  • {f}")
    return "\n".join(fixture_lines) if fixture_lines else "  No fixtures found for today."


def format_tomorrow_fixtures(fixtures_tomorrow: list) -> str:
    """Format tomorrow's slate as one line per match."""
    tomorrow_lines = []
    for f in fixtures_tomorrow:
        try:
            kickoff_dt = datetime.fromisoformat(f["commence_time"].replace("Z", "+00:00"))
            kickoff_et = kickoff_dt.astimezone(timezone(ET_OFFSET))
            time_str = kickoff_et.strftime("%I:%M %p").lstrip("0") + " ET"
        except (KeyError, ValueError):
            time_str = "TBD"
        ground = f.get("ground", "")
        group = f.get("group", "")
        suffix = ""
        if ground or group:
            parts = [p for p in (ground, group) if p]
            suffix = f" ({', '.join(parts)})"
        tomorrow_lines.append(f"  {time_str} — {f['home_team']} vs {f['away_team']}{suffix}")
    return "\n".join(tomorrow_lines) if tomorrow_lines else "  No matches scheduled for tomorrow."


def format_injuries_block(injuries: list) -> str:
    """Format the injury list, capped for prompt length."""
    inj_lines = []
    for inj in injuries[:30]:  # cap at 30 entries for prompt length
        try:
            player = inj["player"]["name"]
            team = inj["team"]["name"]
            reason = inj.get("injury", {}).get("reason", "unknown")
            inj_lines.append(f"  • {player} ({team}): {reason}")
        except (KeyError, TypeError):
            pass
    return "\n".join(inj_lines) if inj_lines else "  No injury data available."


def build_dynamic_content(
    today_str: str,
    fixtures: list,
    fixtures_tomorrow: list,
    recent_results: str,
    odds_result: dict,
    injuries: list,
    news: str,
    around_the_tournament: str,
    line_movements: str,
) -> str:
    """Dynamic content block: today's data — never cache this."""
    et_now = now_et().strftime("%Y-%m-%d %H:%M ET")

    fixtures_text = format_today_fixtures(fixtures)
    results_text = recent_results if recent_results else "  No recent results."

    # Format DraftKings odds with implied probabilities
    odds_lines = []
    for match in odds_result.get("data", []):
        home = match.get("home_team", "")
        away = match.get("away_team", "")
        for bm in match.get("bookmakers", []):
            if bm.get("key") != "draftkings":
                continue
            markets_text = []
            for mkt in bm.get("markets", []):
                key = mkt.get("key")
                outcomes = mkt.get("outcomes", [])
                if key == "h2h":
                    parts = []
                    for o in outcomes:
                        price = o["price"]
                        imp = implied_prob(int(price))
                        parts.append(f"{o['name']} {price:+d} ({imp:.1%})")
                    markets_text.append(f"H2H: {' | '.join(parts)}")
                elif key == "totals":
                    for o in outcomes:
                        imp = implied_prob(int(o["price"]))
                        markets_text.append(f"Total {o.get('point', '')} {o['name']} {o['price']:+d} ({imp:.1%})")
            if markets_text:
                odds_lines.append(f"  {home} vs {away}:\n    " + "\n    ".join(markets_text))
    odds_text = "\n".join(odds_lines) if odds_lines else "  No DraftKings odds available."

    injuries_text = format_injuries_block(injuries)
    tomorrow_text = format_tomorrow_fixtures(fixtures_tomorrow)

    return f"""## LIVE DATA — {et_now}

### Today's Fixtures ({today_str})
{fixtures_text}

### Results (Last 2 Days — dated)
{results_text}

### Tomorrow's Fixtures
{tomorrow_text}

### Current DraftKings Odds
{odds_text}

Odds quota remaining: {odds_result.get('quota_remaining', 'unknown')}

### Line Movements vs Yesterday
{line_movements}

### Injury Report
{injuries_text}

### Today's News & Intelligence
{news}

### Around the Tournament (Color & Stories)
{around_the_tournament}

---

## REQUEST

Produce the full morning briefing report in this exact order:

1. **TOURNAMENT STATUS** — Current day/round, matches played, standings snapshot if relevant. 3–5 lines max.

2. **RESULTS** — Completed matches from the last two days. You MUST split them into two dated subsections and never combine them under one header:
   - **Yesterday — [Weekday, Month D]** — matches played the day before today
   - **Two Days Ago — [Weekday, Month D]** — matches played two days before today
   - One bullet per match, formatted: `- Team A X–Y Team B (Group Z) — [note]`. Em-dash (—) before the note, never a colon. En-dash (–) between the goals in the score, never a hyphen. The note should have personality and editorial voice — write it like a knowledgeable fan recapping the match, not a wire-service summary. 1-2 sentences.
   - Assign each match using the date in the provided results data. Do NOT output a single "YESTERDAY'S RESULTS" heading containing both days.
   - If a subsection has no matches, write "No matches." under it. If nothing has been played at all: "No matches played yet."

3. **TODAY'S MATCHES** — Each match gets a bold header line immediately above its paragraph (no blank line between header and paragraph), formatted exactly: `**Team A vs. Team B — H:MM PM ET | Stadium Name, City | Group X**` (use "vs." with a period, ET 12-hour time with AM/PM, stadium comma city, pipe separators). Then one paragraph per match (4–5 sentences): kickoff time ET, venue, tactical setup, key injuries, one betting angle sentence. Today's matches only.

4. **NEWS & INJURIES** — 3–5 bullets, one line each. Only items relevant to today's matches.

5. **BET RECOMMENDATIONS** — 3–5 bets using the exact structured format from the system prompt. Do not include a MODEL EDGE line or any model/edge-percentage field — the allowed fields are BET, ODDS, EDGE REASONING, RISK LEVEL, RECOMMENDED STAKE, KEY RISK FACTORS only. Evaluate ALL matches in the Today's Fixtures list above for bet angles — including any late-night (midnight–3 AM ET) kickoffs. Do not skip or dismiss any match without specific analysis.

6. **AROUND THE TOURNAMENT** — 3–5 bullets on general WC atmosphere, color stories, and tournament narrative beyond today's matches. Each bullet 1–3 sentences — enough to deliver the observation properly; this is the section with the most license for dry wit. No odds, no bet angles.

7. **PARLAYS** — 3–4 parlays, max 3 legs per parlay. Legs on separate matches or clearly correlated. Format each exactly: `**Parlay N: [Name] — [legs summary]**` on its own line, then `Estimated combined odds: approximately +XXX. [1-2 sentences of rationale.]`, then `**RECOMMENDED STAKE:** $X (X units)`.

8. **SHARP MONEY** — 3 bullets max, or "Nothing notable."

9. **TOMORROW'S SLATE** — Use the fixture data provided above. One markdown bullet per match, each on its own line:
   "- HH:MM ET — Home vs Away"
   No analysis, no odds. Do not combine matches onto a single line.

Use specific American odds numbers. If no strong plays exist, say so explicitly.
"""


# ── WC Odds Caching ───────────────────────────────────────────────────────────

def cache_upcoming_wc_odds() -> None:
    """Cache Pinnacle pre-match odds for WC matches in the next 3 days.

    Requires STATS_API_KEY. Silently skips if the key is absent or if the
    import fails. Never raises — a caching failure must not block the report.
    """
    if not os.getenv("STATS_API_KEY", ""):
        return
    try:
        import sys as _sys
        _sys.path.insert(0, str(ROOT / "model"))
        from data_collector import pull_wc_prematch_odds  # noqa: PLC0415
        result = pull_wc_prematch_odds(resume=True, lookahead_days=3)
        if result.get("saved"):
            print(f"[ODDS CACHE] Saved {result['saved']} Pinnacle odds file(s) for upcoming WC matches")
    except Exception as e:
        print(f"[WARN] WC odds caching skipped: {e}", file=sys.stderr)


# ── Claude API ─────────────────────────────────────────────────────────────────

def call_claude(system_prompt: str, static_context: str, dynamic_content: str) -> str:
    """Call Claude with prompt caching on system prompt and static context."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": static_context,
                            "cache_control": {"type": "ephemeral"},
                        },
                        {
                            "type": "text",
                            "text": dynamic_content,
                        },
                    ],
                }
            ],
        )
        return response.content[0].text
    except Exception as e:
        print(f"[ERROR] Claude API call failed: {e}", file=sys.stderr)
        raise


# ── Report Saving ─────────────────────────────────────────────────────────────

def save_report(report_text: str, today_str: str, quota_remaining: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{today_str}_morning_report.md"
    report_date = datetime.strptime(today_str, "%Y-%m-%d")
    date_str = f"{report_date.strftime('%A %B')} {report_date.day}, {report_date.year}"
    header = (
        f"# World Cup Morning Report \n"
        f"{date_str}\n\n"
        f"[Live dashboard link →]({DASHBOARD_URL})\n\n"
        f"---\n\n"
    )
    report_path.write_text(header + report_text, encoding="utf-8")
    print(f"[OK] Report saved to {report_path}")
    return report_path


def _fmt_human_date(dt: datetime) -> str:
    """Format a date as 'Weekday, Month D' (no leading zero on the day)."""
    return dt.strftime("%A, %B %d").replace(" 0", " ")


def split_results_by_date(combined: str, yesterday_iso: str, two_days_ago_iso: str) -> tuple:
    """Split a combined 'YYYY-MM-DD: ...' results blob into two date buckets."""
    if not combined or combined.strip().startswith(
        ("(recent results unavailable", "(Claude web will search")
    ):
        placeholder = "(Claude web will search for this — see search instructions above)"
        return placeholder, placeholder

    yesterday_lines, two_days_lines = [], []
    for line in combined.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(yesterday_iso):
            yesterday_lines.append(stripped)
        elif stripped.startswith(two_days_ago_iso):
            two_days_lines.append(stripped)
        else:
            # Unlabeled line — default to the more recent bucket
            yesterday_lines.append(stripped)

    yesterday_text = "\n".join(f"  {l}" for l in yesterday_lines) if yesterday_lines else "  No matches."
    two_days_text = "\n".join(f"  {l}" for l in two_days_lines) if two_days_lines else "  No matches."
    return yesterday_text, two_days_text


def format_odds_block_v2(odds_result: dict) -> str:
    """Format DraftKings odds as one HOME/AWAY/Draw/O-U line per match."""
    lines = []
    for match in odds_result.get("data", []):
        home = match.get("home_team", "")
        away = match.get("away_team", "")
        home_odds = away_odds = draw_odds = ou_text = None
        for bm in match.get("bookmakers", []):
            if bm.get("key") != "draftkings":
                continue
            for mkt in bm.get("markets", []):
                key = mkt.get("key")
                outcomes = mkt.get("outcomes", [])
                if key == "h2h":
                    for o in outcomes:
                        name = o.get("name", "")
                        if name == home:
                            home_odds = o.get("price")
                        elif name == away:
                            away_odds = o.get("price")
                        elif name.lower() == "draw":
                            draw_odds = o.get("price")
                elif key == "totals" and outcomes:
                    o = outcomes[0]
                    ou_text = f"{o.get('point', '')} {o.get('name', '')} {o.get('price', 0):+d}"
        if home_odds is None and away_odds is None:
            continue
        parts = [
            f"HOME {home_odds:+d}" if home_odds is not None else "HOME n/a",
            f"AWAY {away_odds:+d}" if away_odds is not None else "AWAY n/a",
        ]
        if draw_odds is not None:
            parts.append(f"Draw {draw_odds:+d}")
        if ou_text:
            parts.append(f"O/U {ou_text}")
        lines.append(f"  {home} vs {away}: " + " | ".join(parts))
    return "\n".join(lines) if lines else "  (No DraftKings odds available — use web search for current lines)"


WEB_PROMPT_TEMPLATE = """# WC2026 Morning Report Prompt — {report_date}
# Paste this entire file into a Claude web chat (claude.ai).
# Claude will run web searches inline and write the full report.
# After Claude responds, copy the report text into:
#   reports/{report_date}_morning_report.md
# Then send with: python agent/morning_report.py --send-email
#
# ─────────────────────────────────────────────────────────────────────────────

## INSTRUCTIONS FOR CLAUDE WEB

You are generating the World Cup 2026 morning briefing report using the v2 format below.
Before writing anything, run these two web searches and incorporate the results.

**Search 1 — News and injuries:**
Search for: "World Cup 2026 injuries lineup news {search_date} {today_teams}"
Return 4–6 bullet points: confirmed injuries, suspensions, expected lineups, fitness concerns.
Only items relevant to today's matches. Distinguish confirmed from unconfirmed.

**Search 2 — Around the tournament:**
Search for: "World Cup 2026 stories atmosphere moments {search_date}"
Return 4–5 bullet points: crowd moments, VAR controversies, player milestones, coach quotes,
fan stories, venue conditions, tournament narrative threads.
No match result summaries — color and narrative only.

Scores for yesterday and two days ago are pre-filled in the LIVE DATA section below. Do NOT search for scores. Use those confirmed figures and write editorial notes for each.

---

## SYSTEM PROMPT (v2)

{system_prompt}

---

## OUTPUT FORMAT — follow this section order exactly

### SECTION 1 — HEADER BLOCK

**Line 1:** 2–3 short punchy phrases — the biggest things happening today. Facts, not hype.
Example: "Day 14. Matchday 3 begins. Six matches, all simultaneous within slots."

**Line 2:** `[Live dashboard →](https://levijb.github.io/WorldCup2026/dashboard/tournament.html)`

**Line 3 — TABLE OF CONTENTS** (two-level markdown anchor links):
Generate the TOC dynamically based on today's fixtures. Top level = major sections.
Sub-level = one entry per match under Today's Matches and Predictions.
Format each match sub-entry as: `  - [Team A vs. Team B — H:MM PM ET](#team-a-vs-team-b)`
Anchor IDs: lowercase, spaces to hyphens, strip special characters, strip periods.

---

### SECTION 2 — TOURNAMENT STATUS

4–6 bullets or short sentences:
- Day number and tournament stage
- Which groups play today and matchday number
- Who has clinched / who is eliminated (relevant to today's groups only)
- Group standings for today's groups only. Format: `Group B: Canada 4pts | Switzerland 4pts | Bosnia 1pt | Qatar 0pts`
- One sentence on broader tournament picture if notable

Scannable. Not an essay.

---

### SECTION 3 — RESULTS

Two dated subsections. Never merge under one header.

**Yesterday — [Weekday, Month D]**
**Two Days Ago — [Weekday, Month D]**

Format per match: `- Team A X–Y Team B (Group Z) — [note]`
- En-dash (–) between goals. Em-dash (—) before note.
- Late-night games (11 PM or midnight ET kickoff) count for the calendar date they kicked off.
- Notes: 1–2 sentences, editorial voice. One sharp observation — market implication, narrative angle, or tactical read. Pick the most valuable. Don't pad.
- If no matches for a subsection: "No matches."

---

### SECTION 4 — TODAY'S MATCHES

One bold header + one paragraph per match. No blank line between header and paragraph.

Header format: `**Team A vs. Team B — H:MM PM ET | Stadium Name, City | Group X**`
Use "vs." with period. ET 12-hour format. Pipe separators.

Paragraph, 4–5 sentences:
1. Group scenario — what each team needs from this match specifically.
2. Tactical setup and what WC2026 form (not reputation) suggests.
3. Key injuries or lineup factors relevant to today.
4. Venue/conditions if relevant (altitude, heat, dome — skip if standard sea-level).
5. One sentence pointing toward the prediction or bet angle.

Do not re-explain group standings — readers have TOURNAMENT STATUS.

---

### SECTION 5 — NEWS & INJURIES

4–6 bullets, one line each. From Search 1 above.
Confirmed injuries: state clearly ("X is officially out").
Unconfirmed: flag explicitly ("X reported carrying a knock — unconfirmed").
Facts only. No editorial padding.

---

### SECTION 6 — PREDICTIONS

Pure football analysis. No odds, no betting language, no units anywhere in this section.

One subsection per match. Header: `#### Team A vs. Team B`

**Paragraph 1 — Tactical read (3–4 sentences):**
Lead with the single most important tactical story of this matchup. Draw on WC2026 form first,
then qualifying/continental data as context. No reputation-only analysis ("Brazil are world-class").
Specific observations only.

**Paragraph 2 — Game flow + scoreline (2 sentences):**
Most likely game-state progression, then one clear prediction:
`Predicted score: X–X (Team A win)` or `Predicted score: X–X (Draw)`

---

### SECTION 7 — BET RECOMMENDATIONS

Pure betting. Evaluate every match in today's fixtures.

**Tiered structure — label every bet:**
- TIER 1 (1–2 per day, $8–10, 4–5 units): highest confidence only. Do not force one.
- TIER 2 (2–3 per day, $6, 3 units): well-supported edge with known risks.
- TIER 3 (2–4 per day, $2–4, 1–2 units): props, hedges, supporting plays.

**Format for every bet:**
```
**BET:** [Selection] — [Match] ([Market]) [TIER 1 / TIER 2 / TIER 3]
**ODDS:** [American odds] ([Book]) | Implied: [X.X%]
**EDGE REASONING:** [2–3 sentences. Sentence 1: the edge. Sentence 2: the support. Sentence 3 if needed: market signal or structural reason.]
**RISK LEVEL:** Low / Medium / High
**RECOMMENDED STAKE:** $X (X units)
**KEY RISK FACTORS:**
- [one line]
- [one line max]
```

Rules:
- Do NOT use "Asian Handicap" — say "spread" or write the line directly.
- Do NOT include MODEL EDGE or any model-probability field.
- If a match has no edge, state why in one sentence with the specific odds as reference.
- Include 1–2 player props when matchup data supports a specific rate.
- Only prop confirmed starters. Never prop an injury-doubt player.
- When a Tier 1/2 bet is on a favorite, evaluate whether a Tier 3 hedge on the other side makes mathematical sense. State the hedge explicitly if so.

---

### SECTION 8 — PARLAYS

4–6 parlays. Max 4 legs each. Required types:
- At least one mixing result/total legs with player props
- At least one purely player props across multiple matches
- At least one partially hedging a Tier 1 or Tier 2 straight bet

Rules: no stacking legs that all require the same team to dominate. Name any correlation explicitly.

Format:
```
**Parlay N: [Name] — [legs summary]**
- Leg 1: [selection] @ [odds]
- Leg 2: [selection] @ [odds]
- Leg 3: [selection] @ [odds — if applicable]
Estimated combined odds: approximately +XXX.
[1–2 sentences: why these legs belong together, what driver they share or don't share.]
**RECOMMENDED STAKE:** $X (X units)
```

---

### SECTION 9 — SHARP MONEY

3 bullets max, or "Nothing notable today."
Only include genuinely notable line movements or handle signals. Don't pad.

---

### SECTION 10 — AROUND THE TOURNAMENT

4–5 bullets. 1–2 sentences each — enough to deliver the observation and stop.
No odds. No bet angles. Match-specific facts belong in sections 4 or 5.
Cover: crowd moments, VAR controversies, player milestones, records broken, fan stories,
coach quotes, venue conditions, tournament narrative threads developing across groups.
Each bullet should carry one clear observation. Don't extend for personality.

---

### SECTION 11 — TOMORROW'S SLATE

One bullet per match, each on its own line:
`- H:MM PM ET — Team A vs. Team B (Group X, Venue, City)`

No analysis. No odds. Use the fixture data from LIVE DATA below.

---

## LIVE DATA — {report_date} {data_timestamp}

### Today's Fixtures ({report_date})
{today_fixtures}

### Results — Yesterday ({yesterday_date})
{yesterday_results}

### Results — Two Days Ago ({two_days_ago_date})
{two_days_ago_results}

### Tomorrow's Fixtures
{tomorrow_fixtures}

### Current Odds
{odds_block}

### Line Movements vs Yesterday
{line_movements}

### Injury Report
{injury_report}

---

## KEY CONTEXT

### Group Standings (today's groups only)
{group_standings}

### Advancement Scenarios
{advancement_scenarios}

### Additional Intelligence
{additional_context}
"""


def dump_web_prompt(
    system_prompt: str,
    today_str: str,
    fixtures: list,
    fixtures_tomorrow: list,
    recent_results: str,
    odds_result: dict,
    injuries: list,
    line_movements: str,
) -> Path:
    """Assemble the v2 web-prompt template and write to reports/YYYY-MM-DD_web_prompt.txt.

    The output is formatted for direct paste into a Claude web chat. Only two
    web searches are embedded as explicit instructions (news/injuries, and
    tournament color) — match scores are pre-fetched here via the Anthropic
    API so Claude web doesn't need to search for them.
    """
    et_now = now_et()
    yesterday_dt = et_now - timedelta(days=1)
    two_days_ago_dt = et_now - timedelta(days=2)

    yesterday_results, two_days_ago_results = split_results_by_date(
        recent_results,
        yesterday_dt.strftime("%Y-%m-%d"),
        two_days_ago_dt.strftime("%Y-%m-%d"),
    )

    today_teams = " ".join(sorted({
        name
        for f in fixtures
        for name in (
            f.get("teams", {}).get("home", {}).get("name"),
            f.get("teams", {}).get("away", {}).get("name"),
        )
        if name
    }))

    fields = {
        "report_date": today_str,
        "search_date": et_now.strftime("%B %d %Y"),
        "today_teams": today_teams or "(no fixtures found)",
        "system_prompt": system_prompt,
        "today_fixtures": format_today_fixtures(fixtures),
        "yesterday_date": _fmt_human_date(yesterday_dt),
        "yesterday_results": yesterday_results,
        "two_days_ago_date": _fmt_human_date(two_days_ago_dt),
        "two_days_ago_results": two_days_ago_results,
        "tomorrow_fixtures": format_tomorrow_fixtures(fixtures_tomorrow),
        "odds_block": format_odds_block_v2(odds_result),
        "line_movements": line_movements or "  No significant line movements vs yesterday's cache.",
        "injury_report": format_injuries_block(injuries),
        "data_timestamp": et_now.strftime("%H:%M ET"),
        "group_standings": "(Use confirmed scores above to infer standings)",
        "advancement_scenarios": "(Claude web will determine from standings above)",
        "additional_context": "None.",
    }

    assembled = WEB_PROMPT_TEMPLATE.format(**fields)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"{today_str}_web_prompt.txt"
    out_path.write_text(assembled, encoding="utf-8")
    return out_path


# ── Git Push ───────────────────────────────────────────────────────────────────

def git_commit_and_push(report_path: Path, today_str: str) -> None:
    try:
        # Only add the report file (safe — avoids accidentally staging secrets)
        result = subprocess.run(
            ["git", "status", "--porcelain", str(report_path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            print("[INFO] No changes to commit for report file.")
            return
        subprocess.run(["git", "add", str(report_path)], cwd=str(ROOT), check=True)
        commit_msg = f"report: {today_str} morning briefing"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(ROOT), check=True)
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Git operation failed: {e}", file=sys.stderr)
        return

    branch = (
        subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(ROOT), capture_output=True, text=True,
        ).stdout.strip()
        or "main"
    )

    # The commit above is safe locally regardless of what happens below — push
    # collisions must never lose the report, only fail to publish it.
    for attempt in (1, 2):
        subprocess.run(["git", "fetch", "origin"], cwd=str(ROOT), check=True)
        behind = subprocess.run(
            ["git", "rev-list", "--count", f"HEAD..origin/{branch}"],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        if int(behind.stdout.strip() or "0") > 0:
            print(f"[GIT] Local is behind origin/{branch}; rebasing before push.")
            rebase = subprocess.run(
                ["git", "pull", "--rebase", "origin", branch],
                cwd=str(ROOT), capture_output=True, text=True,
            )
            if rebase.returncode != 0:
                # Check which files are conflicting
                conflict_check = subprocess.run(
                    ["git", "diff", "--name-only", "--diff-filter=U"],
                    cwd=str(ROOT), capture_output=True, text=True,
                )
                conflicting = conflict_check.stdout.strip().splitlines()
                report_rel = str(report_path.relative_to(ROOT))

                if conflicting == [report_rel]:
                    # Only the report file conflicts — take our local version automatically
                    subprocess.run(
                        ["git", "checkout", "--ours", report_rel],
                        cwd=str(ROOT), check=True,
                    )
                    subprocess.run(
                        ["git", "add", report_rel],
                        cwd=str(ROOT), check=True,
                    )
                    env = {**os.environ, "GIT_EDITOR": "true"}
                    continue_result = subprocess.run(
                        ["git", "rebase", "--continue"],
                        cwd=str(ROOT), capture_output=True, text=True, env=env,
                    )
                    if continue_result.returncode == 0:
                        print(f"[GIT] Auto-resolved report conflict; rebase continued.")
                    else:
                        subprocess.run(["git", "rebase", "--abort"], cwd=str(ROOT))
                        print(
                            f"[ERROR] Auto-resolve failed. Report committed locally but NOT pushed. "
                            f"Run: git rebase --abort && git push --force-with-lease",
                            file=sys.stderr,
                        )
                        return
                else:
                    # Non-report files conflicting — abort and surface for manual resolution
                    subprocess.run(["git", "rebase", "--abort"], cwd=str(ROOT))
                    print(
                        f"[ERROR] Rebase conflict on non-report files: {conflicting}. "
                        f"Manual resolution required: git pull --rebase origin {branch}",
                        file=sys.stderr,
                    )
                    return
            print(f"[GIT] Rebase onto origin/{branch} succeeded.")

        push = subprocess.run(["git", "push"], cwd=str(ROOT), capture_output=True, text=True)
        if push.returncode == 0:
            print(f"[OK] Committed and pushed: {commit_msg}")
            return

        if attempt == 1:
            print(
                f"[GIT] Push rejected, retrying fetch/rebase/push once: {push.stderr.strip()}",
                file=sys.stderr,
            )
        else:
            print(
                f"[ERROR] Push failed after retry. Report '{commit_msg}' is committed "
                f"locally but NOT pushed to origin/{branch}: {push.stderr.strip()}",
                file=sys.stderr,
            )


# ── Email Sending ─────────────────────────────────────────────────────────────

def build_email_html(markdown_content: str) -> str:
    """Convert markdown report to styled light-mode HTML email."""
    import re

    lines = markdown_content.split('\n')
    output_blocks = []  # list of HTML strings
    i = 0

    def inline_format(text: str) -> str:
        """Apply inline markdown formatting to a string."""
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#1a56db;text-decoration:none;">\1</a>', text)
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#111827;font-weight:600;">\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        return text

    def slugify(heading_html: str) -> str:
        """GitHub-style slug: strip tags/punctuation (no substitution), turn each
        whitespace run-char into its own hyphen, so it matches the anchors the
        model already writes in its TOC (e.g. "Today's Matches" -> "todays-matches",
        "News & Injuries" -> "news--injuries")."""
        text = re.sub(r'<[^>]+>', '', heading_html).lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\s', '-', text)
        return text.strip('-')

    def is_match_header(line: str) -> bool:
        """Detect a bold match-preview header line."""
        stripped = line.strip()
        return (stripped.startswith('**') and stripped.endswith('**')
                and ' ET ' in stripped and ' | ' in stripped
                and not stripped.startswith('**BET:')
                and not stripped.startswith('**ODDS:')
                and not stripped.startswith('**EDGE')
                and not stripped.startswith('**RISK')
                and not stripped.startswith('**RECOMMENDED')
                and not stripped.startswith('**KEY')
                and not stripped.startswith('**Parlay'))

    def is_bet_label(line: str) -> bool:
        """Detect a bet block label line."""
        stripped = line.strip()
        return any(stripped.startswith(label) for label in [
            '**BET:', '**ODDS:', '**EDGE REASONING:', '**RISK LEVEL:',
            '**RECOMMENDED STAKE:', '**KEY RISK FACTORS:'
        ])

    def is_parlay_header(line: str) -> bool:
        """Detect a parlay block header."""
        stripped = line.strip()
        return re.match(r'\*\*Parlay \d+:', stripped) is not None

    def render_bet_block(block_lines: list) -> str:
        """Render a bet recommendation block as an amber-bordered card."""
        rendered = []
        for line in block_lines:
            line = line.strip()
            if not line or line == '---':
                continue
            if line.startswith('- '):
                rendered.append(f'<div style="margin:2px 0 2px 12px;color:#374151;font-size:13px;">• {inline_format(line[2:])}</div>')
            else:
                # Bold label + value
                rendered.append(f'<div style="margin:4px 0;font-size:13px;line-height:1.5;">{inline_format(line)}</div>')
        return (
            '<div style="background:#fffbeb;border-left:4px solid #f59e0b;border-radius:0 6px 6px 0;'
            'padding:14px 16px;margin:16px 0;">'
            + '\n'.join(rendered)
            + '</div>'
        )

    def render_parlay_block(block_lines: list) -> str:
        """Render a parlay block as a blue-grey bordered card."""
        rendered = []
        for line in block_lines:
            line = line.strip()
            if not line or line == '---':
                continue
            if line.startswith('- '):
                rendered.append(f'<div style="margin:2px 0 2px 12px;color:#374151;font-size:13px;">• {inline_format(line[2:])}</div>')
            else:
                rendered.append(f'<div style="margin:4px 0;font-size:13px;line-height:1.5;">{inline_format(line)}</div>')
        return (
            '<div style="background:#f0f4ff;border-left:4px solid #6366f1;border-radius:0 6px 6px 0;'
            'padding:14px 16px;margin:16px 0;">'
            + '\n'.join(rendered)
            + '</div>'
        )

    # Group lines into logical blocks
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines (handled as block separators implicitly)
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped == '---':
            output_blocks.append('<hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;">')
            i += 1
            continue

        # H1
        if stripped.startswith('# ') and not stripped.startswith('##'):
            text = stripped[2:]
            output_blocks.append(
                f'<h1 style="font-size:22px;font-weight:700;color:#111827;'
                f'border-bottom:2px solid #e5e7eb;padding-bottom:12px;margin:0 0 8px;">'
                f'{inline_format(text)}</h1>'
            )
            i += 1
            continue

        # H2
        if stripped.startswith('## '):
            text = stripped[3:]
            heading_text = inline_format(text)
            slug = slugify(heading_text)
            output_blocks.append(
                f'<h2 id="{slug}" style="font-size:13px;font-weight:700;color:#1a56db;'
                f'text-transform:uppercase;letter-spacing:0.7px;margin:28px 0 10px;">'
                f'{heading_text}</h2>'
            )
            i += 1
            continue

        # H3
        if stripped.startswith('### '):
            text = stripped[4:]
            heading_text = inline_format(text)
            slug = slugify(heading_text)
            output_blocks.append(
                f'<h3 id="{slug}" style="font-size:15px;font-weight:600;color:#1f2937;margin:20px 0 6px;">'
                f'{heading_text}</h3>'
            )
            i += 1
            continue

        # H4
        if stripped.startswith('#### '):
            text = stripped[5:]
            output_blocks.append(
                f'<h4 style="font-size:14px;font-weight:600;color:#374151;margin:16px 0 4px;">'
                f'{inline_format(text)}</h4>'
            )
            i += 1
            continue

        # Bet block — collect until blank line or next bet block or ---
        if is_bet_label(stripped):
            block_lines = []
            while i < len(lines) and lines[i].strip() and lines[i].strip() != '---':
                block_lines.append(lines[i])
                i += 1
            output_blocks.append(render_bet_block(block_lines))
            continue

        # Parlay block
        if is_parlay_header(stripped):
            block_lines = []
            while i < len(lines) and lines[i].strip() and lines[i].strip() != '---':
                block_lines.append(lines[i])
                i += 1
            output_blocks.append(render_parlay_block(block_lines))
            continue

        # Match preview header — bold line with ET time and pipes
        if is_match_header(stripped):
            # Strip outer **
            text = stripped[2:-2]
            # Split into name part and meta part on first |
            parts = text.split(' | ', 1)
            name = parts[0].strip()
            meta = parts[1].strip() if len(parts) > 1 else ''
            output_blocks.append(
                f'<div style="background:#f8fafc;border-left:4px solid #1a56db;'
                f'border-radius:0 6px 6px 0;padding:10px 14px;margin:20px 0 6px;">'
                f'<div style="font-size:15px;font-weight:700;color:#111827;">{inline_format(name)}</div>'
                f'<div style="font-size:12px;color:#6b7280;margin-top:3px;">{inline_format(meta)}</div>'
                f'</div>'
            )
            i += 1
            continue

        # Bullet list — collect consecutive bullet lines, with one level of nesting
        if stripped.startswith('- '):
            list_items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                content = lines[i].strip()[2:]
                i += 1
                # Collect any nested "  - " items that follow this top-level item
                nested_items = []
                while i < len(lines) and lines[i].startswith('  - '):
                    nested_items.append(
                        f'<li style="margin-bottom:3px;line-height:1.6;color:#6b7280;font-size:13px;'
                        f'padding-left:4px;">{inline_format(lines[i].strip()[2:])}</li>'
                    )
                    i += 1
                sub_html = ''
                if nested_items:
                    sub_html = (
                        '<ul style="padding-left:16px;margin:4px 0 2px;list-style-type:none;">'
                        + ''.join(nested_items)
                        + '</ul>'
                    )
                list_items.append(
                    f'<li style="margin-bottom:6px;line-height:1.65;color:#374151;">'
                    f'{inline_format(content)}{sub_html}</li>'
                )
            output_blocks.append(
                '<ul style="padding-left:20px;margin:8px 0 12px;">'
                + ''.join(list_items)
                + '</ul>'
            )
            continue

        # Regular paragraph — collect until blank line
        para_lines = []
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#'):
            current = lines[i].strip()
            # Stop if we hit a structural element
            if (current == '---' or current.startswith('- ')
                    or is_bet_label(current) or is_parlay_header(current)
                    or is_match_header(current)):
                break
            para_lines.append(current)
            i += 1

        if para_lines:
            text = ' '.join(para_lines)
            output_blocks.append(
                f'<p style="font-size:14px;line-height:1.75;color:#374151;margin:0 0 14px;">'
                f'{inline_format(text)}</p>'
            )
        else:
            i += 1

    body_html = '\n'.join(output_blocks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>World Cup 2026 Morning Report</title>
</head>
<body style="margin:0;padding:0;background-color:#f6f8fa;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f6f8fa;">
    <tr>
      <td align="center" style="padding:24px 12px 40px;">

        <!-- Content card -->
        <table width="640" cellpadding="0" cellspacing="0" border="0"
               style="max-width:640px;width:100%;background:#ffffff;
                      border:1px solid #e5e7eb;border-radius:8px;
                      box-shadow:0 1px 3px rgba(0,0,0,0.08);">
          <tr>
            <!-- Top accent bar -->
            <td style="background:linear-gradient(90deg,#1a56db,#6366f1);
                       height:4px;border-radius:8px 8px 0 0;font-size:0;">&nbsp;</td>
          </tr>
          <tr>
            <td style="padding:28px 32px 32px;">
              {body_html}

              <!-- Footer -->
              <div style="margin-top:32px;padding-top:16px;border-top:1px solid #e5e7eb;
                          font-size:12px;color:#9ca3af;text-align:center;">
                World Cup 2026 Morning Report &nbsp;|&nbsp;
                <a href="https://levijb.github.io/WorldCup2026/dashboard/tournament.html"
                   style="color:#1a56db;text-decoration:none;">Live Dashboard</a>
              </div>
            </td>
          </tr>
        </table>

      </td>
    </tr>
  </table>

</body>
</html>"""


def send_emails(report_text: str, today_str: str) -> None:
    import smtplib
    import ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    if not GMAIL_APP_PASSWORD:
        print("[WARN] GMAIL_APP_PASSWORD not set, skipping email.", file=sys.stderr)
        return
    if not GMAIL_FROM:
        print("[WARN] RESEND_TO_EMAIL (Gmail sender address) not set, skipping email.", file=sys.stderr)
        return

    try:
        subscribers = json.loads(SUBSCRIBERS_PATH.read_text(encoding="utf-8")).get("subscribers", [])
    except (json.JSONDecodeError, OSError) as e:
        print(f"[WARN] Could not load subscribers: {e}", file=sys.stderr)
        return

    active = [s for s in subscribers if s.get("active")]
    if not active:
        print("[INFO] No active subscribers.")
        return

    et_now = now_et()
    weekday = et_now.strftime("%A")
    date_display = et_now.strftime("%B %d").replace(" 0", " ").lstrip()
    subject = f"World Cup 2026 Morning Brief — {weekday} {date_display}"
    html_body = build_email_html(report_text)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(GMAIL_FROM, GMAIL_APP_PASSWORD)
            for sub in active:
                to_email = sub.get("email", "")
                if not to_email or to_email == "REPLACE_WITH_YOUR_EMAIL":
                    print(f"[SKIP] Subscriber '{sub.get('name')}' has no valid email.")
                    continue
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = subject
                    msg["From"] = GMAIL_FROM
                    msg["To"] = to_email
                    msg.attach(MIMEText(html_body, "html"))
                    server.sendmail(GMAIL_FROM, to_email, msg.as_string())
                    print(f"[OK] Email sent to {to_email}")
                except smtplib.SMTPException as e:
                    print(f"[WARN] Email send failed for {to_email}: {e}", file=sys.stderr)
    except smtplib.SMTPAuthenticationError:
        print("[WARN] Gmail authentication failed — check GMAIL_APP_PASSWORD in .env", file=sys.stderr)
    except smtplib.SMTPException as e:
        print(f"[WARN] SMTP connection failed: {e}", file=sys.stderr)


# ── Send Saved Report ──────────────────────────────────────────────────────────

def send_saved_report(date_str: str) -> None:
    """Read an already-saved report from disk and send it. Does NOT regenerate."""
    report_path = REPORTS_DIR / f"{date_str}_morning_report.md"
    if not report_path.exists():
        print(f"[ERROR] No report found for {date_str} at {report_path}")
        print("[ERROR] Generate it first with: python agent/morning_report.py")
        sys.exit(1)
    report_text = report_path.read_text(encoding="utf-8")
    print(f"[SEND] Sending report from {report_path}")
    send_emails(report_text, date_str)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="WC2026 Morning Report Generator")
    parser.add_argument("--no-email", action="store_true", help="(ignored) Email never auto-sends")
    parser.add_argument("--no-push", action="store_true", help="Skip git commit/push")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt, skip Claude API call")
    parser.add_argument("--send-email", action="store_true", help="Send today's saved report (no regeneration)")
    parser.add_argument("--send-date", metavar="YYYY-MM-DD", help="Date of report to send (default: today)")
    parser.add_argument(
        "--web-prompt",
        action="store_true",
        help="Build and save the assembled prompt to reports/YYYY-MM-DD_web_prompt.txt for use in Claude web (one lightweight results lookup uses the API; no full report generation call)",
    )
    args = parser.parse_args()

    if args.send_email:
        date_str = args.send_date if args.send_date else today_date_str()
        send_saved_report(date_str)
        return

    today_str = today_date_str()
    print(f"[START] Generating morning report for {today_str}")

    # 1. Load system prompt
    if not SYSTEM_PROMPT_PATH.exists():
        print("[ERROR] agent/system_prompt.md not found.", file=sys.stderr)
        sys.exit(1)
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    # 2. Fetch data that doesn't require Anthropic
    print("[FETCH] Odds...")
    odds_result = fetch_odds()

    print("[FETCH] Today's fixtures (from odds cache)...")
    fixtures = fetch_fixtures_today()
    fixtures_tomorrow = fetch_fixtures_tomorrow()

    print("[FETCH] Injuries...")
    injuries = fetch_injuries()

    # 3. Cache upcoming Pinnacle odds for the next 3 days (optional — requires STATS_API_KEY)
    cache_upcoming_wc_odds()

    # 4. Load yesterday's cache for line movement comparison
    previous_cache = load_odds_cache()
    line_movements = compute_line_movements(odds_result["data"], previous_cache)

    # 5. Web searches: recent results + news (share one Anthropic client)
    if args.web_prompt:
        # v2 web prompt: pre-fetch results here (cheap) so Claude web doesn't
        # need to search for scores. News and atmosphere stay deferred to the
        # two search instructions embedded in the prompt itself.
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            print("[FETCH] Recent results via web search (pre-filled for Claude web)...")
            recent_results = fetch_recent_results_via_search(client)
        except Exception as e:
            recent_results = f"(recent results unavailable: {e})"
        news = "(Claude web will search for this — see search instructions above)"
        around_the_tournament = "(Claude web will search for this — see search instructions above)"
    elif not args.dry_run:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            print("[FETCH] Recent results via web search...")
            recent_results = fetch_recent_results_via_search(client)
            print("[FETCH] News via web search...")
            news = fetch_news_via_claude(client, today_str)
            print("[FETCH] Around the tournament via web search...")
            around_the_tournament = fetch_atmosphere_via_claude(client, today_str)
        except Exception as e:
            recent_results = f"(recent results unavailable: {e})"
            news = f"(news search unavailable: {e})"
            around_the_tournament = f"(atmosphere search unavailable: {e})"
    else:
        recent_results = "(recent results skipped in dry-run mode)"
        news = "(news search skipped in dry-run mode)"
        around_the_tournament = "(atmosphere search skipped in dry-run mode)"

    # 6. Build prompt
    static_context = build_static_context()
    dynamic_content = build_dynamic_content(
        today_str=today_str,
        fixtures=fixtures,
        fixtures_tomorrow=fixtures_tomorrow,
        recent_results=recent_results,
        odds_result=odds_result,
        injuries=injuries,
        news=news,
        around_the_tournament=around_the_tournament,
        line_movements=line_movements,
    )

    if args.dry_run:
        print("\n" + "=" * 60)
        print("SYSTEM PROMPT (first 500 chars):")
        print(system_prompt[:500])
        print("\n" + "=" * 60)
        print("STATIC CONTEXT:")
        print(static_context)
        print("\n" + "=" * 60)
        print("DYNAMIC CONTENT (first 2000 chars):")
        print(dynamic_content[:2000])
        print("=" * 60)
        print("[DRY RUN] Skipping Claude API call, report save, git push, and email.")
        return

    # ── Web prompt path ────────────────────────────────────────────────────────
    if args.web_prompt:
        out_path = dump_web_prompt(
            system_prompt=system_prompt,
            today_str=today_str,
            fixtures=fixtures,
            fixtures_tomorrow=fixtures_tomorrow,
            recent_results=recent_results,
            odds_result=odds_result,
            injuries=injuries,
            line_movements=line_movements,
        )
        print(f"[WEB PROMPT] Saved to {out_path}")
        print(f"[WEB PROMPT] Paste into claude.ai — Claude will run the two search instructions and write the report.")
        print(f"[WEB PROMPT] After editing, send with: python agent/morning_report.py --send-email")
        return

    # 8. Call Claude
    print("[CLAUDE] Generating report...")
    report_text = call_claude(system_prompt, static_context, dynamic_content)

    # 9. Save odds cache (before saving report so quota is current)
    save_odds_cache(odds_result["data"])

    # 10. Save report
    quota_remaining = odds_result.get("quota_remaining", "unknown")
    report_path = save_report(report_text, today_str, quota_remaining)

    # 11. Git commit and push
    if not args.no_push:
        git_commit_and_push(report_path, today_str)

    print(f"[DONE] Report saved to {report_path}")
    print(f"[NEXT] Review and edit the file, then send with:")
    print(f"       python agent/morning_report.py --send-email")


if __name__ == "__main__":
    main()
