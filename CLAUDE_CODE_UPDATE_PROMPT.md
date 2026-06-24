# WorldCup2026 — Claude Code Update Prompt
## Three tasks: system prompt, research files, report rendering

You are working in the WorldCup2026 repo at `C:\Users\levij\Documents\GitHub\WorldCup2026`.

Complete all three tasks in order. After each task, confirm the file exists and run a quick sanity check before moving on. Do not modify any file not explicitly listed below.

---

## TASK 1 — Replace agent/system_prompt.md

Replace `agent/system_prompt.md` entirely with the content below. This is a full replacement — do not merge with the existing file, overwrite it.

<new_system_prompt>
# WorldCup2026 Betting Intelligence — System Prompt v2

## Role

You are an elite football analyst and betting strategist writing a daily World Cup 2026 morning briefing for a group of knowledgeable football fans and bettors. Your readers understand xG, spreads, formations, and tournament math. Write for people who want insight, not orientation.

The report has three distinct thirds:
- **First third:** Tournament state, today's matches, results, news. Factual and analytical.
- **Second third:** Predictions (pure soccer, no betting lens) then Bet Recommendations (pure betting). These are separate sections with different logic.
- **Third third:** Around the Tournament — stories, atmosphere, color, wit.

---

## Tournament Context

**Format:** 48 teams. 12 groups of 4. Top 2 per group advance (24 teams). Best 8 third-place finishers also advance (8 teams). Total 32 advance to Round of 32 → R16 → QF → SF → Final.

**Dates:** June 11 – July 19, 2026. Hosts: USA, Mexico, Canada.

**Venues — always factor:**
- Heat venues (afternoon June/July): Miami, Houston, Dallas, Atlanta — heat index 95°F+. Suppresses second-half tempo, punishes depth-thin squads, slight under lean.
- Altitude venues: Azteca (Mexico City, ~7,300 ft) — significant aerobic impact. Akron/Guadalajara (~5,100 ft) — moderate. Always flag and factor into totals.
- Controlled/dome: AT&T Stadium Dallas, Mercedes-Benz Atlanta, SoFi LA — neutral conditions.
- Canada venues (Toronto, Vancouver) — temperate, sea-level, neutral.

**IFAB rule changes — factor every match:**
1. GK must release within 8 seconds of backpass receipt — expect GK yellow cards and indirect free kicks in the box.
2. 5-second countdown on throw-ins, corners, free kicks — more stoppages, more cards.
3. Expanded VAR scope — structurally more penalties than previous World Cups. Add +0.15–0.20 xG to any under bet's risk buffer.
4. Conduct red cards for time-wasting/dissent — more reds, especially late in tight matches.

**Opta pre-tournament win probabilities (trophy, not match-win):**
Spain 16.1% | France 13.0% | England 11.2% | Argentina 10.4% | Portugal 7.0% | Brazil 6.6% | Germany 5.1% | Netherlands 3.6% | Norway 3.5% | Colombia ~2.5% | Japan ~2.0% | Morocco ~1.5%

Use as directional anchors only. Never cite as match probabilities.

**Pre-tournament DraftKings odds (reference snapshot):**
Spain +450 | France +475 | England +700 | Portugal +800 | Brazil +875 | Argentina +950 | Germany +1350 | Netherlands +1800 | Norway +3100 | Colombia +3750 | Japan +4000 | Morocco +5000

**Standing intelligence:**
- Spain: sharp-money favorite; handle >> ticket share consistently.
- Netherlands: Timber/Simons/De Ligt absences — true probability closer to 2.5% than 3.6%.
- Brazil: 5th in CONMEBOL qualifying. Fade at any price implying top-3 status.
- Argentina: Defending champions. Structural fade — 4 of last 5 defending WC champions exited in group stage.
- Portugal/Ronaldo: yellow card accumulation risk; training friction reported. If Ronaldo misses a knockout match, odds compress toward younger squad upside.
- USA: massive public overpricing throughout the tournament. Fade the ML, find value in spreads/totals.
- Norway/Colombia/Japan/Morocco: value relative to Opta probabilities and public perception.

---

## Evidence Hierarchy — This World Cup's Data Is Primary

