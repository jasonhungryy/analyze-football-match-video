---
name: analyze-football-match-video
description: Automatically analyze an individual association-football player's full match or clips from Veo, YouTube, Google Drive, similar web links, or uploaded video. Use when the user provides a match and player identity cues and wants every visible reception timestamped, on-ball and off-ball actions reviewed, better choices explained, a first-use player profile created, or progress and regression compared across matches. User-written summaries and timestamps are optional. Support all positions, public or signed-in video players, initially unknown playing intervals, and Chinese or English reports.
---

# Analyze Football Match Video

Produce an automatic, evidence-based coaching review of a target player's football performance. The normal input is only a video link or file plus enough cues to identify the player. Do not require the player to summarize the match or mark timestamps first. Treat the video as primary evidence, optional user notes as hypotheses to verify, and the private player profile as development context rather than proof.

## Load only the references needed

- Read `references/video-sources.md` when opening or navigating footage.
- Read `references/player-onboarding.md` when no usable private player profile exists.
- Read `references/analysis-rubric.md` before evaluating actions or writing the report.
- Read `references/position-lenses.md` for the target player's position.
- Read `references/report-templates.md` when producing the final report.
- Read `references/privacy-and-safety.md` whenever the source, identity, injury context, or sharing status is sensitive.
- Read `references/longitudinal-profile.md` whenever a stored baseline or earlier match history exists.
- If `references/player-profile.md` exists, treat it as private user-provided context. Never assume it exists and never expose its contents unless necessary for the user's request.

## 1. Onboard the player on first use

Check for `references/player-profile.md`. If no usable profile exists, or an older profile lacks essential onboarding fields, pause the video review and follow `references/player-onboarding.md`. Preserve existing history and ask only for missing essentials when upgrading an older profile.

Ask one grouped set of questions covering:

- Age or age group, dominant foot, and football experience.
- Primary and secondary positions, preferred side, and coach instructions.
- Self-assessed short speed, recovery speed, endurance, and strength.
- Perceived strengths, problems, development goal, and current priority.
- Match format, competition level, intensity, duration, substitution rules, and team style.
- Optional pain, injury, fatigue, or workload context.
- Permission to store the profile locally and update it after future matches.

Summarize the answers into a player model, invite corrections, and continue in the same turn without requiring a second confirmation round. When local storage is approved, create the private profile and use it in this review. If answers are incomplete, mark them unknown and continue rather than repeating the full questionnaire. Do not ask the user to identify timestamps or analyze their own actions.

## 2. Establish the match input

Extract or infer the following before detailed analysis:

- Video source and whether it is accessible.
- Target player cues: team colour, bib or number, position, side, footwear, body shape, or nearby teammates.
- Playing intervals in video time, when known. Accept `MM:SS`, `HH:MM:SS`, and dotted forms such as `39.24` when the meaning is clear.
- Whether timestamps refer to video time or match time. Record any offset instead of silently converting.
- Optional user-marked events and the claim attached to each event.
- Desired output language, depth, and comparison baseline.
- Physical context supplied by the user, such as fatigue or pain. Treat this as context, not a diagnosis.

After onboarding, the minimum intended input is a video plus team colour and shirt or bib number, or equivalent identity cues. Proceed without asking for a self-summary or timestamps. If playing intervals are unknown, inspect the footage to locate when the player enters, leaves, or changes role. If two players share the same number or the user already reports an identity collision, request two stable distinguishing cues before attribution; otherwise ask a concise question only when identity remains ambiguous after inspecting the footage.

Default to a complete review of every identified playing interval unless the user explicitly asks for a quick, sampled, or clip-only review.

Use `scripts/normalize_timestamps.py` when several intervals or mixed timestamp formats make manual normalization error-prone.

## 3. Access the footage without changing it

Use the most appropriate available viewer:

1. Open a public link in the in-app browser or equivalent web viewer.
2. Use the user's signed-in browser only when the source requires their existing session.
3. Inspect uploaded or local clips directly when available.
4. If access fails, request a permitted alternative such as an uploaded clip, exported segment, screenshots, or timestamped notes.

Do not alter sharing settings, download restricted footage without permission, upload or republish video, or claim to have watched frames that were not accessible.

## 4. Locate playing intervals and lock player identity

Scan the match to find the target player's appearances when intervals were not provided. Record the first confident appearance, substitutions, temporary absences, position changes, and final appearance. Do not assume the player was on the pitch merely because the match was in progress.

Build an identity hypothesis from multiple cues rather than one cue alone. Confirm it near the start of every playing interval using at least two stable cues when possible.

Re-lock identity after:

- Halftime or a change of ends.
- Substitutions or formation changes.
- Long camera cuts, zoom changes, or tracking loss.
- Bib, shirt, or positional changes.

Keep identity confidence separate from action confidence. If identity becomes uncertain, stop attributing actions until the player is reacquired. Report unresolved ambiguity explicitly.

## 5. Build a complete reception and action ledger

For a full-match request, review every identified playing interval continuously. Do not replace continuous review with representative sampling merely to save time. The primary deliverable is a chronological log of every visible, confidently attributable reception.

Count a reception when the player intentionally receives or gains control of a ball from a teammate, opponent, restart, rebound, or loose-ball recovery. For every reception, record:

