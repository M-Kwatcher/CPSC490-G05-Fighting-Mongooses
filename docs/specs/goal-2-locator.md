# Specification — Goal 2: Locator

> Epic: #14 · Stories: #15, #16, #17, #18
> Owner: Aylani Tran · Sprint: 2 · Status: draft

The locator estimates where a whale call came from, its direction and its
distance, using the time difference of arrival (TDOA) between hydrophones.

## Scope

**In scope.** Simulated hydrophone recordings of a call from a known position,
direction from 2 hydrophones, distance from a 4-hydrophone array, a
demonstration over many simulated scenarios, and the seawater speed of sound.

**Out of scope.** Real hydrophone hardware, real-time streaming, depth (3D),
several whales calling at once, echoes, telling front from back with only 2
hydrophones, and the speed of sound changing with temperature or depth.

## Functional requirements

| ID | Requirement | Story |
|---|---|---|
| FR-1 | When given two hydrophone recordings of a call, the system shall estimate the direction it came from. | #15 |
| FR-2 | In a simulated two-hydrophone setup (10 m apart), the estimated direction shall be within 15° of the true direction, from −80° to 80°. | #15 |
| FR-3 | When given recordings from the 4-hydrophone array, the system shall estimate the distance to the call. | #16 |
| FR-4 | In a simulated setup (4 hydrophones in a 50 m square), the estimated distance shall be within 10% of the true distance, from 25 m to 500 m, in any direction. | #16 |
| FR-5 | When run on 20 simulated scenarios, the system shall report how many meet FR-2 and FR-4; at least 16 of 20 (80%) shall. | #17 |
| FR-6 | All locator calculations shall use the seawater speed of sound, 1,500 m/s. | #18 |

## Non-functional requirements

| ID | Requirement | Why it matters here |
|---|---|---|
| NFR-1 | Speed of sound, sample rate and hydrophone positions are set in one place, `prototype/locator/config.py`. | Real datasets use different sample rates (one is 2 kHz), so this must be easy to change. |
| NFR-2 | FR-2 and FR-4 hold with added noise as loud as the call itself. | Ocean recordings are noisy. |
| NFR-3 | Simulated noise is seeded, so every test gives the same result each run. | A test that passes sometimes proves nothing. |
| NFR-4 | Every functional requirement has an automated test that CI runs on every pull request. | Keeps the requirements checked as the code changes. |

## Acceptance criteria (epic level)

- [ ] FR-1 through FR-6 each have a test that fails if the behavior is removed.
- [ ] `python -m locator.smoke` prints a direction and a distance from a fresh clone, following `prototype/README.md`.
- [ ] The #17 demonstration meets FR-5 on 20 scenarios.
- [ ] `python .github/scripts/check_repo.py` is green and the prototype tests pass.

## Open questions

| Question | Owner | Needed by |
|---|---|---|
| Which dataset's sample rate do we design for? One is 2 kHz, where one sample is 0.75 m of sound travel instead of 3 cm. | Aylani, Max | Sprint 3 |
| What hydrophone layout and spacing would a real deployment use? | Team | Sprint 3 |
| Do any datasets have the same call recorded on several hydrophones, so we can test beyond simulation? | Max | Sprint 3 |
| How does the detector (#10, #13) hand saved calls to the locator? | Matt, Isabel, Aylani | Sprint 3 |