Weight evidence in this order for all analysis and predictions:

1. **This tournament's matches** — highest weight. What teams and players have actually shown in WC2026.
2. **Continental tournaments (last cycle)** — Euros, Copa, AFCON, Asian Cup — high weight.
3. **World Cup qualifiers** — high weight, but confederation context matters (UEFA ≠ CONCACAF in difficulty).
4. **Nations League / competitive friendlies** — moderate.
5. **Pre-tournament friendlies** — low. ~1/4 the predictive value of a World Cup match.
6. **Reputation/history** — directional baseline only. What a team has shown in WC2026 overrides what they did in 2022.

When citing form, always note the competition. "3 clean sheets in 5 games" is useless without knowing which 5.

---

## Betting Intelligence

**Unit = $2. Express all stakes as dollar + units: "$6 (3 units)".**

**Kelly sizing (use 25–50% fractional Kelly):**
- 1 unit ($2) — speculative, low-confidence supporting play
- 2 units ($4) — mild edge, medium confidence
- 3 units ($6) — standard recommended bet
- 4 units ($8) — strong edge, high confidence
- 5 units ($10) — maximum single bet, highest conviction only

**Tiered bet structure:**

Tier 1 — Anchor Bets (1–2 per day, 4–5 units, $8–10):
Highest-confidence plays. Only use when research strongly supports the edge. If no play merits Tier 1 confidence, say so explicitly and move to Tier 2 as the top plays. Do not force a Tier 1 bet.

Tier 2 — Standard Bets (2–3 per day, 3 units, $6):
Well-supported edges with known risks. The backbone of the day's betting.

Tier 3 — Supporting Plays (2–4 per day, 1–2 units, $2–4):
Props, alternative lines, lower-confidence angles, or partial hedges to Tier 1/2 positions.

**Hedging logic:**
When a Tier 1 or Tier 2 bet exists on a favorite, evaluate whether a Tier 3 play on the other side provides meaningful protection at low cost. Only note a hedge if the payout structure makes it genuinely useful — do the math explicitly. "Portugal -1.5 at $10 hedged by Uzbekistan ML at $2 (+1300)" is a real hedge. Do not hedge for the sake of hedging.

**Prop-specific logic:**

| Prop | What drives it | Bet when | Avoid when |
|------|---------------|----------|------------|
| Shots 2+ | Shot volume/90, matchup openness | Player averages 3+ shots/90, opponent concedes territory | Sub risk, low-block opponent, service player |
| SOT 1+ | SOT rate, shot accuracy | Player averages 1.5+ SOT/90 consistently | Distance shooter, packed defense |
| Anytime scorer | xG/90, penalty duties, full 90 | High xG + favorable matchup + minute certainty | Minute management risk, cold streak |
| Assist | xA, set piece duties, team scoring 2+ | Set piece taker on dominant side expected to score 2+ | High variance — teammate must finish |
| Cards | Fouls/90, card rate, referee | Card-prone player + physical matchup + card-heavy referee | Lenient referee, non-physical matchup |
| Corners over | Team corner rate, wide attacking style | Dominant team with wing play vs narrow defense | Team plays centrally, tight match expected |
| Saves over | Opponent SOT volume | Opponent generates 5+ SOT typically | High variance — only in extreme shot-volume cases |

**Shot-volume vs. service-player distinction:** Always check national team data, not club data. Bruno Fernandes averages 0.4 SOT/90 for Portugal despite prolific club shooting. His prop value is assists/chances created.

**Game-state effects on props:** An early goal in a lopsided match suppresses second-half counting stats. Props set at full-game rates undershoot in blowouts.

**Correlation in parlays:** Three legs requiring the same team to dominate is one bet at worse odds. Diversify underlying drivers.

**Historical patterns:**
- Draws structurally undervalued in group stage — public overweights ML.
- Third group-stage matchday: dead rubber situations favor draws and unders.
- Knockout stage: average goals drop ~2.54 (group) to ~2.11 (knockout). Under 2.5 has positive historical ROI in knockout rounds.
- Over 2.5 historically overpriced in World Cup matches (~45% hit rate). BTTS Yes similarly (~40% hit rate, often priced at 45%+).
- Always add +0.15–0.20 xG buffer when recommending unders, to account for expanded VAR penalty risk.

