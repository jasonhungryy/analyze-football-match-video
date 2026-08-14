# Evidence and analysis rubric

## Complete player-involvement ledger

For a full-match individual review, continuously inspect every identified playing interval and create a chronological ledger of every visible, confidently attributable material sequence involving the player. This is the primary evidence table. Do not select only highlights, mistakes, touches, or receptions.

Include:

- On-ball actions and meaningful touches, whether controlled or uncontrolled.
- Defensive actions: pressing, delaying, duels, tackles, interceptions, blocks, clearances, recovery runs, tracking, marking, handovers, line movement, box protection, cover, and second-ball responsibility.
- Attacking and defensive transitions.
- Restarts taken, received, defended, or visibly prepared for.
- Meaningful attacking support, width, overlaps, underlaps, decoy runs, box runs, and rest-defence.
- Routine positioning when it directly shows the player's assignment, spacing, or response to the phase.

Merge a continuous passage into one sequence window while phase, role, and outcome remain substantially the same. Split it when any of those materially changes. A player merely being visible is not enough; the player's action or position must be directly relevant to the play.

| Field | What to record |
|---|---|
| Sequence number | Sequential within the match |
| Timestamp | Exact start and end of the material passage |
| Labels | One or more: on-ball, defending, attacking transition, defensive transition, restart, attacking off-ball, defensive positioning |
| Observation | Only what is visible |
| Decision | Appropriate, mixed, poor, or not judgeable |
| Execution | Effective, mixed, failed, or not judgeable |
| Effect | Immediate tactical consequence |
| Better option | Only when visibly supported; otherwise “not established” |
| Confidence | Separate identity and interpretation confidence |
| Source | User marker or blind scan |

At the end, report the total confirmed sequence windows, overlapping label counts, uncertain exclusions, and any footage ranges where completeness could not be established. Never add overlapping label counts and present the sum as a unique-event total.

## Complete reception subset

After the full player-involvement ledger, log every visible reception attributable to the player with adequate identity confidence. Do not select only highlights or mistakes. This subset supplements rather than replaces the main ledger.

Use these reception types:

- Teammate pass received.
- Restart received.
- Opponent ball won and controlled.
- Loose ball or rebound secured.
- Aerial ball intentionally controlled or redirected.

Do not count a clearance, deflection, block, or uncontrolled duel touch as a reception, but include it in the other-action ledger when meaningful.

Record:

| Field | What to record |
|---|---|
| Reception number | Sequential within the match |
| Timestamp | Start of control; add possession end when useful |
| Context | Zone, phase, pressure, nearby support |
| Before receiving | Scan, movement, body orientation when visible |
| First touch | Direction, security, and purpose |
| Action sequence | Pass, carry, dribble, cross, shot, retention, loss, or foul won |
| Outcome | Immediate result without outcome bias |
| Better option | Only when visibly supported; otherwise “not established” |
| Coaching note | Keep, improve, or neutral plus one concise reason |
| Confidence | Separate identity and interpretation confidence |

At the end, report:

- Total confirmed receptions.
- Receptions with a useful forward action, safe retention, and loss, while explaining that these categories are contextual rather than a universal score.
- Possible receptions excluded because identity or contact was uncertain.
- Any footage ranges where completeness could not be established.

## Compact non-reception fields

When a compact clip review does not justify the full table, use these minimum fields for a non-reception action. Full-match reviews must use the complete player-involvement ledger above.

| Field | What to record |
|---|---|
| Timestamp | Video time or clip name plus local time |
| Source | User marker or blind scan |
| Phase | Buildup, attack, defensive block, transition, or set piece |
| Observation | Only what is visible |
| Decision | Appropriate, mixed, poor, or not judgeable |
| Execution | Effective, mixed, failed, or not judgeable |
| Effect | Immediate tactical consequence |
| Identity confidence | High, medium, or low |
| Interpretation confidence | High, medium, or low |

## Confidence standard

- **High:** target identity and action are clear; relevant context is visible.
- **Medium:** identity is likely or one important contextual element is off-camera.
- **Low:** identity, touch, opponent pressure, or consequence is ambiguous.

Do not use low-confidence events as the main support for a development priority.

