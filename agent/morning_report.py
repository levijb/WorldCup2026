"""
morning_report.py — Daily betting intelligence report generator.

Usage:
    python agent/morning_report.py                # full run
    python agent/morning_report.py --no-email     # skip email send
    python agent/morning_report.py --no-push      # skip git commit/push
    python agent/morning_report.py --dry-run      # print prompt, no Claude call
"""

import argparse
import json
import os
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
MODEL_PREDICTIONS_PATH = ROOT / "data" / "processed" / "model_predictions.json"

# ── Config ────────────────────────────────────────────────────────────────────
ODDS_API_KEY = os.getenv("THE_ODDS_API_KEY", "")
API_SPORTS_KEY = os.getenv("API_SPORTS_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_TO_EMAIL = os.getenv("RESEND_TO_EMAIL", "")

MODEL = "claude-sonnet-4-6"
ET_OFFSET = timedelta(hours=-4)  # EDT (UTC-4)


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
    """Fetch today's WC fixtures from API-Sports."""
    try:
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {"x-apisports-key": API_SPORTS_KEY}
        params = {"league": 1, "season": 2026, "date": today_date_str()}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("response", [])
    except requests.RequestException as e:
        print(f"[WARN] API-Sports fixtures fetch failed: {e}", file=sys.stderr)
        return []


def fetch_recent_results() -> list:
    """Fetch WC results from the last 3 days."""
    try:
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {"x-apisports-key": API_SPORTS_KEY}
        today = now_et().date()
        from_date = (today - timedelta(days=3)).isoformat()
        to_date = (today - timedelta(days=1)).isoformat()
        params = {"league": 1, "season": 2026, "from": from_date, "to": to_date}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("response", [])
    except requests.RequestException as e:
        print(f"[WARN] API-Sports recent results fetch failed: {e}", file=sys.stderr)
        return []


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
    """Run a web search for today's WC news via Claude's web_search tool."""
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": (
                    f"Search for: '{today_str} World Cup 2026 news team form injury updates lineup'. "
                    "Return a concise bullet-point summary of the most important items found, "
                    "focused on match-relevant news, injuries, suspensions, and lineup changes."
                ),
            }],
        )
        # Extract text from response — tool use blocks come back with tool_result content
        text_parts = [b.text for b in resp.content if hasattr(b, "text")]
        return "\n".join(text_parts) if text_parts else "(no news retrieved)"
    except Exception as e:
        print(f"[WARN] News search failed: {e}", file=sys.stderr)
        return f"(news search unavailable: {e})"


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


