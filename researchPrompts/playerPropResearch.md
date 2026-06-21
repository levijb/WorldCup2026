# Player Prop Research Template

## How to use

Paste this into a Claude chat with a player name and their upcoming match. Example prompt: "Run a full player prop profile on Bruno Fernandes for Portugal vs DR Congo using playerPropResearch.md." This template produces a statistical and role-based profile of an individual player in the context of a specific match. It's research-first with a prop-betting lens — the output should tell you whether a player's prop lines are likely to hit, not just whether the player is "good."

---

## Instructions

You are profiling a single player's statistical tendencies, tactical role, and matchup context to assess expected output in a specific match. Use live web search for all current data. The core question for every stat is: **what is this player's baseline rate, and does this specific matchup push it higher or lower than usual?**

### Tone and format

- Dense and numerical. Lead with rates, not narratives.
- Every claim needs a number or a sourced observation. "He shoots a lot" is useless. "He averages 3.2 shots per 90 across qualifying, 2.8 in this tournament" is useful.
- Flag sample size on everything. 2 tournament matches is not a stable rate.

---

## Research sections (complete all)

### 1. Player identity and role

- Position, age, club team, minutes played in this tournament
- Tactical role in this specific national team system — not his club role, which may differ significantly
  - Example: a player who plays as a #10 at his club might operate as a deeper #8 for his national team, which changes his shot and chance creation volume entirely
- Is he a guaranteed starter? Any rotation risk or minute-management concern?
  - Minute management is especially relevant for older stars (Ronaldo, Messi, Modric) in comfortable group-stage wins where the manager may sub them at 60–65 minutes. A sub at 60' means roughly 33% fewer counting stats than a full 90.
- Set piece duties: does he take corners, free kicks, penalties? This is a massive prop inflator.
  - If the primary set piece taker is injured/suspended, do duties shift to this player?

### 2. Shot volume profile

This is the most important section for shots and SOT props.

- **Shots per 90**: tournament rate, qualifying rate, last 12 months for national team, club rate for context
- **Shots on target per 90**: same breakdown
- **SOT/shot ratio**: what percentage of his shots hit the frame? A player who takes 4 shots but only puts 1 on target is a very different prop profile than one who takes 2 shots and puts 1.5 on target.
- **Shot location**: does he shoot from distance (lower xG per shot, lower SOT rate) or primarily from inside the box?
- **Shot type**: right foot, left foot, headers. Does the matchup favor one type? (e.g. a team that concedes from crosses creates headed shot opportunities)

**Critical distinction — shot-volume players vs service players:**
- Shot-volume players (strikers, attacking midfielders who shoot frequently): evaluate on shots/SOT props
- Service players (creative midfielders, wing-backs who create but rarely shoot): evaluate on assist props, chances created, crosses
- Getting this wrong is a common error. Bruno Fernandes at 0.4 SOT/90 for Portugal is a service player in that system despite being a prolific shooter at club level. His value is in "to assist" or "chances created" markets, not "shots on target 1+."

### 3. Goal threat profile

- **Goals per 90**: tournament, qualifying, last 12 months (national team)
- **xG per 90**: is he overperforming or underperforming xG? Overperformance is partially skill (elite finishers like Haaland) but partially luck and will regress.
- **Non-penalty xG**: strip out penalties to see his true open-play/set-piece goal threat
- **Anytime goalscorer context**: goalscorer props are high variance. Even a player averaging 0.5 xG per 90 (very good) only scores in roughly 35–40% of matches. This market rewards patience, not confidence.
- **Penalty likelihood**: does his team win penalties frequently? Is he the designated taker?

### 4. Chance creation profile

- **Key passes per 90** (passes leading to a shot)
- **xA per 90** (expected assists): a player with high xA and low actual assists is creating real chances that teammates are missing. The underlying creative output is strong.
- **Assist rate**: how often do his key passes actually convert?
- **Chance creation channel**: through balls, crosses, set piece deliveries, combination play?
- **Assist prop context**: assists are even higher variance than goals because they require a teammate to finish. A player can create 3 clear chances and get 0 assists if teammates miss. xA is a better predictor than actual assists.

### 5. Discipline profile