## Decision versus execution

Use this matrix to avoid outcome bias:

| Decision | Execution | Interpretation |
|---|---|---|
| Good | Good | Reinforce the behaviour |
| Good | Poor | Train the technique without discouraging the choice |
| Poor | Good | Successful outcome may hide a risky mechanism |
| Poor | Poor | Diagnose the earliest controllable cause |

## Coding pre-reception scanning

Use a consistent observation window so “scan more” does not become a vague judgment:

1. Review up to six seconds before the reception, or from the moment the player and relevant space become visible.
2. Code **confirmed scan** only when a head, shoulder, or whole-body turn is visibly directed away from the ball toward useful space, opponents, or teammates, followed by behaviour consistent with receiving information.
3. Code **possible scan** when a movement may gather information but the view is too distant or brief to confirm direction.
4. Code **not visible** when the player or pre-reception period is off-camera, obstructed, or too short.
5. Code **no visible scan in an adequate window** only when at least roughly three seconds of clear pre-reception behaviour is visible and the player does not look away from the ball despite relevant uncertainty.

Do not count head movement mechanically. Evaluate whether the player could gather useful information, retain it, and use it in body orientation or the next action. Never treat “not visible” as “did not scan.”

## Common analysis dimensions

### Before receiving

- Shoulder checks and information gathered.
- Body orientation and access to forward options.
- Distance and angle from teammates and opponents.
- Recognition of pressure and next action.

### In possession

- First touch direction and security.
- Speed and appropriateness of the decision.
- Pass, carry, dribble, cross, or shot execution.
- Ability to disguise, combine, switch, or retain.
- Rest-defence consequences of the action.

### Out of possession

- Starting position relative to ball, opponent, teammates, and goal.
- Pressing trigger, angle, speed, and braking distance.
- Cover shadow and protection of central space.
- Tracking, handover, recovery line, and box positioning.
- Communication visible or audible in the footage.

### Transitions

- First reaction after possession changes.
- Counterpress, delay, recovery, or forward run choice.
- Recognition of numerical advantage or danger.
- Sprint direction and connection to teammates.

### Set pieces

- Assignment, starting position, scanning, contact, second-ball reaction, and exit.

## Repeated mechanisms

Treat a mechanism as recurring only when supported by at least two independent events, preferably across different phases or periods. A single high-cost event may still be a priority, but label it as a high-impact incident rather than a repeated trait.

One short or low-opportunity clip set may show an **initial improvement signal**, but not a stable trend. Prefer at least two comparable evidence-backed reviews before describing an improvement as established.

Rank priorities using:

1. Frequency.
2. Tactical cost or opportunity value.
3. Confidence of evidence.
4. Trainability.
5. Relevance to the player's role.

## Blind-scan minimum

For a full-match request, inspect all identified playing intervals continuously for every material player-involvement sequence and for the complete reception subset. Include quiet defensive and off-ball passages; they often reveal positioning, scanning, marking, and line discipline better than highlights.

Follow `coverage-audit.md`: divide playing time into blocks of at most 60 seconds, complete a continuous identity pass and a separate action/responsibility pass, and validate the manifest before using completeness language. Sparse screenshots, candidate windows, ball-contact detections, or user markers may assist navigation but may not determine which time ranges are reviewed.

Before closing each block, explicitly check for no-touch defending, aerial first points, transition reactions, weak-side/back-post responsibility, pre-reception body orientation, and the action immediately after an apparent clearance, header, tackle, or regain.

When a reconciled user marker exposes a blind-ledger miss, do not patch only that timestamp. Classify the miss, re-open the adjacent block, and rescan all playing intervals for the same event family. The coverage manifest must record that rescan as reviewed.

Representative sampling is acceptable only when the user asks for a quick review, the source contains clips rather than the full performance, or technical limitations prevent continuous coverage. Label the result accordingly.

## Training translation

For every priority, specify:

- The repeatable mechanism.
- One short match-day cue.
- A representative practice task.
- A constraint that recreates the decision.
- A measurable indicator for the next match.

Prefer observable measures such as “shoulder check before 7 of 10 receptions” over vague goals such as “improve awareness.”
