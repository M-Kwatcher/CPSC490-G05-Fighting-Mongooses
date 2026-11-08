# Design - AI detection

> Epic: #8 · Stories: #10, #11, #12, #13
> Sprint: 3 · Status: draft
> Specification: [../specs/goal-1-detector.md] (need to connect when merged in same branch)

## 1. System Context

The system boundary for the detector exists in between the database and
locator. It first draws from the database to first train itself to sufficiency, and
later sends what it detectors to the locator.

"""ADD DIAGRAM WHEN MERGED"""

*Figure 1- *

## 2. Components

| Component | Responsibility | Interface | Where |
|---|---|---|---|
| audio converter | Converts the audio files stored in the database to a readable format for the detector (.npz) | Audio file -> `/data` | `prototype/ai-detector` |
| ai trainer | Builds/trains the models based off the files located within data. Model stored in a pt file | `/data` -> model.pt | `prototype/ai-detector/whale_detector.py` |
| live detector | Runs the ai indefinitely, forwarding the recording, time, and hydrophone ID when hearing a whale | live audio -> `/recordings` | `prototype/ai-detector` |

