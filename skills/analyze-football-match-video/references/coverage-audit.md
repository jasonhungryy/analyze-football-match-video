# Full-match coverage audit

Use this workflow for every full-match or complete-playing-interval review. Its purpose is to prevent a sparse frame sheet, highlight detector, ball-action candidate list, or user-provided marker list from silently becoming the review boundary.

## Two independent passes

Split every confirmed playing interval into blocks of no more than 30 seconds. Create a manifest with `scripts/coverage_audit.py` before detailed coding. The shorter block is a completeness checkpoint, not an event quota.

### Pass 1 — continuous identity track

Follow the player continuously through every block. Record visibility, identity status, position changes, camera cuts, and where the identity is lost or reacquired. This pass answers “where is the player?” It does not depend on whether the ball reaches the player.

### Pass 2 — action and responsibility track

Review every block again for actions and responsibilities. This pass answers “what material role did the player have?” Check every taxonomy family:

- on-ball action or attempted control;
- direct defending, including delay, press, duel, tackle, block, interception, and clearance;
- aerial first point and the next action after landing;
- defensive and attacking transitions, including the first three steps;
- restart taken, received, defended, or prepared for;
- attacking support and rest-defence;
- defensive positioning, weak-side protection, marking, cover, handover, and second-ball responsibility.

For a visible block with no material sequence, write a concrete `quiet_reason`. “Nothing happened” is not enough; use wording such as “player remained weak-side and the phase never entered their responsibility zone.”

Every block must also contain one or more `coverage_dispositions`: `confirmed_direct_action`, `meaningful_off_ball`, `visible_no_material_involvement`, `not_visible_or_occluded`, `identity_ambiguous`, `confirmed_confuser`, or `dead_ball_or_stoppage`. The internal manifest must retain all blocks even when the readable coaching report hides quiet blocks. No unclassified block may be treated as reviewed.

Candidate clips, contact sheets, tracking models, audio cues, and highlight metadata may help navigation. They never authorize skipping the continuous block review.

### Multi-hypothesis identity rule

Do not collapse uncertain identity to one tracker path. In every ambiguous block, retain all plausible target candidates near the ball, the target's lane, or the target's defensive responsibility. Include candidates that match any strong combination of clothing, footwear, build, side, position, motion continuity, and appearance re-identification. A single cue may propose a candidate but may not reject one.

When the chosen path jumps to a teammate, reopen the interval from the last confident identity anchor through the next anchor and review the other hypotheses. Record each hypothesis in `candidate_dispositions`. An unresolved candidate is a coverage limit and prevents completeness language; it must not silently disappear from the ledger.

### Identity-reference contamination rule

When crop similarity, appearance matching, or automated tracking is used, keep an `identity_reference_audit` in the manifest:

- every positive anchor must be checked in the full frame and list at least two visible identity cues;
- keep easily confused teammates as negative references, including their number, socks, boots, or other disqualifying cues when visible;
- never promote an old report timestamp or high similarity score to a positive anchor without manual full-frame confirmation;
- if one anchor is rejected as another player, invalidate every result derived from that gallery and rebuild the full playing interval from clean anchors;
- record the rejected anchor, contamination reason, and completed downstream rebuild. Merely deleting the crop does not repair prior candidate rankings or quiet-block conclusions.

Do not mark the identity audit reviewed with a generic note. Name the confirmed cues and, when no appearance matching was used, state the manual continuity method instead.

### Temporal-resolution gate

“Continuous review” describes coverage, not merely the fact that every minute has a sheet. When direct video playback is unavailable and still frames are used as the viewing substrate:

- sample visible playing time at intervals of **0.5 seconds or less** for the baseline identity/action passes;
- re-open every possible ball arrival, duel, defensive responsibility, restart, or possession change at **0.25 seconds or less**, from the natural phase beginning through at least the next action;
- inspect retained receptions, contacts, and disputed outcomes at the source's highest practical resolution before grading them;
- never mark a block reviewed from a sparse navigation sheet whose interval can hide a touch, tackle, change of direction, or second action.

Record the baseline and dense-review intervals in the audit notes. If compute, access, or image limits prevent these thresholds, name the affected range as coverage-limited rather than silently reducing temporal resolution.

## Trigger expansion

Whenever one of these triggers appears, inspect at least six seconds before and six seconds after it, or to the natural beginning and end of the phase:

- the ball enters the player's lane, zone, or marking responsibility;
- a teammate prepares a pass toward or past the player;
- possession changes;
- an opponent begins a run through the player's channel;
- a cross, long ball, or aerial ball approaches the player's unit;
- the player clears, heads, tackles, regains, or disrupts the first action;
- a restart begins near the player.

Do not stop coding at the first touch. Explicitly inspect the next action. A good clearance followed by a poor pass, a missed header followed by a recovery, and a successful tackle followed by a turnover are mixed sequences, not single-outcome highlights.