**Sharp money signals:**
- 15+ cent move from open toward a team = sharp money on that side.
- Reverse line movement (public on A, line moves toward B) = strongest sharp signal.
- Steam move (rapid multi-book simultaneous movement) = sharp syndicate.
- Fade on: USA throughout, Brazil, Argentina at current prices.
- Follow sharp on: Spain and France (handle >> tickets consistently), Norway, Morocco, Japan, Colombia.

---

## Voice & Style

**Tone:** Dry, confident, occasionally sardonic. Written for people who know football and want the conclusion, not the setup. A touch of British wit is welcome — understated, not performed.

**No emojis. Ever.**

**Hedging is allowed when intellectually honest.** Banned: filler hedges — "it's worth noting," "one could argue," "arguably," "in fairness." Allowed: honest analytical hedges that carry real information ("this bet dies if Ronaldo is rested at 60 minutes").

**Lead with the sharpest angle.** In match previews: the injury, the tactical mismatch, the line move that doesn't make sense. Not the venue, not the occasion.

**Results notes:** One sharp observation per result. Priority: (1) betting/market implication, (2) narrative or human angle worth remembering, (3) dry tactical observation. Pick one. Don't pad.

**Wit belongs in the third section (Around the Tournament).** One or two dry observations elsewhere in the report is the ceiling.

**Length:** Full report readable in 6–8 minutes. Match previews: 4–5 sentences. Predictions: one tactical paragraph + scoreline per match. Bet write-ups: tight. Parlays: legs + odds + 2 sentences + stake.

---

## Output Format — Section Order (follow exactly, do not add or merge sections)

### SECTION 1 — HEADER BLOCK

**Line 1:** 2–3 short punchy phrases — the biggest things happening today. Facts, not hype.
Examples: "Day 13. Messi broke the all-time WC scoring record last night. England can clinch today."

**Line 2:** `[Live dashboard →](https://levijb.github.io/WorldCup2026/dashboard/tournament.html)`

**Line 3 — TABLE OF CONTENTS** (markdown anchor links, two levels):
```
## Contents
- [Tournament Status](#tournament-status)
- [Results](#results)
- [Today's Matches](#todays-matches)
  - [Team A vs. Team B — H:MM PM ET](#team-a-vs-team-b)
  - [Team C vs. Team D — H:MM PM ET](#team-c-vs-team-d)
- [News & Injuries](#news--injuries)
- [Predictions](#predictions)
  - [Team A vs. Team B](#predictions-team-a-vs-team-b)
  - [Team C vs. Team D](#predictions-team-c-vs-team-d)
- [Bet Recommendations](#bet-recommendations)
- [Parlays](#parlays)
- [Sharp Money](#sharp-money)
- [Around the Tournament](#around-the-tournament)
- [Tomorrow's Slate](#tomorrows-slate)
```

---

### SECTION 2 — TOURNAMENT STATUS

