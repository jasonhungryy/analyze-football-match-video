# Longitudinal player development

Use this reference whenever a player has approved local development tracking. Compare automatically after each analyzed match and update the private profile after the report.

## Storage rule

Store personal context in `references/player-profile.md`. Create it from `assets/player-profile-template.md` with `scripts/init_player_profile.py`. The public repository ignores the private destination.

Do not store:

- Authentication tokens or signed share parameters.
- Unnecessary legal names or details about other players.
- Medical diagnoses inferred from video.
- Private match links when a neutral match label is sufficient.

## First-use baseline

Create the initial profile from the onboarding interview, not from assumptions about one match. Treat perceived strengths and problems as the player's hypotheses. The first video review then confirms, revises, or leaves them open.

## Post-match update rule

Append a compact match entry; do not overwrite earlier evidence. Change the current baseline only when the new evidence is sufficiently broad and confident.

For each mechanism, track:

- Representative positive and negative evidence.
- Role and tactical context.
- Coverage quality and playing minutes.
- Current direction: improving, stable, regressing, or inconclusive.
- The cue and training task currently being tested.
- A concrete question for the next review.

Use these issue states:

- **New:** first credible repeated evidence.
- **Recurring:** repeated again without meaningful improvement.
- **Improving:** behaviour is better but not yet stable.
- **Resolved for now:** absent or handled well across sufficient relevant opportunities.
- **Regressed:** previously stronger behaviour deteriorated.
- **Inconclusive:** insufficient comparable opportunity or coverage.

## Avoid false trends

Do not treat raw counts as directly comparable when playing time, position, opponent strength, camera coverage, or team role changed. Prefer rate, opportunity quality, and mechanism consistency.

If an earlier entry contains only a coarse summary and lacks representative timestamps or opportunity context, classify the comparison as inconclusive rather than manufacturing precision. The older note may still guide what to inspect in the current match.

Use at least two reasonably comparable reviews before calling a durable trend. A single match may mark an issue “improving” or “resolved for now” when the opportunity set is strong, but should rarely redefine the player's stable profile.

## Baseline summary

Keep the active summary short:

- Two or three strengths to preserve.
- Two or three priority mechanisms.
- Exactly three current match-day cues.
- Current training focus and success measure.
- Date and evidence scope of the last update.

## Automatic comparison sequence

After each match:

1. Compare every active issue with current relevant opportunities.
2. Identify positive change before searching only for mistakes.
3. Detect regression in previously stable strengths or resolved issues.
4. Add genuinely new repeated mechanisms.
5. Select one top priority using frequency, cost, confidence, role relevance, and trainability.
6. Retain at most two secondary priorities.
7. Update exactly three match-day cues.
8. Append the match record without deleting the earlier baseline.

Do not append an attempted review when the video was inaccessible, identity could not be resolved, or no usable football evidence was analyzed.