- Exact video timestamp and, when useful, the end of the possession.
- How the ball arrived and the pressure level.
- Scanning and body orientation before receiving when visible.
- First touch and immediate decision.
- Complete action sequence: retain, pass, carry, dribble, cross, shoot, lose, or draw a foul.
- Outcome and immediate tactical effect.
- Whether a clearly better option existed, with the evidence for it.
- A short improvement suggestion when the choice or execution can improve.
- Identity and interpretation confidence.

Also log meaningful non-reception actions that affect the evaluation, including carries that start off-camera, duels, interceptions, tackles, pressing actions, recovery runs, marking, line-breaking runs, box actions, set pieces, and decisive off-ball positioning.

For every other material observation, record:

- Video timestamp or timestamp range.
- Phase of play and score or tactical context when visible.
- Observable action.
- Decision quality.
- Technical execution.
- Immediate tactical effect.
- Confidence in player identity and interpretation.
- Whether the event came from a user marker or blind scan.

Use direct visual language. Distinguish:

- **Observed:** visible in the footage.
- **Inferred:** a reasonable tactical interpretation.
- **Unknown:** not visible or not recoverable from the source.

Number receptions sequentially so the player can refer to them later. Report a total reception count and the number excluded because identity or ball contact was uncertain. Do not turn one event into a stable trait. Label a mechanism as repeated only when it appears across multiple independent events or phases.

## 6. Review the whole performance automatically

Continuously review all located playing intervals for the complete reception ledger. In parallel, review off-ball behaviour across these phases:

- In-possession buildup.
- Progression and final-third attacks.
- Defensive block and box defending.
- Defensive and attacking transitions.
- Set pieces when relevant.
- Off-ball movement away from the immediate camera focus.

If the user supplied markers or notes, verify them as an additional section; never make them a prerequisite. State whether each is supported, partly supported, contradicted, or not judgeable.

Disclose whether coverage was continuous, sampled, or restricted to clips. If technical limitations make complete review impossible, name the missing ranges and do not label the reception log complete.

## 7. Evaluate by mechanism and role

Apply the common rubric in `references/analysis-rubric.md`, then the role lens in `references/position-lenses.md`.

Separate the cause of an outcome:

- Was the decision appropriate?
- Was the technique adequate?
- Did positioning before the action create or remove options?
- Did scanning and body orientation affect the decision?
- Did physical context visibly constrain execution?
- What was the tactical consequence?

Prefer mechanisms the player can train, such as late shoulder checks, closed receiving shape, straight-line pressing, delayed recovery, poor cover-shadow angle, or rushed final action.

## 8. Compare with the player's history

When a private profile contains earlier matches, automatically compare the current evidence with the previous baseline. Do not wait for a separate comparison request. If the user remembers an old problem but no stored evidence exists, treat it as a hypothesis to inspect; do not claim improvement or regression without a comparable baseline.

For every active issue or development mechanism, classify the current state as:

- **Improved:** stronger or more consistent execution with comparable opportunities.
- **Resolved for now:** previously repeated problem is absent across sufficient relevant opportunities.
- **Stable:** similar behaviour and outcome.
- **Regressed:** previously stronger behaviour deteriorated in comparable contexts.
- **Inconclusive:** the role, opponent, coverage, or opportunity count is not comparable.

State what improved, what regressed, whether earlier problems were addressed, what new mechanism appeared, and which single priority now offers the highest value. Use opportunity quality and mechanism consistency rather than raw counts alone.

## 9. Synthesize without overstating

Rank findings by repeatability, tactical cost, and trainability. Preserve positive evidence as well as errors.

For each priority, connect:

`evidence → recurring mechanism → match cue → training task → progress measure`

Give exactly three short match-day cues unless the user requests another number. Keep them memorable enough to use during play.

Distinguish genuine change from differences in opponent, role, camera coverage, match state, or sample size.

## 10. Write the report

Use the structure in `references/report-templates.md`. Lead with the conclusion, then provide the event ledger and supporting reasoning.

Include:

1. Scope, identity confidence, and coverage limits.
2. Direct performance conclusion.
3. The complete numbered reception ledger with timestamps, actions, outcomes, and better options.
4. Other meaningful on-ball and off-ball evidence.
5. Optional user-note verification.
6. Strengths worth preserving.
7. Improvements, regressions, and status of previously tracked issues.
8. Two or three development priorities, clearly identifying the current top priority.
9. Exactly three match-day cues.
10. A short training plan with measurable indicators.
11. Uncertainty, excluded receptions, and inaccessible ranges.

Respond in the user's language. Use common football vocabulary and add an English term in parentheses only when it improves clarity.

## 11. Update the private baseline

If the player approved automatic local updates during onboarding, follow `references/longitudinal-profile.md` after delivering each completed evidence-backed review. Append the compact match record, update the issue tracker, and refresh the current priorities without erasing earlier evidence. Do not add a match entry when access failed, identity was unresolved, or no usable video evidence was reviewed. If profile storage is approved but automatic updates are not, ask before writing each match result. If profile storage is declined, do not create the file. Keep all personal data in `references/player-profile.md`, which is excluded from the public repository.
