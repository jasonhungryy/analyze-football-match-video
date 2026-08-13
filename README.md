# Analyze Football Match Video

A Codex skill for automatic, evidence-based association-football player review. Give it a match link plus enough information to identify the player; it can find the player's minutes, log every visible reception and meaningful action, diagnose improvement opportunities, and compare the performance with previous matches. Self-written notes and timestamps are optional.

The skill is designed for player development rather than highlight generation. It separates what is visible from what is inferred, records confidence and video timestamps, and supports longitudinal comparison across matches.

## What it does

- Runs a first-use player interview covering age group, position, physical profile, match format and intensity, perceived problems, and development goals.
- Builds a private longitudinal profile, then uses it to understand the player's role and priorities in future reviews.
- Handles known or initially unknown playing intervals and normalizes mixed timestamp formats.
- Re-identifies the target player after substitutions, halftime, camera cuts, and kit changes.
- Reviews the player's minutes continuously and creates a timestamped ledger of every identifiable reception plus other meaningful actions.
- Reviews optional user-marked moments without requiring the user to pre-analyze the match.
- Separates decision quality, technical execution, tactical effect, and physical context.
- Uses position-specific lenses for fullbacks, centre-backs, midfielders, wingers, strikers, and goalkeepers.
- Produces an evidence table, strengths, development priorities, three match-day cues, and a short training plan.
- Compares each match with the historical baseline: improvement, regression, resolved issues, recurring issues, and the current top priority.

## Install

Copy the skill directory into your Codex skills folder:

```bash
cp -R skills/analyze-football-match-video ~/.codex/skills/
```

Or install the repository path with your preferred Codex skill installer.

## Personal setup

On first use, the skill asks one grouped set of onboarding questions and creates a private profile with your permission. You can also initialize the file manually from the included template:

```bash
python3 skills/analyze-football-match-video/scripts/init_player_profile.py
```

This creates `skills/analyze-football-match-video/references/player-profile.md`. That path is ignored by Git so match links, injuries, identifiers, and personal baselines are not accidentally committed.

## Example requests

- “Use `$analyze-football-match-video` to review me. Here is the Veo link; I am number 10 on the blue team.”
- “Analyze every one of my receptions and tell me which possessions I should handle differently. I do not have timestamps.”
- “Compare this match with my previous games: what improved, what regressed, and which old problem is still unresolved?”

## Privacy and limitations

Only analyze footage the user is permitted to access. Do not change sharing settings, upload or republish match footage, expose private links, or infer sensitive identity details. Video review is observational coaching, not medical diagnosis. See the skill references for the full evidence and privacy rules.

## Development

Run the checks from the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/analyze-football-match-video
```

## License

[MIT](LICENSE)
