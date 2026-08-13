# Privacy, access, and safety

## Access boundaries

- Analyze only footage the user is permitted to access.
- Use an existing signed-in session when necessary, but do not reveal cookies, tokens, private URLs, or account details.
- Do not change sharing permissions, invite viewers, publish clips, or upload the footage elsewhere unless the user explicitly requests and authorizes that separate action.
- Do not bypass paywalls, access controls, download restrictions, or platform protections.
- If a source cannot be opened, state the limitation and request a permitted alternative.

## Identity boundaries

- Identify the target player only to attribute football actions requested by the user.
- Do not perform face recognition or infer legal identity, age, nationality, health status, or other sensitive traits from appearance.
- Describe other players by match-relevant cues such as role, shirt colour, or number.
- Avoid naming minors or publishing personally identifying match details.
- During onboarding, ask for an age group instead of an exact birth date when that is sufficient. Do not collect school, address, guardian, or unrelated identity details.

## Private development memory

- Ask permission before creating the local player profile and before enabling automatic post-match updates.
- Store only development context needed for future reviews.
- Keep the profile in the Git-ignored `references/player-profile.md` file.
- Honor requests to correct, stop updating, or delete the private profile.
- Do not place private match links, signed URL parameters, or personal injury details in public reports or repository files.

## Health and injury context

- Treat pain, fatigue, and injury history supplied by the user as contextual information.
- Describe visible movement changes without diagnosing a condition.
- Do not advise playing through pain. Recommend professional assessment when symptoms are persistent, worsening, or acute.

## Evidence honesty

- Never imply footage was watched continuously if it was sampled.
- Never invent timestamps, scorelines, formations, player identities, or off-camera actions.
- Separate observed facts, tactical inferences, and unknowns.
- Keep private profile data out of public reports unless it is directly relevant and the user wants it included.
