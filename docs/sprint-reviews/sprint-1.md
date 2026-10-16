# Sprint 1 review — Sep 29 – Oct 12

> One file per sprint, written at the sprint boundary (the setup guide's
> *The four sprints* section). This file, the board, and the merged PRs are
> what the sprint's **5%** (of the syllabus's 20% *Prototype & repository
> practice*) is assessed on — as they stand at the boundary.
> This is what makes **Transparency** and carry-over decisions visible at
> grading time — don't reconstruct it later.

## Progress this sprint — the substance

This is what the sprint's 5% is assessed on. Be concrete and link things.

**Proposal moved:**
| Section | What changed | Where |
|---|---|---|
| §1 Introduction | Background, project aim, and a significance paragraph | PR #19 |
| §1.1 Related Work | Cornell 2025 right whale acoustic monitoring study [1] | PR #19 |
| §1.2 Problem Statements | Limits of visual surveys and approach restrictions (MMPA [2]); why acoustic analysis is non-trivial | PR #19 |
| §2 Goals and Objectives | Objectives rewritten as measurable results per instructor feedback (#7); Objective 2.5 folded into 2.1; linked to Epic #8 (stories #9–#13) and Epic #14 (stories #15–#18) | PR #19 |
| §8 References | Garcia et al. 2025 and the Marine Mammal Protection Act | PR #19 |
| README.md | Replaced the course setup guide with the team and project README | PR #22 |

**Prototype moved:** Nothing yet. `prototype/` still contains only the
course's example login slice; no WILS code was written this sprint. A
prototype was not expected in Sprint 1.

Both lines are thin, and we are saying so plainly: during the sprint we
worked on the proposal in a shared Google Doc and did not move it into the
repository. The epics and user stories (#8–#18), the course labels, and
PRs #19, #21 and #22 were all created on **Oct 13–14, after the sprint
boundary**, in response to instructor issue #7. Work was also concentrated:
the proposal and issues came from one member, the README from another, and
two members had no work in the repository.

## Velocity

| | Story points | Stories |
|---|---|---|
| Planned | 0 | 0 |
| Completed | 0 | 0 |

No user stories or writing tasks existed during Sprint 1, so none were
pointed or placed in the `Sprint 1` milestone. `scripts/sprint_report.py
--sprint 1` reports 0 committed, 0 added mid-sprint and 0 completed.

## Completed (merged PRs)

| Story | Owner | Points | PR |
|---|---|---|---|
| — (no user stories completed) | — | — | — |

Merged into `develop` after the boundary: PR #19 (proposal §1–§2 and
references, Oct 14), PR #21 (first draft of this review), PR #22 (team
README). Instructor updates merged on Oct 13: PR #2 (sprint report counts
writing-task points; README sponsor link fixed), PR #4 (harness G10 lets a
writing task stand alone), PR #6 (one-command Word export of `proposal.md`).

## Carried over — and why

| Story | Owner | Why not finished | Decision |
|---|---|---|---|
| #9–#13 (Goal 1, Epic #8) | None during Sprint 1 | Filed after the boundary with no assignee or milestone | Moved to the `Sprint 2` milestone, each with one owner, a priority and points |
| #15–#18 (Goal 2, Epic #14) | None during Sprint 1 | Filed after the boundary with no assignee or milestone | Moved to the `Sprint 2` milestone, each with one owner, a priority and points |

## Loop health (docs/aidlc/loop-engineering.md §8)

| | This sprint |
|---|---|
| Failed CI runs before green, per PR | PR #19: 3 · PR #21: 2 · PR #22: 3 (average about 2.7) |
| Harness rules added (rows in the harness log) | 0 |

We are still discovering requirements during the work: the PR-body rules,
the broken README link, and the §2 issue-link format were all found through
red CI runs or instructor feedback rather than read before starting.

## Prototype increment

None this sprint. Prototype v0 starts in Sprint 2 in `prototype/`; the first
prototype demo is at our Sprint 3 meeting (Oct 27).

## Feedback we received, and what we did about it

Every item of feedback from the instructor, the sponsor, or a reviewer gets a
row. "We were told and did nothing" is a legitimate row — with a reason.

| Feedback (source) | What we changed | Issue / PR |
|---|---|---|
| Instructor, issue #7: no epics or user stories in the repo; HW#5 §2 cited Epic #1 and #2, which were not ours | Filed Epic #8 (stories #9–#13) and Epic #14 (stories #15–#18), each story with its objective, parent epic, and acceptance criteria; linked all of them from §2 | #8–#18 / PR #19 |
| Instructor, HW#5 evaluation in issue #7: objectives were build steps with no measure of done; missing cover page, problem statement, and references; fold Objective 2.5 into 2.1 | Rewrote every objective as a measurable result, added the cover page, §1.2 Problem Statements, and §8 References, and folded 2.5 into 2.1 | PR #19 |
| Instructor, issues #1, #3, #5: course scaffold updates to review and merge | Reopened, reviewed, and merged the instructor PRs (they had been closed without merging) | PR #2, PR #4, PR #6 |
| Instructor, Sprint 1 evaluation (Oct 14): no story has a milestone or an assignee | Moving every story into `Sprint 2` with one owner, a priority and points | #9–#18 |
| Instructor, Sprint 1 evaluation: this review had unfilled placeholders and a stale line about PR #19 | Filled every section and removed the stale line | this PR |
| Instructor, Sprint 1 evaluation: contribution concentrated in a few members | Split the follow-up work across members as separate issues, each reviewed by someone other than its author | #24, #25, #26 |
| Sprint 2 meeting (Oct 13): cite every goal and objective in §2 with a typed issue link, add a comparative analysis to §1.1, set up sprints, release to `main` | Filed as issues and in progress | #24, #25, #26 |

## Contribution snapshot

Three metrics the team chose, per member. Not a grade — a conversation
starter, and an early warning the team can act on itself.

Counts as of Oct 14, from GitHub. Sprint 1 had two team meetings: the Sprint 1 meeting (Sep 29) and a Discord call (Oct 6).

| Member | Meetings attended | Merged PRs | Issues closed | Reviews given |
|---|---|---|---|---|
| Max Kwatcher (@M-Kwatcher) | 2/2 | 1 | 1 | 2 |
| Matthew Brambila (@matt-bram) | 2/2 | 0 | 0 | 0 |
| Michael Sainz (@michaelsainzz) | 1/2 | 0 | 0 | 1 |
| Aylani Tran (@a-t-tran) | 2/2 | 2 | 3 | 3 |
| Isabel Gargallo (@Isabel285) | 2/2 | 0 | 0 | 0 |

Two members had no work in the repository during Sprint 1 and one had only a
review. For Sprint 2, every member owns at least one story and lands work
through their own pull request, and reviews are spread so that nobody only
authors or only reviews.

## What we change next sprint

- Do the work in the repository while the sprint is running, not at the
  boundary: every story gets an owner, the sprint milestone, a priority and
  points at planning, and progress is pushed at least every few days.