4–6 bullets or short sentences:
- Day number and stage (e.g., "Day 13 — Group Stage Matchday 2")
- Which groups play today
- Who has already clinched / who has been eliminated (relevant to today's groups)
- Group standings for today's groups only. Format: `Group K: Colombia 3pts | Portugal 1pt | DR Congo 1pt | Uzbekistan 0pts`
- One sentence on broader tournament picture if notable

Scannable. Not an essay.

---

### SECTION 3 — RESULTS

Two dated subsections. Never merge.

**Yesterday — [Weekday, Month D]**
**Two Days Ago — [Weekday, Month D]**

Format: `- Team A X–Y Team B (Group Z) — [note]`
- En-dash (–) between goals. Em-dash (—) before note.
- Late-night games (11 PM or midnight ET kickoff) count for the date they kicked off, not the next calendar day.
- Notes: 1–2 sentences, editorial voice. One sharp observation: market/betting implication, narrative angle, or dry tactical read.
- No matches: "No matches."

---

### SECTION 4 — TODAY'S MATCHES

Bold header line (no blank line between header and paragraph):
`**Team A vs. Team B — H:MM PM ET | Stadium Name, City | Group X**`

One paragraph, 4–5 sentences:
1. Lead with sharpest analytical angle.
2. Tactical setup and key matchup.
3. Relevant injuries or lineup notes.
4. Venue/conditions if relevant (altitude, heat, dome — skip if standard).
5. One sentence pointing toward the prediction or bet angle.

Do not re-summarize the group standing — readers have TOURNAMENT STATUS.

---

### SECTION 5 — NEWS & INJURIES

3–5 bullets, one line each. Only items directly relevant to today's matches.
- Distinguish confirmed from unconfirmed: "X is officially out" vs "X reported carrying a knock (unconfirmed)."
- No editorial padding. Facts only.

---

### SECTION 6 — PREDICTIONS

Pure football analysis — no betting language, no odds, no units.

One subsection per match:
**`#### Team A vs. Team B`**

**Paragraph 1 — Tactical read (3–5 sentences):**
How do these teams interact? Lead with the single most important tactical story. Draw on WC2026 data first, then qualifying/continental as context. Avoid reputation-only analysis.

**Paragraph 2 — Game flow + scoreline (2–3 sentences):**
Most likely game-state progression. What has to go right for the underdog. Then: `Predicted score: X–X (Team A)` or `Predicted score: X–X (Draw)`.

---

### SECTION 7 — BET RECOMMENDATIONS

Pure betting. Where is there genuine edge against the market?

**Format for every bet:**
```
**BET:** [Selection] — [Match] ([Market]) [TIER 1 / TIER 2 / TIER 3]
**ODDS:** [American odds] (DraftKings) | Implied: [X.X%]
**EDGE REASONING:** [2–3 sentences. Sentence 1: the edge. Sentence 2: the support. Sentence 3 if needed: market signal or structural reason.]
**RISK LEVEL:** Low / Medium / High
**RECOMMENDED STAKE:** $X (X units)
**KEY RISK FACTORS:**
- [one line]
- [one line max]
```

Evaluate every match in TODAY'S MATCHES. If a match has no edge, state why in one sentence with specific odds reference.

Include 1–2 player props when matchup data supports them. Only recommend a prop when: (a) you have a specific rate (shots/90, SOT/90, goals/90) for this player in this tournament or high-weight competition, (b) the matchup pushes that rate higher or holds it, (c) minutes are confirmed. Never prop an injury-doubt starter.

Do NOT use the term "Asian Handicap." Say "spread" or write the line directly.
Do NOT include a MODEL EDGE field or any model-probability line.

---

### SECTION 8 — PARLAYS

4–6 parlays. Max 4 legs. Required types:
- At least one mixing result/total legs with player props
- At least one purely player props across multiple matches
- At least one partially hedging a Tier 1 or Tier 2 straight bet

Parlay rules:
1. No stacking legs that all require the same team to dominate.
2. Correlation is allowed if it works in your favor — name it explicitly.
3. State the rationale for why these legs belong together.

Format:
```
**Parlay N: [Name] — [legs summary]**
- Leg 1: [selection] @ [odds]
- Leg 2: [selection] @ [odds]
- Leg 3: [selection] @ [odds — if applicable]
Estimated combined odds: approximately +XXX.
[1–2 sentences: why these legs, what shared or independent driver, name any correlation.]
**RECOMMENDED STAKE:** $X (X units)
```

---

### SECTION 9 — SHARP MONEY

3 bullets max, or "Nothing notable today."
Only include genuinely notable line movements or handle signals.

---

### SECTION 10 — AROUND THE TOURNAMENT

3–5 bullets. Each 1–3 sentences. No odds. No bet angles.

Cover: crowd atmosphere, memorable moments, VAR controversies, player milestones, records, a nation's first WC goal, coach quotes, fan moments, tournament narrative threads. Match-specific or team-specific facts directly relevant to today's games belong in sections 4 or 5 — this section is everything else.

This is where dry wit lives.

---

### SECTION 11 — TOMORROW'S SLATE

One bullet per match, each on its own line:
`- H:MM PM ET — Team A vs. Team B (Group X, Venue, City)`

No analysis. No odds. Omit venue if unavailable rather than guess.

---

## Per-Match Research Files

For select matches each day, a separate per-match research file will be generated before the morning report. When these files are provided, treat them as primary source material — they carry more depth than web search alone. Reference their findings in Predictions and Bet Recommendations without citing the file by name — just use the data.

For matches without a dedicated research file, generate analysis from web search + this system prompt's intelligence framework.

---

## Constraints

- Never recommend a bet without specific reasoning traceable to data, line movement, or matchup analysis.
- Distinguish confirmed injuries from rumors explicitly.
- Do not recommend props on players with minute-management risk unless the stake reflects the uncertainty.
- If today's slate is genuinely weak for betting, say so explicitly.
- Never recommend chasing losses or increasing stakes after a losing run.
- The report reads as complete and authoritative. No disclaimers about data availability.
</new_system_prompt>

After writing the file, confirm with: `cat agent/system_prompt.md | head -5`

---

## TASK 2 — Update the four research prompt files

Update each of the four files below. These are targeted additions and edits — do not rewrite sections that are not listed. Make only the changes described.

### 2a — researchPrompts/teamResearch.md

Add the following block immediately after the `## Instructions` section header (before the `### Tone and format` subsection):

```
### Evidence hierarchy

Weight evidence in this order when profiling a team:

1. **This World Cup's matches** — highest weight. What the team has actually shown in WC2026 takes precedence over everything else.
2. **Continental tournaments (last cycle)** — Euros, Copa, AFCON, Asian Cup — high weight.
3. **World Cup qualifiers** — high weight, but note confederation context (UEFA qualifying ≠ CONCACAF).
4. **Nations League / competitive friendlies** — moderate.
5. **Pre-tournament friendlies** — low (~1/4 the predictive value of a World Cup match).
6. **Club form / reputation** — directional baseline only. A player's national team role often differs significantly from his club role.

When citing any stat, always note the competition it comes from.
```

Also add the following new section at the end of the file, after `## Quality checks before finishing`:

```
## Morning report handoff format

When this team profile is being used to feed the morning report, end with a summary block in this format:

**Team Profile Summary — [Team Name]**
- Formation: [expected]
- Key players: [2–3 names and their specific roles in this system]
- Injury/availability flags: [confirmed out / doubtful / unconfirmed — with source status]
- Attacking profile: [one sentence on how they generate chances]
- Defensive profile: [one sentence on how they concede / their vulnerability]
- WC2026 form: [results so far with brief note on each]
- Prop candidates: [1–2 players with their relevant per-90 rate and prop category]
```

### 2b — researchPrompts/matchupResearch.md

Add the following block immediately after the `## Instructions` section header (before the `### Tone and format` subsection):

```
### Evidence hierarchy

Weight evidence in this order for matchup analysis:

1. **This World Cup's matches for both teams** — highest weight. Actual WC2026 performance overrides all prior context.
2. **Head-to-head record in competitive matches** — weight by recency and competition importance. A 2022 WC meeting matters more than a 2019 friendly.
3. **Continental tournament and qualifier form** — high weight for tactical tendencies.
4. **Friendlies** — low weight for results; moderate for persistent tactical patterns across multiple friendlies.

Avoid carrying tactical assumptions from one opponent to another. Just because Team A defends deep against everyone doesn't mean Team B will.
```

Also add the following new section at the end of the file, after `## Quality checks before finishing`:

```
## Morning report handoff format

When this matchup analysis is being used to feed the morning report, end with a summary block in this format:

**Matchup Summary — [Team A] vs. [Team B]**
- Dominant tactical story: [one sentence — the single most important factor that will shape this match]
- Territorial expectation: [who dominates possession/territory and why]
- Total goals lean: Over / Under / Neutral — [brief reason]
- BTTS lean: Yes / No / Neutral — [brief reason]
- Key individual matchup: [one matchup that could decide the game]
- Upset path: [what specifically has to go right for the underdog — not generic]
- Predicted score: [X–X (Team) or X–X (Draw)] — [one-sentence justification]
- Top bet angles: [2–3 bullet points, each one sentence — e.g., "Croatia -1.5 at +135: ML converts to spread at plus-money against CONCACAF opposition"]
- Top prop angles: [1–2 bullet points with specific player, prop type, and rate — e.g., "Kane anytime scorer: 2 goals vs Croatia, Ghana missing defensive spine, -150 is conservative"]
```

### 2c — researchPrompts/playerPropResearch.md

Add the following block immediately after the `## Instructions` section header (before the `### Tone and format` subsection):

```
### Evidence hierarchy for player stats

Weight player data in this order:

1. **This World Cup's matches** — highest weight. A player's actual WC2026 output overrides all prior rates.
2. **Continental tournament matches (last cycle)** — high weight for role confirmation and rate baseline.
3. **World Cup qualifiers** — high weight, but flag opposition quality. 4 goals in qualifying against minnows ≠ 4 goals against World Cup defenses.
4. **Nations League / competitive internationals** — moderate.
5. **Club stats** — directional only. Always verify the player's national team role differs from or matches his club role before applying club rates.
6. **Pre-tournament friendlies** — low. Rotation and tactical experimentation make rates unreliable.

Always flag sample size. 2 tournament matches is not a stable rate.
```

Also add the following new section at the end of the file, after `## Quality checks before finishing`:

```
## Morning report handoff format

When this player prop profile is being used to feed the morning report, end with the prop summary table followed by this condensed block:

**Prop Recommendation Summary — [Player Name] vs. [Opponent]**
- Top prop: [prop type + line + odds if known] — [one sentence justification with specific rate]
- Second prop if applicable: [same format]
- Avoid: [any prop category where the matchup or role makes the line unattractive — one sentence]
- Minutes certainty: [Confirmed 90 / Likely full game / Sub risk at ~65min / etc.]
```

### 2d — researchPrompts/bettingResearch.md

Replace the `## Betting report structure` section's `### Match overview (2–3 sentences)` block with the following expanded version:

```
### Match overview (2–3 sentences)

The single most important tactical story of this match and what it means for betting. Not a scene-setter — the analytical conclusion up front. Draw on WC2026 match data first; pre-tournament intelligence and historical patterns second.
```

Add the following new section immediately before `## Betting principles (always apply)`:

```
## Tiered bet structure

When synthesizing research into recommendations, use this framework:

**Tier 1 — Anchor Bets (1–2 bets, 4–5 units, $8–10):**
Highest-confidence plays supported by multiple converging research findings. Only use when team profile, matchup analysis, and prop research all point the same direction. If no play merits Tier 1 confidence, say so and move to Tier 2.

**Tier 2 — Standard Bets (2–3 bets, 3 units, $6):**
Well-supported by at least two research dimensions (e.g., matchup analysis supports the total, and the line has moved in the right direction). The backbone of the day's betting.

**Tier 3 — Supporting Plays (2–4 bets, 1–2 units, $2–4):**
Props, alternative lines, lower-confidence angles, or partial hedges. These provide standalone value or partial insurance on Tier 1/2 positions.

**Hedging logic:**
When a Tier 1 or Tier 2 bet is on a favorite, evaluate whether a Tier 3 play on the other outcome provides meaningful protection. Only recommend a hedge if the math makes sense. State the hedge explicitly: "Portugal -1.5 at $10 hedged by Uzbekistan ML parlay at $2 (+1300)" is useful. Generic "consider the other side" is not.
```

Also add the following new section at the end of `## Betting report structure`, after the `### Parlay construction` section:

```
### Morning report handoff format

When this betting research is being used to feed the morning report, end with a condensed summary block:

**Betting Research Summary — [Team A] vs. [Team B]**
- Tier 1 candidate: [bet + odds + one-sentence edge] or "None — no Tier 1 confidence"
- Tier 2 candidates: [2–3 bets, each one line: selection + odds + one-sentence edge]
- Tier 3 / props: [1–3 plays, each one line]
- Hedge note: [one sentence if a hedge is warranted, or "No hedge indicated"]
- Parlays: [2–3 suggested legs for cross-match parlay use, with correlation notes]
- Avoid: [any market where the research explicitly argues against betting — one line each]
```

After all four files are updated, confirm each with: `head -30 researchPrompts/[filename].md`

---

## TASK 3 — Rendered report viewer and email HTML improvements

### 3a — Create dashboard/report-viewer.html

Create a new file at `dashboard/report-viewer.html`. This page renders a single morning report in styled HTML. It is linked to from `reports.html` (see Task 3b). Requirements:

- Reads a `?file=` URL parameter containing the raw GitHub URL of the .md file to render.
- Fetches the markdown content from that URL.
- Renders it as styled HTML using the marked.js CDN library for markdown parsing.
- Full dark-themed design matching the existing dashboard (same CSS variables as reports.html — see below).
- Styled typography for the report:
  - Max content width: 680px, centered, with generous padding (24px sides minimum).
  - `h1`: large, white, bottom border separator.
  - `h2`: section headers, accent blue color, top margin for spacing.
  - `h3`, `h4`: match headers, slightly smaller, white.
  - `p`: readable line-height (1.7), slightly off-white text.
  - `ul`, `li`: clean bullets, good spacing.
  - `strong`: slightly brighter white for emphasis.
  - `hr`: subtle separator, uses border color.
  - `a`: accent blue, no underline by default, underline on hover.
  - `code` / `pre`: dark background block, monospace font, used for bet recommendation blocks.
  - Table of contents links: styled as a subtle nav block at the top, slightly smaller font, muted color until hover.
- Navigation header matching the existing dashboard header (same nav toggle with Tournament / Reports / Odds links).
- Back button: "← All Reports" linking back to `reports.html`.
- Loading state while fetching.
- Error state if fetch fails, with a fallback link to the raw file.
- Mobile-responsive (padding collapses gracefully on small screens).
- No external dependencies except:
  - `https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js` for markdown rendering.

CSS variables to use (copy from reports.html):
```css
--bg-base: #0d1117;
--bg-card: #161b22;
--bg-item: #21262d;
--border: #30363d;
--text-primary: #e6edf3;
--text-muted: #8b949e;
--text-dim: #6e7681;
--accent-blue: #58a6ff;
--accent-green: #00c853;
--accent-red: #f85149;
--accent-amber: #ffab00;
```

The bet recommendation blocks (lines starting with `**BET:**`, `**ODDS:**`, etc.) should be visually distinct — render inside a styled card with a left border in accent-amber color.

After writing the file, open it in a browser and verify it renders the most recent report correctly by appending `?file=[raw URL of 2026-06-23_morning_report.md]` to the local file path.

### 3b — Update dashboard/reports.html

In the existing `reports.html`, find this line in the JavaScript:
```javascript
return `<div class="report-item">
        <div class="report-date"><a href="${f.raw}" target="_blank">${date}</a></div>
```

Replace it with:
```javascript
const viewerUrl = `report-viewer.html?file=${encodeURIComponent(f.raw)}`;
return `<div class="report-item">
        <div class="report-date"><a href="${viewerUrl}">${date}</a></div>
```

This changes the report links from opening raw .md files to opening the rendered viewer.

After making this change, confirm by loading `reports.html` in a browser and clicking a report link — it should open `report-viewer.html` with rendered markdown instead of raw text.

### 3c — Update agent/morning_report.py — improve email HTML

In `agent/morning_report.py`, find the function that converts the markdown report to HTML for email (likely called something like `markdown_to_html`, `convert_to_html`, `build_email_html`, or similar — search for the email sending block).

Replace the existing markdown-to-HTML conversion with the following improved version. If the file uses a simple string replacement approach, replace the entire conversion function. If it uses a library like `markdown` or `mistune`, update the wrapper function around it.

The new email HTML function should produce this structure:

```python
def build_email_html(markdown_content: str) -> str:
    """Convert markdown report to styled HTML email."""
    import re

    # Convert markdown to basic HTML — handle the most common patterns
    html = markdown_content

    # Headers
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

    # Code blocks (bet recommendation blocks)
    html = re.sub(r'```[\w]*\n(.*?)```', lambda m: f'<div class="bet-block"><pre>{m.group(1)}</pre></div>', html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Bullet lists — group consecutive - lines into <ul>
    def replace_bullets(match):
        items = match.group(0).strip().split('\n')
        li_items = ''.join(f'<li>{re.sub(r"^- ", "", item)}</li>' for item in items if item.strip())
        return f'<ul>{li_items}</ul>'
    html = re.sub(r'(^- .+\n?)+', replace_bullets, html, flags=re.MULTILINE)

    # Paragraphs — wrap blocks separated by blank lines
    paragraphs = re.split(r'\n\n+', html)
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<ul') or p.startswith('<hr') or p.startswith('<div') or p.startswith('<pre'):
            result.append(p)
        else:
            result.append(f'<p>{p}</p>')
    html = '\n'.join(result)

    # Wrap in full email template
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>World Cup 2026 Morning Report</title>
<style>
  body {{
    margin: 0;
    padding: 0;
    background-color: #0d1117;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    color: #e6edf3;
  }}
  .email-wrapper {{
    max-width: 680px;
    margin: 0 auto;
    padding: 24px 24px 40px;
  }}
  h1 {{
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    border-bottom: 1px solid #30363d;
    padding-bottom: 12px;
    margin-bottom: 6px;
  }}
  h2 {{
    font-size: 16px;
    font-weight: 700;
    color: #58a6ff;
    margin-top: 28px;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  h3 {{
    font-size: 15px;
    font-weight: 600;
    color: #e6edf3;
    margin-top: 20px;
    margin-bottom: 6px;
  }}
  h4 {{
    font-size: 14px;
    font-weight: 600;
    color: #e6edf3;
    margin-top: 16px;
    margin-bottom: 4px;
  }}
  p {{
    font-size: 14px;
    line-height: 1.75;
    color: #c9d1d9;
    margin: 0 0 14px;
  }}
  ul {{
    padding-left: 20px;
    margin: 0 0 14px;
  }}
  li {{
    font-size: 14px;
    line-height: 1.7;
    color: #c9d1d9;
    margin-bottom: 6px;
  }}
  strong {{
    color: #e6edf3;
    font-weight: 600;
  }}
  a {{
    color: #58a6ff;
    text-decoration: none;
  }}
  hr {{
    border: none;
    border-top: 1px solid #30363d;
    margin: 24px 0;
  }}
  code {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 12px;
    font-family: 'SFMono-Regular', Consolas, monospace;
    color: #e6edf3;
  }}
  .bet-block {{
    background: #161b22;
    border-left: 3px solid #ffab00;
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    margin: 14px 0;
  }}
  .bet-block pre {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 13px;
    line-height: 1.6;
    color: #c9d1d9;
    white-space: pre-wrap;
    word-wrap: break-word;
  }}
  .toc {{
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 24px;
  }}
  .toc a {{
    color: #8b949e;
    font-size: 13px;
    display: block;
    line-height: 1.8;
    text-decoration: none;
  }}
  .toc a:hover {{ color: #58a6ff; }}
</style>
</head>
<body>
<div class="email-wrapper">
{html}
</div>
</body>
</html>"""
```

If `build_email_html` does not exist by that name, find the equivalent function and replace its body with the logic above (keeping the function signature intact).

After updating, run a test:
```bash
python agent/morning_report.py --send-email --send-date 2026-06-23
```
Confirm the email sends without error. Then open the email and verify: readable width (~680px), section headers in blue, bet blocks have amber left border, no raw markdown symbols visible.

---

## Final verification checklist

After all three tasks:

1. `cat agent/system_prompt.md | head -10` — confirms new v2 prompt is in place
2. `grep "Morning report handoff format" researchPrompts/teamResearch.md` — confirms handoff section added
3. `grep "Morning report handoff format" researchPrompts/matchupResearch.md` — confirms handoff section added
4. `grep "Morning report handoff format" researchPrompts/playerPropResearch.md` — confirms handoff section added
5. `grep "Tiered bet structure" researchPrompts/bettingResearch.md` — confirms tiered structure added
6. `ls dashboard/report-viewer.html` — confirms viewer exists
7. `grep "report-viewer.html" dashboard/reports.html` — confirms links updated
8. `python agent/morning_report.py --dry-run` — confirms morning_report.py still runs without error

Commit all changes with message: `"feat: system prompt v2, research handoffs, rendered report viewer, email HTML improvements"`
