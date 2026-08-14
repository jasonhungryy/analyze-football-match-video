# Full-match coverage audit

Use this workflow for every full-match or complete-playing-interval review. Its purpose is to prevent a sparse frame sheet, highlight detector, ball-action candidate list, or user-provided marker list from silently becoming the review boundary.

## Two independent passes

Split every confirmed playing interval into blocks of no more than 60 seconds. Create a manifest with `scripts/coverage_audit.py` before detailed coding.

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

Candidate clips, contact sheets, tracking models, audio cues, and highlight metadata may help navigation. They never authorize skipping the continuous block review.

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

## User-marker reconciliation and miss feedback loop

User notes remain hypotheses, not labels to copy. After the blind ledger is complete, review every user marker from at least six seconds before to six seconds after and classify it as supported, partly supported, contradicted, or not judgeable. Link it to the relevant ledger event.

If a supported or partly supported user marker was absent from the blind ledger:

1. Add or correct the event.
2. Record why it was missed: identity loss, sparse sampling, ball-only attention, phase ended too early, event taxonomy omission, or misclassification.
3. Re-open the adjacent coverage block.
4. Re-scan the entire playing time for the same event family. A missed header triggers a full aerial rescan; a missed no-touch recovery triggers a full transition rescan; a missed second action triggers a full post-contact rescan.
5. Record the re-scan in `miss_root_cause_audits` and do not close the manifest until it is marked reviewed.

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

Validation fails when a block is pending, a visible block has neither events nor a quiet reason, an event lacks taxonomy/source fields, a marker is unreconciled, or a missed-event audit lacks the mandatory same-type re-scan.

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
