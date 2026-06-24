# Team Profile Research Template

## How to use

Paste this into a Claude chat along with the team name. Example prompt: "Run a full team profile on Japan using the teamResearch.md template." The output is a reference document — tactical and statistical, not a betting slip. It feeds into matchup analysis and betting strategy downstream.

---

## Instructions

You are building a comprehensive intelligence profile on a single national team for the 2026 FIFA World Cup. Use live web search for everything — do not rely on training data for any current-tournament or recent-form information. This is a research document, not a betting recommendation. A slight betting lens is fine (e.g. "this team's corner rate supports over lines") but the primary goal is accurate, information-dense tactical profiling.

### Evidence hierarchy

Weight evidence in this order when profiling a team:

1. **This World Cup's matches** — highest weight. What the team has actually shown in WC2026 takes precedence over everything else.
2. **Continental tournaments (last cycle)** — Euros, Copa, AFCON, Asian Cup — high weight.
3. **World Cup qualifiers** — high weight, but note confederation context (UEFA qualifying ≠ CONCACAF).
4. **Nations League / competitive friendlies** — moderate.
5. **Pre-tournament friendlies** — low (~1/4 the predictive value of a World Cup match).
6. **Club form / reputation** — directional baseline only. A player's national team role often differs significantly from his club role.

When citing any stat, always note the competition it comes from.

### Tone and format

- Conversational but dense. No fluff, no restating the question, no closing summaries.
- Use structure (headers, short bullets) when it helps readability, but keep bullets to 1–2 sentences max.
- Lead every section with the most important finding, not the setup.
- Flag when sample size is small or evidence is mixed. Don't present 1–2 matches as settled tendencies.

---

## Research sections (complete all)

### 1. Current tournament status

- Group, current record, points, goal difference, qualification standing
- Results so far in this World Cup with scorelines
- Where they sit relative to advancement (clinched, alive, eliminated, scenarios)

### 2. Manager and tactical identity

- Manager name, tenure, tactical philosophy in 2–3 sentences
- Primary formation(s) used in this tournament and in qualifying
- Do they change shape mid-match? Under what game states?
- Pressing style: high press, mid-block, low block? PPDA if available
- Transition speed: do they counter quickly or recycle possession?
- How much training time does this manager typically get with the squad? (Long-tenured managers with stable squads have a cohesion advantage over new appointments)

### 3. Squad and selection

- Likely starting XI and formation
- Key players and what they do tactically (not just "he's good" — how does he function in this system)
- Notable absences: injuries, suspensions, fitness doubts, minute management
- Squad depth: where is the drop-off sharpest if a starter goes down?
- Age profile: is this a young squad building for the future or a veteran window-closing group? This affects motivation and risk tolerance.

### 4. Attacking profile

Search for real per-90 or per-match numbers where possible.

- Goals scored, xG, xG per match (tournament + recent 12 months)
- Shot volume: total shots and shots on target per match
- Shot quality: do they take many low-percentage shots from distance, or work the ball into the box?
- xG open play vs xG from set pieces — how dependent are they on dead balls?
- Chance creation: who creates? Through what channels (wide crosses, through balls, individual dribbles)?
- Finishing efficiency: are they converting above or below xG? (overperformance is unsustainable; underperformance suggests unlucky results)

### 5. Defensive profile

- Goals conceded, xGA, xGA per match
- Defensive structure: high line or deep block? Do they compress space centrally or protect the flanks?
- Vulnerability patterns: where do they concede from? (Crosses, transitions, set pieces, individual errors)
- Pressing effectiveness: do they win the ball high, or does their press get bypassed?
- Clean sheet rate and context (against strong or weak opponents?)

### 6. Set pieces

- Corner frequency: corners won and conceded per match
- Corner delivery style: inswingers, outswingers, short routines?
- Dangerous from corners? (goals or xG from corner situations)
- Free kick threats: anyone with a direct free kick goal threat?
- Penalty record: who takes them, conversion rate, do they win penalties frequently?
- Set piece defensive record: do they concede from dead balls?

### 7. Discipline and cards

- Yellow and red cards per match in tournament and qualifying
- Card-prone players: who picks up yellows consistently?
- Foul frequency: fouls committed and fouls drawn per match
- Style context: are cards tactical (professional fouls to stop counters) or reckless?
- **Important**: low card counts in qualifying don't necessarily mean a disciplined team — it can mean they played weaker opponents who rarely threatened transitions. Check the quality of opposition faced.

### 8. Match context weighting

This is critical for international football. Not all matches carry equal predictive value.

- **World Cup matches** (this tournament): highest weight. Most reliable indicator of current level.
- **Continental tournament matches** (Euros, Copa, AFCON, Asian Cup — last cycle): high weight. Competitive intensity, similar stakes.
- **World Cup qualifiers**: high weight, but context matters. CONCACAF qualifying is a different animal than UEFA qualifying. Some confederations have massive quality gaps between top and bottom teams — a 5-0 against a minnow tells you less than a 1-0 against a peer.
- **UEFA Nations League**: moderate-high weight. Taken seriously by most teams, but some rotate.
- **Friendlies**: low weight. Teams rotate heavily, experiment tactically, and rarely play at full intensity. A friendly result (win or loss) is weak evidence. Friendly *patterns* across multiple matches can reveal something (e.g. a team consistently conceding from set pieces across 5 friendlies), but any single friendly is noise. Nate Silver's PELE model weights friendlies at roughly 1/3 to 1/4 the value of World Cup matches.
- **Pre-tournament friendlies** (last 2–3 before the WC): slightly higher than normal friendlies because squads are usually full strength, but still below competitive matches.

When citing form or statistics, always note the competition context. "4 wins in their last 5" means nothing without knowing if those were against San Marino in qualifying or France in the Nations League.

### 9. Historical tournament pedigree

- World Cup history: titles, best finishes, how deep they typically go
- Recent tournament performances (last 2–3 major tournaments)
- Do they historically perform above or below expectations at World Cups?
- Knockout stage record: do they handle pressure or collapse? (Penalty shootout record if relevant)
- Tournament experience in the current squad — how many players have been to a World Cup before?

### 10. Environmental and logistical factors

- Where are they based for this World Cup? Travel distances between group venues.
- Climate adaptation: are they used to the heat/humidity of US summer venues, or the altitude of Mexican venues?
- Fan support: is there a significant diaspora presence in their group-stage cities?
- Time zone adjustment if traveling from a distant confederation

---

## Quality checks before finishing

- Did you cite competition context for every form/stat claim? (Not just "3 clean sheets in 5 games" but "3 clean sheets in 5 World Cup qualifiers against X, Y, Z")
- Did you flag where sample size is thin?
- Did you distinguish between sustainable performance (process stats like xG, shot volume, pressing numbers) and outcome stats (actual goals, actual clean sheets) that carry more variance?
- Did you weight friendlies appropriately low?

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
