# WorldCup2026

A personal AI-powered World Cup 2026 newsletter and betting intelligence system. Every morning during the tournament, I run the AI prompts to generate the morning report, manually edit it, and send it via email to subscribers. The reports cover tournament news, match previews, tactical predictions, and betting recommendations for the day's games.

Built with Claude (web and Code) and Python. I originally designed the newsletter to be completely automated but that requires paying extra for API tokens, so I switched to a web based final prompt to pull live data. 

**Tournament:** June 11 – July 19, 2026 | USA / Mexico / Canada

---

## What it does

**Daily morning report (the main product):** A structured newsletter sent each morning via email covering:
- Tournament status and group standings
- Yesterday's results with editorial notes
- Today's match previews with tactical analysis
- Injury and lineup news
- Pure soccer predictions with scorelines
- Tiered bet recommendations (straight bets, props, hedges)
- Parlays with correlation analysis
- Sharp money signals
- Around the tournament — color stories, fan moments, records

**Live dashboard** (`levijb.github.io/WorldCup2026/dashboard/`):
- Group standings and knockout bracket (auto-updated from openfootball data)
- Live odds tracking via The Odds API (DraftKings lines, implied probabilities, line movement)
- All past morning reports in a rendered viewer
- Bet tracker with P&L

**Deep match research:** Four prompt templates (`researchPrompts/`) for pre-bet research on individual matches, teams, and players — covering tactical matchup analysis, player prop profiles, and full betting strategy synthesis. Used for deep dives on key matches before generating the morning report.

---

## How the report is generated

The system was originally designed to be fully automated: a GitHub Actions cron job at 7 AM ET would fetch live data, call the Claude API, generate the report, and email it — zero human involvement. That vision is mostly intact in the code.

In practice, two things pushed it toward a semi-manual workflow:

**1. I like to edit the reports.** The AI-generated base is strong but benefits from a human pass — catching stale data, adjusting tone, adding context from things I noticed watching the games. The final report is always better for it.

**2. The Claude API costs too much per report at the quality level required.** Generating a full structured morning report with web search via the API runs $0.80–1.50 per call. Over a 39-day tournament that adds up fast. Claude web (claude.ai) produces identical output at no marginal cost since it's a flat subscription — but it can't be triggered automatically from a script.

**The current workflow:**

```bash
# Step 1: fetch live data and build the prompt file
python agent/morning_report.py --web-prompt
# → reports/YYYY-MM-DD_web_prompt.txt

# Step 2: paste the prompt file into a new Claude web chat (claude.ai)
# Claude runs web searches, writes the full report

# Step 3: copy Claude's output into the reports folder
# reports/YYYY-MM-DD_morning_report.md

# Step 4: edit as needed, then send
python agent/morning_report.py --send-email
```

The `--web-prompt` flag assembles a complete self-contained prompt file with the system prompt, live odds, fixture data, confirmed scores, search instructions, and section format — everything Claude needs to generate the report without any additional context. Paste and run.

The fully automated API path still works if you want it (`python agent/morning_report.py` with `ANTHROPIC_API_KEY` set), but the web mode is the daily driver.

---

## Prerequisites