- **Yellow cards per 90**: tournament, qualifying, club
- **Fouls committed per 90**: the base rate that drives cards
- **Card context**: are his cards tactical (professional fouls stopping counters, time-wasting) or reckless (bad tackles, dissent)?
- **Position-specific card tendency**: defensive midfielders and aggressive full-backs have structurally higher card rates than wingers or center-backs
- **Referee factor**: if the referee is assigned and known, cross-reference their cards-per-match average. A referee averaging 5+ yellows per match vs one averaging 3 changes the landscape significantly.
- **Matchup card context**: is this a physical, combative matchup (CONCACAF-style, high-pressing clash) or a technical, possession-dominant affair? Physical matches produce more fouls and more cards.

### 6. Matchup-specific adjustment

This is where you move from baseline rates to match-specific projections.

- **Opponent defensive style**: do they sit deep (fewer shots from distance against a packed box, but more corners from sustained pressure) or play a high line (more space in behind, more transition chances, potentially more shots)?
- **Territorial dominance expectation**: if his team is expected to dominate possession and territory, his shot/corner/chance creation numbers get inflated. If his team is the underdog expected to sit deep, they're deflated.
- **Opponent quality adjustment**: a player averaging 3 shots per 90 in qualifying against minnows will not replicate that against a World Cup quarterfinal-caliber defense.
- **Game state prediction**: if his team is heavy favorite and likely to lead early, does the manager sub him early? Does the team ease off in the second half, suppressing late-game counting stats?
- **Specific defensive weakness**: does the opponent concede in a way that maps onto this player's strengths? (e.g. opponent concedes from crosses + this player is the primary crosser = assist/chance creation upside)

### 7. Minutes and role certainty

- **Expected minutes**: 90? 75? 60? This is the single biggest factor for counting stat props.
- **Substitution risk**: what does the manager's sub pattern look like? Does he pull this player regularly at a certain minute mark?
- **If subbed at 60 minutes**: a player needs roughly 50% higher per-90 rates to hit the same counting stat thresholds in 60 minutes that he'd hit in 90. A "shots 2+" prop for a player averaging 2.5 shots per 90 is borderline at 90 minutes and negative expected value at 60 minutes.
- **Tactical role change risk**: might the manager shift formation mid-game in a way that changes this player's output? (e.g. going from a 4-3-3 to a 5-4-1 to protect a lead moves an attacking midfielder deeper)

### 8. Saves and keeper props (if applicable)

Only relevant if profiling a goalkeeper.

- **Saves per 90**: tournament and qualifying rate
- **Shots faced per 90**: the denominator that drives save totals
- **Opponent shot volume**: how many shots does the other team generate? This is the primary driver of save props.
- **Save percentage**: is the keeper overperforming (saving more than expected from shot quality faced)?
- **xGOT context**: expected goals on target tells you the quality of shots faced, not just the volume
- **Saves-over caution**: keeper save props have enormous variance. A keeper facing 5 shots might save 2 or might save 5 depending on shot quality and placement. The underlying rate is noisy even across a full qualifying campaign. Be very cautious with saves props unless the shot volume is clearly extreme.

---

## Output format

After completing all sections, end with a **Prop Summary Table** that looks like this:

| Prop category | Baseline rate | Matchup adjustment | Direction |
|---|---|---|---|
| Shots 2+ | 2.8/90 qualifying, 2.3/90 tournament | Opponent sits deep → more speculative shots | Slightly above baseline |
| SOT 1+ | 1.1/90 qualifying | Low SOT ratio + packed box → harder | At or below baseline |
| Anytime scorer | 0.35 xG/90 | Low-block reduces quality chances | Below baseline |
| To assist | 0.22 xA/90 | Set piece deliveries + crossing opportunities | Above baseline |
| Yellow card | 0.18/90 qualifying | Non-physical matchup, lenient referee | Below baseline |

This table is the handoff to the betting strategy workflow. It tells you which props have matchup-supported cases and which are baseline or worse.

---

## Quality checks before finishing

- Did you distinguish between club stats and national team stats? They can diverge significantly.
- Did you separate tournament sample from qualifying/friendly sample and weight appropriately?
- Did you identify the player's tactical role in *this specific team system*, not just his general position?
- Did you account for minutes risk (sub patterns, minute management)?
- Did you check if the player's club shooting/creating tendencies transfer to his national team role, or if the role is different enough to change the baseline?
- Did you flag the shot-volume vs service-player distinction if relevant?
