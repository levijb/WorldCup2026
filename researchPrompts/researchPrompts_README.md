# Research Prompts

Four prompt templates for World Cup 2026 match research and betting strategy. Designed for use in a Claude web chat (claude.ai) — paste the relevant file contents as the system or opening message, then ask your question.

---

## Files

| File | Purpose |
|------|---------|
| `bettingResearch.md` | Master strategy prompt — orchestrates the other three into a full betting report |
| `teamResearch.md` | Deep tactical + statistical profile of a single national team |
| `matchupResearch.md` | Head-to-head breakdown for a specific match |
| `playerPropResearch.md` | Individual player profile for prop market evaluation |

---

## How to use

### Option A — Full betting strategy (most common)

Paste `bettingResearch.md` into a Claude chat. Then say:

> "Build a full betting strategy for [Team A] vs [Team B]."

The prompt instructs the agent to automatically run team profiles on both sides, a matchup analysis, and player prop profiles on key players — then synthesize everything into a structured betting report covering moneyline, totals, corners, player props, and 2–4 constructed parlays.

### Option B — Individual research reports

Paste the relevant template and ask for a single report:

> "Run a full team profile on Japan using the teamResearch.md template."

> "Run a matchup analysis for Argentina vs Mexico."

> "Build a player prop profile on Kylian Mbappé for France vs Poland."

These produce information-heavy tactical documents. Useful when you want to understand a team or player deeply before deciding which bets to make. Run them first, then take the findings into `bettingResearch.md` for the actual betting strategy.

### Option C — Specific questions

Paste `bettingResearch.md` and ask a narrow question:

> "What's the corners angle for England vs Senegal?"

> "Is Ronaldo a viable anytime scorer against South Korea?"

> "Which parlay legs from today's slate make sense together?"

The agent answers from the relevant section without running the full workflow.

---

## How the files relate

```
bettingResearch.md
│
├── calls → teamResearch.md (run for both teams)
├── calls → matchupResearch.md (run for the specific match)
└── calls → playerPropResearch.md (run for 3–5 key players)
         │
         └── synthesizes all findings into:
               • Moneyline / spread analysis
               • Total goals (over/under, BTTS)
               • Corners market
               • Player props with matchup adjustments
               • 2–4 constructed parlays with correlation checks
               • Risk levels and stake guidance
```

---

## Key principles baked into the templates

**Match importance weighting** — not all results count equally. The templates weight matches on a hierarchy: World Cup matches > continental tournament matches > qualifiers > Nations League > friendlies. A team that went 5-0 in pre-tournament friendlies has told you almost nothing. A team that went 3-1 in the group stage tells you a lot.

**Club stats ≠ national team stats** — a player's role for his national team often differs significantly from his club role. Always check national team per-90 data, not club data. The templates enforce this explicitly.

**Shot-volume vs service-player distinction** — the most common player prop error. A creative midfielder who assists constantly but shoots rarely should be evaluated on assist/chances-created props, not shots props. The player prop template catches this.

**Game-state effects on props** — an early goal in a lopsided match suppresses second-half counting stats because the favorite eases off. Props set at full-game average rates will undershoot in blowouts. The matchup template has a dedicated section on this.

**Correlation in parlays** — stacking three legs that all require the same team to dominate is one bet with worse odds, not three independent bets. The betting strategy template enforces diversification of underlying drivers across parlay legs.

---

## Recommended workflow

1. Check today's slate the night before
2. Identify 1–3 matches worth researching deeply
3. For each: paste `bettingResearch.md` into a fresh Claude chat → "full betting strategy for [match]"
4. Pull the best angles from each report into your actual bets
5. Cross-match parlay legs can be built in the same session by asking "now build me parlays across today's three matches"
