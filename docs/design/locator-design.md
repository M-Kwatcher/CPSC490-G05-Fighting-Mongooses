# Design — Goal 2: Locator

> Epic: #14 · Stories: #15, #16, #17, #18 · Task: #49
> Owner: Aylani Tran · Sprint: 3 · Status: draft · Spec: [goal-2-locator.md](../specs/goal-2-locator.md)

## Overview

## Data flow

```mermaid
flowchart LR
    R[Hydrophone recordings] --> D[findDelay<br/>cross-correlation]
    D -->|2 hydrophones| A[delayToAngle] --> Dir[Direction]
    D -->|4 hydrophones| P[estimatePosition<br/>least squares] --> Dist[Distance]
    C[config.py<br/>speed of sound, sample rate, layouts] -.-> D
    C -.-> A
    C -.-> P
```

*Figure 1. Data flow through the locator.*

## Hydrophone layouts

## The math

## Key decisions

## Known limits

## Not designed yet