def build_dynamic_content(
    today_str: str,
    fixtures: list,
    recent_results: list,
    odds_result: dict,
    injuries: list,
    news: str,
    line_movements: str,
    model_predictions_md: str,
) -> str:
    """Dynamic content block: today's data — never cache this."""
    et_now = now_et().strftime("%Y-%m-%d %H:%M ET")

    # Format today's fixtures
    fixture_lines = []
    for f in fixtures:
        try:
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            kickoff_utc = f["fixture"]["date"]
            kickoff_dt = datetime.fromisoformat(kickoff_utc.replace("Z", "+00:00"))
            kickoff_et = kickoff_dt.astimezone(timezone(ET_OFFSET)).strftime("%I:%M %p ET")
            venue = f["fixture"].get("venue", {}).get("name", "TBD")
            city = f["fixture"].get("venue", {}).get("city", "")
            fixture_lines.append(f"  • {kickoff_et} | {home} vs {away} | {venue}, {city}")
        except (KeyError, ValueError):
            fixture_lines.append(f"  • {f}")
    fixtures_text = "\n".join(fixture_lines) if fixture_lines else "  No fixtures found for today."

    # Format recent results
    result_lines = []
    for f in recent_results:
        try:
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            hg = f["goals"]["home"]
            ag = f["goals"]["away"]
            match_date = f["fixture"]["date"][:10]
            result_lines.append(f"  • {match_date}: {home} {hg}–{ag} {away}")
        except (KeyError, TypeError):
            pass
    results_text = "\n".join(result_lines) if result_lines else "  No recent results."

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

    # Format injuries
    inj_lines = []
    for inj in injuries[:30]:  # cap at 30 entries for prompt length
        try:
            player = inj["player"]["name"]
            team = inj["team"]["name"]
            reason = inj.get("injury", {}).get("reason", "unknown")
            inj_lines.append(f"  • {player} ({team}): {reason}")
        except (KeyError, TypeError):
            pass
    injuries_text = "\n".join(inj_lines) if inj_lines else "  No injury data available."

    return f"""## LIVE DATA — {et_now}

### Today's Fixtures ({today_str})
{fixtures_text}

### Recent Results (Last 3 Days)
{results_text}

### Current DraftKings Odds
{odds_text}

Odds quota remaining: {odds_result.get('quota_remaining', 'unknown')}

### Line Movements vs Yesterday
{line_movements}

### Injury Report
{injuries_text}

### Today's News & Intelligence
{news}

{model_predictions_md}

---

## REQUEST

Please produce the full morning briefing report with these sections:

1. **OVERNIGHT SUMMARY** — Results from yesterday, key developments since last report, any breaking news affecting today's bets.

2. **TODAY'S MATCH PREVIEWS** — For each match today, a focused preview covering: tactical matchup, form, key players, conditions, narrative context.

3. **BET RECOMMENDATIONS (3–5 bets)** — Use the exact structured format from the system prompt. Include model edge for each. Justify every recommendation specifically.

4. **PARLAY SUGGESTIONS (1–2 parlays)** — $1–5 each, max 3 legs. Explain leg selection rationale.

5. **SHARP MONEY OBSERVATIONS** — Notable line movements, reverse line movement, any steam detected.

6. **KEY WATCH ITEMS** — Lineup confirmations, weather checks, news to monitor before matches kick off.

Use specific American odds numbers. Be concise but thorough. If no strong plays exist today, say so explicitly.
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


# ── Model Predictions ──────────────────────────────────────────────────────────

def load_model_predictions_markdown() -> str:
    """Load model predictions and format as markdown for the prompt."""
    if not MODEL_PREDICTIONS_PATH.exists():
        return "## MODEL PREDICTIONS\n\n(Model predictions not yet generated — run model/predictions.py first)"
    try:
        predictions = json.loads(MODEL_PREDICTIONS_PATH.read_text(encoding="utf-8"))
        generated_at = predictions.get("generated_at", "unknown")
        matches = predictions.get("predictions", [])
        if not matches:
            return f"## MODEL PREDICTIONS\n\nGenerated: {generated_at}\n(No predictions for today)"
        lines = [f"## MODEL PREDICTIONS\n\nGenerated: {generated_at}\n"]
        for pred in matches:
            home = pred.get("home_team", "?")
            away = pred.get("away_team", "?")
            lines.append(f"### {home} vs {away}")
            lines.append(f"- Model xG: {home} {pred.get('home_xg_pred', '?')} — {away} {pred.get('away_xg_pred', '?')}")
            lines.append(
                f"- Win probabilities: {home} {pred.get('home_win_pct', '?')}% | "
                f"Draw {pred.get('draw_pct', '?')}% | {away} {pred.get('away_win_pct', '?')}%"
            )
            # Edges
            for edge_key, label in [
                ("home_edge", f"{home} ML edge"),
                ("draw_edge", "Draw edge"),
                ("away_edge", f"{away} ML edge"),
                ("over_25_edge", "Over 2.5 edge"),
                ("under_25_edge", "Under 2.5 edge"),
                ("btts_edge", "BTTS Yes edge"),
            ]:
                edge_val = pred.get(edge_key)
                if edge_val is not None:
                    flag = " ← EDGE" if edge_val >= 5 else (" ← mild edge" if edge_val >= 3 else "")
                    lines.append(f"- {label}: {edge_val:+.1f}%{flag}")
            # Top scorelines
            top = pred.get("top_scorelines", [])[:3]
            if top:
                sl_str = " | ".join(f"{s['score']} ({s['pct']}%)" for s in top)
                lines.append(f"- Top scorelines: {sl_str}")
            # Player props
            props = pred.get("player_props", [])
            if props:
                lines.append("- Player props:")
                for p in props:
                    lines.append(f"  • {p.get('player')}: anytime scorer {p.get('anytime_scorer_pct', '?')}%")
            lines.append("")
        return "\n".join(lines)
    except (json.JSONDecodeError, OSError, KeyError) as e:
        return f"## MODEL PREDICTIONS\n\n(Error loading predictions: {e})"


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
    generated_at = now_et().strftime("%Y-%m-%d %H:%M ET")
    header = f"# WC2026 Morning Report — {today_str}\n\n_Generated: {generated_at} | API quota remaining: {quota_remaining}_\n\n---\n\n"
    report_path.write_text(header + report_text, encoding="utf-8")
    print(f"[OK] Report saved to {report_path}")
    return report_path


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
        subprocess.run(["git", "push"], cwd=str(ROOT), check=True)
        print(f"[OK] Committed and pushed: {commit_msg}")
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Git operation failed: {e}", file=sys.stderr)


# ── Email Sending ─────────────────────────────────────────────────────────────

def markdown_to_html(md_text: str) -> str:
    """Minimal markdown-to-HTML converter using inline styles — no external CSS."""
    import re
    lines = md_text.split("\n")
    html_lines = []
    bold_re = re.compile(r"\*\*(.+?)\*\*")
    bold_repl = r'<strong style="color:#ffffff">\1</strong>'
    for line in lines:
        if line.startswith("### "):
            line = f'<h3 style="color:#e0e0e0;margin:16px 0 4px">{bold_re.sub(bold_repl, line[4:])}</h3>'
        elif line.startswith("## "):
            line = f'<h2 style="color:#ffffff;margin:20px 0 6px;border-bottom:1px solid #333;padding-bottom:4px">{bold_re.sub(bold_repl, line[3:])}</h2>'
        elif line.startswith("# "):
            line = f'<h1 style="color:#ffffff;margin:0 0 16px">{bold_re.sub(bold_repl, line[2:])}</h1>'
        elif line.strip() == "---":
            line = '<hr style="border:none;border-top:1px solid #333;margin:16px 0">'
        elif line.startswith("- ") or line.startswith("• "):
            content = bold_re.sub(bold_repl, line[2:])
            line = f'<li style="margin:2px 0">{content}</li>'
        elif line.strip() == "":
            line = "<br>"
        else:
            line = f'<p style="margin:4px 0">{bold_re.sub(bold_repl, line)}</p>'
        html_lines.append(line)

    body_content = "\n".join(html_lines)
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="background:#0f1117;color:#c0c0c0;font-family:Georgia,serif;max-width:700px;margin:0 auto;padding:24px;line-height:1.6;font-size:15px">
{body_content}
<hr style="border:none;border-top:1px solid #333;margin:24px 0">
<p style="color:#555;font-size:12px">WorldCup2026 — automated morning briefing</p>
</body>
</html>"""