- Python 3.12
- Git
- API accounts (free tiers are sufficient for all):
  - [The Odds API](https://the-odds-api.com) — live DraftKings odds
  - [API-Sports](https://api-sports.io) — fixtures, scores, injuries, standings
  - [Anthropic](https://console.anthropic.com) — Claude API (optional — only needed for automated mode)
  - [Resend](https://resend.com) — email delivery
  - [TheStatsAPI](https://www.thestatsapi.com) — xG and historical data (7-day trial; run `data_collector.py` once during trial to cache what you need)

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

Update `data/subscribers.json` with your email list:

```json
{
  "subscribers": [
    { "name": "Me", "email": "you@example.com", "active": true },
    { "name": "Friend", "email": "friend@example.com", "active": true }
  ]
}
```

---

## Usage

### Morning Report

**Web mode — daily workflow (recommended):**

```bash
# Fetch live data and build the prompt
python agent/morning_report.py --web-prompt
# → reports/YYYY-MM-DD_web_prompt.txt

# Paste the file into claude.ai → copy output → save as reports/YYYY-MM-DD_morning_report.md
# Edit, then send:
python agent/morning_report.py --send-email
```

**API mode — fully automated (requires ANTHROPIC_API_KEY):**

```bash
python agent/morning_report.py           # fetch, generate, save, push, email
python agent/morning_report.py --no-push # skip git commit/push
python agent/morning_report.py --dry-run # print assembled prompt, no Claude call
```

**Send a saved report:**

```bash
python agent/morning_report.py --send-email                         # today's report
python agent/morning_report.py --send-email --send-date 2026-06-20  # specific date
```

### Live Query

For odds and analysis right before or during a match:

```bash
python agent/live_query.py                           # all matches today/next 6h
python agent/live_query.py --match "Brazil vs Morocco"  # specific match
python agent/live_query.py --match "Spain vs France" --save  # save to reports/
```

### Dashboard

Open `dashboard/tournament.html` for group standings and the knockout bracket.

Open `dashboard/index.html` for live odds. On first load, enter your The Odds API key (stored in localStorage). Auto-refreshes every 5 minutes.

Open `dashboard/reports.html` to browse and read past morning reports in a rendered viewer.

---

## Research Prompts

Four prompt templates in `researchPrompts/` for deep pre-bet research on individual matches:

| File | Purpose |
|------|---------|
| `bettingResearch.md` | Master strategy — orchestrates the other three into a full betting report |
| `teamResearch.md` | Tactical and statistical profile of a single national team |
| `matchupResearch.md` | Head-to-head breakdown for a specific match |
| `playerPropResearch.md` | Individual player profile for prop market evaluation |

Paste the relevant file into a Claude web chat, ask for a research report on a specific match or player, then use the output to inform the morning report's betting section. Most useful for knockout round matches where a single game warrants a full deep dive.

---

## GitHub Actions

Secrets required (Settings → Secrets → Actions):

| Secret | Source |
|--------|--------|
| `THE_ODDS_API_KEY` | The Odds API dashboard |
| `API_SPORTS_KEY` | API-Sports dashboard |
| `ANTHROPIC_API_KEY` | Anthropic console |
| `RESEND_API_KEY` | Resend dashboard |
| `RESEND_TO_EMAIL` | Your personal email |
| `STATS_API_KEY` | TheStatsAPI dashboard |

The 7 AM ET cron schedule is currently disabled — reports run manually via the web workflow. To trigger a one-off API-generated report: Actions tab → Morning Report → Run workflow. To re-enable the daily schedule, uncomment the `schedule` block in `.github/workflows/morning-report.yml`.

---

## Model Layer

The Poisson/Dixon-Coles prediction model is currently disabled — output was unreliable with limited group-stage match data. Model files are in the repo for potential re-enablement in the knockout rounds once more match data accumulates.

---

## File Structure

```
WorldCup2026/
├── agent/
│   ├── system_prompt.md        # Claude system prompt — v2 (role, intelligence, format)
│   ├── morning_report.py       # Daily report generator (web-prompt + API modes)
│   └── live_query.py           # On-demand match query
├── dashboard/
│   ├── index.html              # Live odds and bet tracker
│   ├── tournament.html         # Group standings and knockout bracket
│   ├── reports.html            # Report browser
│   └── report-viewer.html      # Rendered markdown report viewer
├── data/
│   ├── bets.json               # Bet log (edit manually)
│   ├── subscribers.json        # Email subscribers
│   └── odds_cache.json         # Odds cache (gitignored)
├── researchPrompts/
│   ├── bettingResearch.md      # Master betting strategy prompt
│   ├── matchupResearch.md      # Match tactical breakdown
│   ├── teamResearch.md         # Team profile template
│   └── playerPropResearch.md   # Player prop research template
├── reports/                    # Daily .md reports and web prompt files
├── .github/workflows/
│   ├── morning-report.yml      # Cron disabled; manual trigger available
│   └── manual-trigger.yml      # On-demand live query via workflow_dispatch
├── .env                        # Local secrets (gitignored)
├── .env.example                # Key template
└── requirements.txt
```