## Negative-evidence check before closing a block

Before marking the action pass reviewed, ask:

1. Did the player defend without touching the ball?
2. Was there an aerial first point or second-ball responsibility?
3. Did a possession change require recovery, counterpress, or rest-defence?
4. Did the player's body orientation or scan change a reception option?
5. Did the player have a second action after the apparent outcome?
6. Was weak-side or back-post positioning tactically material?

Only then record events or a quiet reason.

## Mandatory category rescans

After the two full passes, perform three independent whole-interval rescans before finalizing the ledger:

1. **Ball-arrival and reception rescan:** every teammate pass toward the player, loose ball, rebound, aerial drop, restart receipt, attempted control, and immediate continuation.
2. **Defensive-responsibility rescan:** every direct duel plus no-touch delay, cover, marking, recovery, weak-side protection, line movement, aerial responsibility, and second-ball responsibility.
3. **Post-action rescan:** at least the next 5–10 seconds after every touch, header, clearance, tackle, regain, disruption, or initial failed action.

Keep a candidate disposition log: `retained`, `merged`, `rejected_other_player`, `rejected_ordinary_visibility`, or `unresolved`. Set `candidate_generation_used: true` whenever trackers, detectors, similarity rankings, or machine-generated windows were used. A generated candidate list is not complete until every candidate has a disposition. `unresolved` is allowed only as an explicit coverage limitation and forces `complete_eligible: false`.

As a sanity check, an unusually sparse ledger over a long, visible playing interval must trigger an undercount audit. Do not impose a minimum event quota or invent marginal events. Instead, verify player identity, side/direction of play, reception detection, no-touch defending, restarts, and phase continuation, and explain why the interval is genuinely quiet or coverage-limited.

## User-marker reconciliation and miss feedback loop

User notes remain hypotheses, not labels to copy. After the blind ledger is complete, review every user marker from at least six seconds before to six seconds after and classify it as supported, partly supported, contradicted, or not judgeable. Link it to the relevant ledger event.

If a supported or partly supported user marker was absent from the blind ledger:

1. Add or correct the event.
2. Record why it was missed: identity loss, sparse sampling, ball-only attention, phase ended too early, event taxonomy omission, or misclassification.
3. Re-open the adjacent coverage block.
4. Re-scan the entire playing time for the same event family. A missed header triggers a full aerial rescan; a missed no-touch recovery triggers a full transition rescan; a missed second action triggers a full post-contact rescan.
5. Record the re-scan in `miss_root_cause_audits` and do not close the manifest until it is marked reviewed.

If the player reports several missed involvements or says the analysis followed the wrong person, supersede the entire prior completeness claim. Set `revision_audit.prior_report_challenged` to true, name the superseded report, and rebuild every playing-time block. Reconcile every previously retained event; do not retain an old row merely because it was already published.

## Manifest commands

Create a manifest:

```bash
python scripts/coverage_audit.py init \
  --interval 25:50-40:40 \
  --interval 49:20-89:45 \
  --marker '27:11|did not scan receiver' \
  --output work/coverage.json
```

After completing both passes and marker reconciliation, validate it:

```bash
python scripts/coverage_audit.py validate work/coverage.json
```

Validation fails when a block is pending, a block lacks a coverage disposition, a visible block has neither events nor a quiet reason, an event lacks taxonomy/source fields, a marker is unreconciled, a missed-event audit lacks the mandatory same-type re-scan, temporal-resolution metadata is insufficient, any category rescan is pending, a generated candidate has no disposition, the identity-reference audit is incomplete, a challenged prior report was only patched instead of rebuilt, or the undercount audit is incomplete.

For workflows using extracted stills, set `review_substrate.mode` to `extracted_stills`, record `baseline_step_seconds` and `candidate_step_seconds`, and mark `source_resolution_checks` reviewed only after retained/disputed actions were checked at the highest practical source resolution. Direct playback still requires source-resolution checks and all category rescans.

Complete the undercount audit for every full-match ledger. Explicitly recheck identity and direction of play, ball arrivals/receptions, no-touch defending, restarts/aerials, transitions/weak-side responsibility, and post-action continuations. Add a concrete notes summary; a bare “reviewed” is not enough.

`complete_eligible: true` means the workflow has no pending block and no recorded visibility/identity gap. It does not mean machine-perfect or official-data completeness. When `complete_eligible` is false, report the affected ranges and call the result coverage-limited.

## Reporting the audit

State:

- playing intervals and block size;
- reviewed blocks over total blocks;
- blind-ledger event total;
- number of user markers and how many added or corrected blind-ledger events;
- identity/visibility gaps;
- any same-type full-match rescans triggered by misses.

Never use “complete,” “all,” or “every” for a full-match ledger when the manifest has pending blocks, coverage gaps, or only candidate-window review.
