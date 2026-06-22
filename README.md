# WorldCup2026

Personal FIFA World Cup 2026 betting intelligence system — daily AI-generated reports, live odds tracking, and a browser dashboard. Built for DraftKings and FanDuel with small-stake straight bets and parlays.

Built with Clade web and Clause Code.

Contains prompt .md files for generating in-depth reports on teams, players, and matchups.

**Tournament:** June 11 – July 19, 2026 | USA / Mexico / Canada

---

## Prerequisites

- Python 3.12
- Git
- API accounts (all free tiers are sufficient):
  - [The Odds API](https://the-odds-api.com) — DraftKings live odds
  - [API-Sports](https://api-sports.io) — fixtures, scores, injuries, standings
  - [Anthropic](https://console.anthropic.com) — Claude API for report generation (optional — see `--web-prompt` below)
  - [Resend](https://resend.com) — email delivery
  - [TheStatsAPI](https://www.thestatsapi.com) — xG and historical data (7-day trial, run data_collector.py once during trial)

---

## Setup

```bash
git clone https://github.com/levijb/WorldCup2026.git
cd WorldCup2026
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
# Edit .env with your keys
```

Also update `data/subscribers.json` with your email address.

---

## Usage

### Morning Report

Two modes: API mode (calls Claude directly) or web mode (paste into claude.ai, no API tokens).

**Web mode — recommended daily workflow:**

```bash
# Step 1: fetch live data and build prompt file
python agent/morning_report.py --web-prompt
# → reports/YYYY-MM-DD_web_prompt.txt

# Step 2: open the file, copy everything, paste into claude.ai
# Step 3: copy Claude's response into reports/YYYY-MM-DD_morning_report.md
# Step 4: review and edit, then send
python agent/morning_report.py --send-email
```

**API mode — calls Claude directly (requires ANTHROPIC_API_KEY):**

```bash
python agent/morning_report.py           # fetch data, call Claude API, save report
python agent/morning_report.py --no-push # skip git commit/push
python agent/morning_report.py --dry-run # print assembled prompt, no Claude call
```

**Send a saved report:**

```bash
python agent/morning_report.py --send-email                    # send today's report
python agent/morning_report.py --send-email --send-date 2026-06-20  # send a past report
```

### Live Query (before or during a match)

```bash
python agent/live_query.py                          # all matches today/next 6h
python agent/live_query.py --match "Brazil vs Morocco"  # specific match
python agent/live_query.py --match "Spain vs France" --save  # save to reports/
```

### Dashboard

Open `dashboard/index.html` in a browser. On first load, enter your The Odds API key (stored in localStorage). The page auto-refreshes odds every 5 minutes.

Open `dashboard/tournament.html` for the group stage table and knockout bracket.

### Add a Subscriber

Edit `data/subscribers.json`:

```json
{
  "subscribers": [
    { "name": "Me", "email": "you@example.com", "active": true },
    { "name": "Friend", "email": "friend@example.com", "active": true }
  ]
}
```

---

## GitHub Actions (Automated Daily Reports)

Add these secrets to your repo at **Settings → Secrets → Actions**:

| Secret | Source |
|--------|--------|
| `THE_ODDS_API_KEY` | The Odds API dashboard |
| `API_SPORTS_KEY` | API-Sports dashboard |
| `ANTHROPIC_API_KEY` | Anthropic console |
| `RESEND_API_KEY` | Resend dashboard |
| `RESEND_TO_EMAIL` | Your personal email |
| `STATS_API_KEY` | TheStatsAPI dashboard |

The automatic 7:00 AM ET schedule is currently disabled — reports are generated manually via `--web-prompt`. To trigger a one-off API-generated report, use the **Actions** tab → **Morning Report** → **Run workflow**. To re-enable the daily schedule, uncomment the `schedule` block in `.github/workflows/morning-report.yml`.

For on-demand live queries, use `.github/workflows/manual-trigger.yml` from the Actions tab — enter a match name in the input field.

---

## Model Layer

The Poisson/Dixon-Coles prediction model is currently disabled — output was unreliable with limited group-stage data. Model files remain in the repo for potential re-enablement in the knockout rounds.

---

## File Structure

```
WorldCup2026/
├── agent/
│   ├── system_prompt.md        # Claude system prompt (role, intelligence, formats)
│   ├── morning_report.py       # Daily report generator
│   └── live_query.py           # On-demand match query
├── dashboard/
│   ├── index.html              # Odds, bets, reports dashboard
│   └── tournament.html         # Group table + knockout bracket
├── data/
│   ├── bets.json               # Bet log (edit manually)
│   ├── subscribers.json        # Email subscribers
│   └── odds_cache.json         # Odds cache (gitignored)
├── researchPrompts/            # Prompt templates for match research and betting strategy
├── reports/                    # Daily .md reports and web prompt files
├── .github/workflows/
│   ├── morning-report.yml      # Manual trigger only (cron disabled)
│   └── manual-trigger.yml      # workflow_dispatch with match_focus input
├── .env                        # Local secrets (gitignored)
├── .env.example                # Key template
└── requirements.txt
```
