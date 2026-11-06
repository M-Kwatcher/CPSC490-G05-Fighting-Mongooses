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
| FR-1 | When a whale call is heard, the detector shall recognize it as such | #10 |
| FR-2 | When recognizing a whale call, it shall also identify what species it is | #11 |
| FR-3 | When boat noises are heard, the detector will ignore it | #12 |
| FR-4 | In a simulated set-up (whale call in empty water), it will be at least 80% accurate in a test set | #10 |
| FR-5 | In a simulated set-up (whale call with boat noises), it will be at least 85% accurate in a test set | #12 |
| FR-6 | In a simulated set-up (whale calls from different species), it will be at least 75% accurate in a test set | #11 |
