# Matchup Analysis Research Template

## How to use

Paste this into a Claude chat with the two teams and match details. Example prompt: "Run a full matchup analysis on Portugal vs DR Congo using matchupResearch.md." If you've already run team profiles on both sides, mention that — this template builds on team-level knowledge but focuses on the *interaction* between two specific teams in a specific match context.

---

## Instructions

You are building a tactical and statistical matchup breakdown for a specific World Cup 2026 match. The goal is understanding how these two teams interact — where the advantages lie, what the game is likely to look like, and what patterns to expect. Use live web search throughout. This is primarily a research document; a light betting lens is fine but the core output is analytical, not prescriptive.

### Evidence hierarchy

Weight evidence in this order for matchup analysis:

1. **This World Cup's matches for both teams** — highest weight. Actual WC2026 performance overrides all prior context.
2. **Head-to-head record in competitive matches** — weight by recency and competition importance. A 2022 WC meeting matters more than a 2019 friendly.
3. **Continental tournament and qualifier form** — high weight for tactical tendencies.
4. **Friendlies** — low weight for results; moderate for persistent tactical patterns across multiple friendlies.

Avoid carrying tactical assumptions from one opponent to another. Just because Team A defends deep against everyone doesn't mean Team B will.

### Tone and format

- Conversational, direct, dense. No preambles.
- Lead with the single most important tactical story of this matchup — the thing that will most likely decide the game. Don't bury it under scene-setting.
- Flag thin evidence. 1–2 match samples are not tendencies.

---

## Research sections (complete all)

### 1. Match context

- Competition stage (group matchday 1/2/3, knockout round), date, venue, kickoff time
- What each team needs from this match: must-win, can-afford-a-draw, dead rubber, etc.
- Group standings and scenarios if applicable — does the result affect other teams' fates?
- Bracket implications: does finishing 1st vs 2nd materially change the R32/R16 path? If yes, explain the divergence.

### 2. Tactical shape matchup

- Expected formations for both teams
- How do these formations interact? Where are the numerical advantages and mismatches?
  - Example: a 4-3-3 pressing team vs a 3-5-2 that builds through wing-backs creates specific overload/underload zones
- Which team is likely to have more possession? Does the other team *want* to cede it?
- Pressing vs build-up: can Team A's press disrupt Team B's build-up? Or does Team B have the technical quality to play through it?
- Transition battle: which team is more dangerous on the counter? Which is more exposed when they lose the ball?

### 3. Key individual matchups

- Identify 2–3 player-vs-player or player-vs-zone matchups that will shape the game
- For each: who has the advantage and why?
- Examples: a pacy winger against a slow-footed fullback, a creative midfielder against a team that doesn't press the 10 space, a target striker against a high defensive line
- Are there specific injury absences that create or eliminate a mismatch?

### 4. Attacking threat assessment (both sides)

For each team:
- Primary attacking channel: central combination play, wide crosses, direct balls in behind, set pieces?
- Shot volume expectation based on opponent quality and own tendencies
- xG context: what's a realistic xG range for this team against this level of opponent?
- Who scores? Primary goal threats and their recent form (tournament + last 12 months, weighted by competition importance — see match context weighting in teamResearch.md)

### 5. Defensive vulnerability assessment (both sides)

For each team:
- Where do they concede? Crosses, transitions, set pieces, individual errors?
- How does the opponent's attacking style map onto those vulnerabilities?
  - Example: if Team A concedes from crosses and Team B's primary attacking channel is wide delivery, that's a clear exploitable angle
- Defensive transition quality: what happens when they lose the ball in the attacking third?
- Keeper form: is the goalkeeper over or underperforming xGOT (expected goals on target)?

### 6. Set piece battle

- Corner frequency for both teams (won and conceded per match)
- Expected total corners for the match based on both teams' rates and the territorial dominance expectation
- Which team is more dangerous from corners? Tall, physical squad or technical delivery?
- Free kick and penalty angles if relevant
- Set piece defensive weaknesses on either side

### 7. Discipline and game management

- Card tendencies for both teams
- Is this a matchup likely to produce cards? (Physical style clash, tactical fouling to stop transitions, rivalry/intensity)
- Referee assignment if known — and their card/foul tendencies
- Game management: which team is better at protecting a lead? Which is more likely to chase the game and leave themselves exposed?
- Substitution patterns: does either manager make early tactical subs or wait until 70+ minutes?

### 8. Conditions and context factors

- Venue: indoor/outdoor, surface, altitude (Azteca at 7,300 ft is a real factor), dimensions
- Weather: temperature, humidity, precipitation — relevant if extreme
- Travel and rest: how many days since each team's last match? Did either team travel a long distance between venues?
- Fan dynamics: is one team playing with a de facto home crowd?
- Time of day: late-night kickoffs in hot climates favor the team more accustomed to those conditions

### 9. Historical precedent

- Head-to-head record (but weight by recency and competition importance — a 2014 World Cup meeting matters more than a 2019 friendly)
- Have these tactical archetypes clashed before? (e.g. "high-pressing European team vs compact African counter-attacking team" has a pattern even if these specific teams haven't met)
- Does either team have a historical pattern in this stage of the tournament? (e.g. consistently poor in group openers, strong in must-win scenarios)

### 10. Game prediction framework

Synthesize everything above into:

- **Most likely game state progression**: how does this game unfold minute by minute? (e.g. "Team A dominates possession early, Team B absorbs and counters, first goal likely comes from X")
- **Most likely scoreline range**: not a single prediction, but a range (1-0 / 2-1 / 0-0 type cluster)
- **Total goals lean**: over or under, and why — based on both teams' xG generation/concession rates and the tactical dynamic
- **BTTS lean**: both teams to score or not? Based on defensive quality and whether the underdog can generate chances
- **Upset likelihood**: what's the realistic path for the underdog? What specific things have to go right?

### 11. Game-state risk mapping

This is the single most overlooked factor in match analysis. How does the game change *after* a goal?

- **If the favorite scores first**: do they keep pressing or sit back and protect? Does the underdog open up (creating more chances both ways) or stay compact?
- **If the underdog scores first**: does the favorite have the tactical flexibility to chase? Do they become reckless? Does the underdog have the experience to manage a lead?
- **Goalless at halftime**: how does each team adjust? Does either manager have a track record of effective halftime tactical changes?

This matters for props and totals: an early goal in a lopsided match can *suppress* second-half counting stats because the favorite eases off. Conversely, a tight match that opens up late can produce a burst of shots and corners in the final 15 minutes.

---

## Quality checks before finishing

- Did you identify the single most important tactical dynamic, and is it the first thing in section 2?
- Did you avoid carrying a framework from one team's typical opponent to this specific opponent? (e.g. "they defend deep against everyone" — do they? Or only against teams that dominate possession, which this opponent might not?)
- Did you weight historical results by competition importance and recency?
- Did you map each team's attacking strengths against the other's defensive weaknesses specifically, rather than just listing both in isolation?
- Did you address game-state effects on the likely flow of the match?

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