def send_emails(report_text: str, today_str: str) -> None:
    if not RESEND_API_KEY:
        print("[WARN] RESEND_API_KEY not set, skipping email.", file=sys.stderr)
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
    subject = f"⚽ WC2026 Morning Brief — {weekday} {date_display}"
    html_body = markdown_to_html(report_text)
    from_addr = RESEND_TO_EMAIL or "noreply@worldcup2026.local"

    for sub in active:
        to_email = sub.get("email", "")
        if not to_email or to_email == "REPLACE_WITH_YOUR_EMAIL":
            print(f"[SKIP] Subscriber '{sub.get('name')}' has no valid email.")
            continue
        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"from": from_addr, "to": [to_email], "subject": subject, "html": html_body},
                timeout=15,
            )
            if resp.status_code == 200:
                print(f"[OK] Email sent to {to_email}")
            else:
                print(f"[WARN] Resend returned {resp.status_code} for {to_email}: {resp.text}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"[WARN] Email send failed for {to_email}: {e}", file=sys.stderr)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="WC2026 Morning Report Generator")
    parser.add_argument("--no-email", action="store_true", help="Skip sending emails")
    parser.add_argument("--no-push", action="store_true", help="Skip git commit/push")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt, skip Claude API call")
    args = parser.parse_args()

    today_str = today_date_str()
    print(f"[START] Generating morning report for {today_str}")

    # 1. Load system prompt
    if not SYSTEM_PROMPT_PATH.exists():
        print("[ERROR] agent/system_prompt.md not found.", file=sys.stderr)
        sys.exit(1)
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    # 2. Fetch all data sources
    print("[FETCH] Odds...")
    odds_result = fetch_odds()

    print("[FETCH] Today's fixtures...")
    fixtures = fetch_fixtures_today()

    print("[FETCH] Recent results...")
    recent_results = fetch_recent_results()

    print("[FETCH] Injuries...")
    injuries = fetch_injuries()

    # 3. Cache upcoming Pinnacle odds for the next 3 days (optional — requires STATS_API_KEY)
    cache_upcoming_wc_odds()

    # 4. Load yesterday's cache for line movement comparison
    previous_cache = load_odds_cache()
    line_movements = compute_line_movements(odds_result["data"], previous_cache)

    # 5. Web search for news (only if not dry-run — costs API tokens)
    if not args.dry_run:
        print("[FETCH] News via web search...")
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            news = fetch_news_via_claude(client, today_str)
        except Exception as e:
            news = f"(news search unavailable: {e})"
    else:
        news = "(news search skipped in dry-run mode)"

    # 6. Load model predictions
    print("[MODEL] Loading predictions...")
    model_predictions_md = load_model_predictions_markdown()

    # 7. Build prompt
    static_context = build_static_context()
    dynamic_content = build_dynamic_content(
        today_str=today_str,
        fixtures=fixtures,
        recent_results=recent_results,
        odds_result=odds_result,
        injuries=injuries,
        news=news,
        line_movements=line_movements,
        model_predictions_md=model_predictions_md,
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

    # 12. Send emails
    if not args.no_email:
        send_emails(report_text, today_str)

    print(f"[DONE] Morning report complete for {today_str}")


if __name__ == "__main__":
    main()
