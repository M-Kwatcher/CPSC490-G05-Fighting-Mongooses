# Sprint 1 review — Sep 28 – Oct 11

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

**Prototype moved:** Nothing yet. `prototype/` still contains only the
course's example login slice; no WILS code was written this sprint.

Both lines are thin, and we are saying so plainly: during the sprint we
worked on the proposal in a shared Google Doc and did not move it into the
repository. The epics and user stories (#8–#18), the course labels, and
PR #19 were all created on **Oct 13, after the sprint boundary**, in response
to instructor issue #7. 〈Team: add any other reason here, e.g. how work was
split, if it explains the gap.〉

## Velocity

| | Story points | Stories |
|---|---|---|
| Planned | 0 | 0 |
| Completed | 0 | 0 |

No user stories existed during Sprint 1, so none were pointed or placed in
the `Sprint 1` milestone.

## Completed (merged PRs)

| Story | Owner | Points | PR |
|---|---|---|---|
| — (no user stories completed) | — | — | — |

Instructor updates merged into `develop` on Oct 13 (after the boundary):
PR #2 (sprint report counts writing-task points; README sponsor link fixed),
PR #4 (harness G10 lets a writing task stand alone), PR #6 (one-command Word
export of `proposal.md`).

## Carried over — and why

| Story | Owner | Why not finished | Decision |
|---|---|---|---|
| #9–#13 (Goal 1, Epic #8) | 〈@owner〉 | Not filed until after the boundary | 〈Team: move to Sprint 2 / re-scope〉 |
| #15–#18 (Goal 2, Epic #14) | 〈@owner〉 | Not filed until after the boundary | 〈Team: move to Sprint 2 / re-scope〉 |
| Proposal PR #19 (closes #7) | @a-t-tran | Opened Oct 13; awaiting teammate review | Merge early in Sprint 2 |

## Loop health (docs/aidlc/loop-engineering.md §8)

| | This sprint |
|---|---|
| Iterations to green, average per PR | 〈n — PR #19 needed 3 CI runs: its description still contained template comments, and the harness was red from the README link fixed by PR #2〉 |
| Harness rules added (rows in the harness log) | 0 |

〈One line: is our spec-writing improving, or are we still discovering
requirements during implementation? — Team to answer.〉

## Prototype increment

None this sprint. 〈Team: state what the Week-8 in-class prototype check will
demo, or what was shown, and what Sprint 2 will build.〉

## Feedback we received, and what we did about it

Every item of feedback from the instructor, the sponsor, or a reviewer gets a
row. "We were told and did nothing" is a legitimate row — with a reason.

| Feedback (source) | What we changed | Issue / PR |
|---|---|---|
| Instructor, issue #7: no epics or user stories in the repo; HW#5 §2 cited Epic #1 and #2, which were not ours | Filed Epic #8 (stories #9–#13) and Epic #14 (stories #15–#18), each story with its objective, parent epic, and acceptance criteria; linked all of them from §2 | #8–#18 / PR #19 |
| Instructor, HW#5 evaluation in issue #7: objectives were build steps with no measure of done; missing cover page, problem statement, and references; fold Objective 2.5 into 2.1 | Rewrote every objective as a measurable result, added the cover page, §1.2 Problem Statements, and §8 References, and folded 2.5 into 2.1 | PR #19 |
| Instructor, issues #1, #3, #5: course scaffold updates to review and merge | Reopened, reviewed, and merged the instructor PRs (they had been closed without merging) | PR #2, PR #4, PR #6 |

## Contribution snapshot

Three metrics the team chose, per member. Not a grade — a conversation
starter, and an early warning the team can act on itself.

| Member | Meetings attended | Merged PRs | Issues closed | Reviews given |
|---|---|---|---|---|
| Max Kwatcher (@M-Kwatcher) | 〈n〉 | 〈n〉 | 〈n〉 | 〈n〉 |
| Matthew Brambila (@〈user〉) | 〈n〉 | 〈n〉 | 〈n〉 | 〈n〉 |
| Michael Sainz (@〈user〉) | 〈n〉 | 〈n〉 | 〈n〉 | 〈n〉 |
| Aylani Tran (@a-t-tran) | 〈n〉 | 〈n〉 | 〈n〉 | 〈n〉 |
| Isabel Gargallo (@〈user〉) | 〈n〉 | 〈n〉 | 〈n〉 | 〈n〉 |

〈If one member is far below the others, say what the team is doing about it
here — and note anything the numbers hide, e.g. pairing (use
`Co-authored-by:` so it shows up), or a big unmerged branch.〉

## What we change next sprint

- 〈Team: one concrete process change, if any〉
