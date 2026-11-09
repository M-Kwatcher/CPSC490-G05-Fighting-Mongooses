# Specifications - Goal 1: AI Detector

> Epic: #8 · Stories: #10, #11, #12, #13
> Owner: Matthew Brambila · Sprint: 3 · Status: Draft

The AI detector determines when a whale sound is heard, and distinguishes it from
other noises possibly heard. Once it hears it, it saves the clip with the time it
was recorded and the hydrophone's ID.

## Scope

**In scope.** Simulating hearing whale calls from a known species with prerecorded
audio, ignoring prerecorded audio of boats and empty water, saving the appropriate
information when a whale is heard, and demonstrating with a simulated scenario.

**Out of scope.** Detector being tested in real time, a hydrophone to listen
for the whale calls, and the ability to play whale calls at a volume and distance similar
to them.

## Functional Requirements

| ID | Requirement | Story |
|---|---|---|
| FR-1 | When a whale call is heard, the detector shall recognize it as such. | #10 |
| FR-2 | When a whale call is heard, the detector will save the audio clip, time, and hydrophone ID. | #13 |
| FR-3 | When recognizing a whale call, it shall also identify what species it is. | #11 |
| FR-4 | When boat noises are heard, the detector will ignore it. | #12 |
| FR-5 | In a simulated set-up (whale call in empty water), it will be at least 80% accurate in a test set. | #10 |
| FR-6 | In a simulated set-up (whale call with boat noises), it will be at least 85% accurate in a test set. | #12 |
| FR-7 | In a simulated set-up (whale calls from different species), it will be at least 75% accurate in a test set. | #11 |

## Non-functional Requirements

| ID | Requirement | Why it matters |
|---|---|---|
| NFR-1 | A different detector is created for each species of whale to all run simultaneously | Each whale noise exists at a different frequency and noise length, so creating multiple detectors as specialists reduces the chance of the detector misinterpreting the data. |
| NFR-2 | FR-6 stills holds true when mixed with boat noises | The ocean can be noisy, so we need to make sure it can accurately identify despite the noise. |
| NFR-3 | The simulations use untrained audio. | Using the same audio doesn't prove the detector knows what to look for, just that it can recognize patterns. |
| NFR-4 | Every functional requirement has an automated test that is ran by CI every pull request. | Ensures code changes won't affect results. |

## Acceptance Criteria
- [ ] FR-1 through FR-7 have a test that fails if the behavior is removed.
- [ ] **TEMP** FR-2 and FR-3 are output to *file* using *command*.
- [ ] Models are trained using only 80-85% of the database, so the remainder can be for testing.
- [ ] `python .github/scripts/check_repo.py` is green and the prototype tests pass.

## Open Questions

| Question | Owner | Needed By |
|---|---|---|
| Where do the audio clips save to? | Team | Sprint 3 |
| How will the detector read the database during training? | Max | Sprint 3 |
| What type of audio file should the clips be saved as? | Aylani | Sprint 3 |
