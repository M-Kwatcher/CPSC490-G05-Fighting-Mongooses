# Project Proposal — WILS: Whale Identification/Location System

**Department of Computer Science**
**CPSC 490 Undergraduate Seminar in Computer Science — Proposal for Capstone Project**

**Group 5 — Fighting Mongooses** · Sponsor: 〈RTX-3 / EL-1 / SNX-n / independent〉
Authors: Kwatcher, Max; Brambila, Matthew; Sainz, Michael; Tran, Aylani; Gargallo, Isabel
Date: 〈YYYY-MM-DD〉

> **This file is the proposal document, not a README.** Its section numbers,
> titles, and guidance are copied from the course Word template, so it
> converts cleanly for Canvas submission. Write continuous academic prose —
> no task lists, no emoji, no repo jargon.
>
> Each section below opens with the template's own guidance in a quote block.
> **Delete the quote blocks and every 〈bracket〉 before submitting.**
>
> **Getting this into the Word template for Canvas.** The template numbers
> its headings **automatically** (a multilevel list: top-level sections at
> level 1, *Related Work* and *Problem Statements* at level 2). The numbers
> typed below exist so the repo copy is readable and checkable — so when you
> move the text into Word, do not end up with both sets.
>
> The reliable route, and the one most teams should use: **open the course
> template and paste your prose section by section**, leaving Word's own
> numbering to do the numbering. Ten minutes, no surprises.
>
> If you prefer to convert, `pandoc` can do it (install with
> `winget install pandoc`):
>
>     pandoc proposal/proposal.md -o proposal.docx --reference-doc="CPSC 490 Project Proposal Template Fall 2026.docx"
>
> Then in Word: delete the typed `0.` / `1.` / `1.1` prefixes (Word re-adds
> them from the list), and set *Related Work* and *Problem Statements* to the
> template's level-2 heading so they number as 1.1 and 1.2. Check figure
> placement, then submit.
>
> **Formatting requirements — the submitted Word document is graded against
> these, explicitly:**
>
> - **Cover page: use the template's cover page, unchanged in layout.** Fill
>   in only its fields — project title, group number and name, sponsor,
>   authors, date — and keep the template's own placement, fonts and spacing
>   for it. The header block at the top of this file carries the same fields
>   so the paste is a transcription, not a redesign.
> - **Font: Times New Roman, 11-point.** Body text, headings and captions
>   take their size and style from the template's own styles — do not
>   restyle anything by hand.
> - **Line spacing: 1.5.** **Margins: 1.0 inch** on all four sides.
> - **Section format, numbering and indentation must match the Word template
>   exactly** — the multilevel-list numbering, heading levels, and paragraph
>   indentation are the template's, not yours. If your document's §1.1 looks
>   different from the template's §1.1, fix yours.
> - **Length: the Final Project Proposal Paper (due Sun Dec 20) must exceed
>   50 pages** under exactly this formatting — font, spacing and margins are
>   fixed above precisely so page count means the same thing for every team.
>   The Preview paper (due Sun Nov 29) is the same document part-way; it has
>   no minimum, but it is graded on the same formatting.
>
> A paste into the template inherits all of this automatically **if you paste
> as text and let Word's styles apply** (Home → Paste → *Keep Text Only*, or
> apply the template's styles after pasting). A pandoc conversion with
> `--reference-doc` inherits it too — but verify font, spacing and margins
> afterward rather than assuming.
>
> Either way, keep this Markdown copy current — it is what peer review and CI
> can actually read. If your team writes in Word instead, commit the `.docx`
> here as well.

---

## 0. Abstract

> The primary purpose of abstract is to help the reader understand the main
> message of current document (proposal in this case) without reading the
> entire document. Therefore an abstract should include at least one or two
> paragraph of background (or motivation) information for the project, a
> brief description of the problem you are trying to solve in this proposal,
> a proposed ideas or solutions, the significance of your proposed idea
> elaborating why the proposed idea is non-trivial, significant, or
> beneficial in one or two paragraphs, the project goals and outcomes in one
> paragraph, and a brief description of what you will discuss in this
> proposal, giving a brief outline of this document in 1-2 sentences in one
> paragraph. Abstract should not exceed one page. Any abstract exceeded
> one-page limit must be shortened.

〈Your abstract. Write it last.〉

## 1. Introduction

Sound travels at a constant speed, which is useful for triangulation since you can measure the difference between one observation and another to begin calculating the origin's location. This is especially beneficial to our system, as sound travels further in water due to the relative density of water compared against air. Sound travels by vibrating the molecules of the medium in which it travels. This means that for sound in water, it travels further than it would in air because the water molecules are more densely packed allowing the energy to propagate further before dissipating. This enables our system to track one or more whales over a considerable distance which would also reduce the total number of microphones needed over an area in order to track the whales. Identifying the whales poses a unique problem. We are hopeful that a properly trained deep learning model will be able to find patterns that the human mind cannot and therefore be able to differentiate one whale from another.

For our project, we seek to create a system that can passively track the location of whales as they transit the oceans of the world and potentially be able to identify specific whales or groups of whales as they are tracked.

Knowing where whales are and which species are present matters for protecting endangered populations, reducing collisions between whales and ships, and supporting responsible whale watching. A passive acoustic system can listen around the clock, in any weather, without disturbing the animals, and at a lower cost than aerial or boat surveys. Automating the detection and location of whale calls would let researchers make use of large amounts of underwater audio that are currently too time-consuming to review by hand.

### 1.1 Related Work

There is a similar project to ours that was done in 2025 by researchers from Cornell [[1](https://news.cornell.edu/stories/2025/02/new-study-advances-acoustic-monitoring-endangered-whale)]. Their goal was to passively and accurately count the right whale population as they fed in a common feeding ground off of Cape Cod. They specifically were interested in tracking right whales as they are an endangered species of whale. Their goal was to augment existing methods for tracking and tallying the right whale population by using a cheaper method than the traditional options which include an aerial survey. Using a deep learning model, the researchers were able to detect right whale sounds with a precision of 86%. Beyond Cape Cod, the researchers hope that their passive system will allow for an expanded range in which scientists can catalog and monitor right whale activity.

Another project with our common goal is an app similarly titles Whale Locator [[2](https://whalelocator.com/)]. Their goal was to reduce the number of ship strikes against whales by letting you know where they are so you could keep a safe distance away. Not only that, but they also provided you with knowledge of where other boats are in the water by using AIS (Automatic Identification System) vessel tracking. However, their service was reliant on people providing sighting reports of the locations of whales. They did also have camera and hydrophone setups to remotely watch and listen to whales, but these need the whale to be nearby to be seen.

An additional project seeking to protect whales is WhaleMap [[3](https://whalemap.org/)]. They're pursuing to better communicate whale survey results to inform more effective conservation activities. Like the Cornell project, they had noticed the threat of extinction that are looming over right whales. They also mix the concepts seen in the previous two projects, utilizing both reports obtained from people and acoustics from whales. To search for the acoustics, they use an underwater glider that has an attached system to detect their noises. The issues with this however is that the gliders expensive to implement on a large scale, as well as most data only existing between Cape Cod to the Honguedo Strait.

| Project | Pros | Cons | How Ours Differs |
|---------|------|------|------------------|
| 2025 Cornell Project | Able to detect the correct whales with 86% accuracy. Cheaper than traditional options. | Currently limited range. | Look out for more whale species. Alerts where to avoid whales. |
| Whale Locator | Marks locations of whales and vessels. Can give live notifications if you're nearing a whale. | Is reliant on the reports provided to it. | Use acoustics to locate whales. |
| WhaleMap | Uses autonomous gliders to acoustically locate whales. Marks locations of whales. | Limited range. Expensive. | Cheaper. Easier to scale. |

### 1.2 Problem Statements

Tracking whales today relies largely on visual methods such as aerial surveys, which are expensive and only work in daylight and good weather. Getting close to whales is also restricted: the Marine Mammal Protection Act makes it illegal to harass marine mammals, and federal guidelines limit how closely people, vessels, and aircraft, including drones, can approach them [[4](https://www.congress.gov/crs-product/R47892)]. Underwater recordings avoid these limits, but they are hard to use on their own, because listening through hours of audio by hand is slow and a recording alone does not show where a whale is.

Solving this is non-trivial. Ocean recordings are full of noise from ships, waves, and other animals, whale calls vary between species and individuals, and estimating a call's location requires precise timing across multiple hydrophones and accounting for how sound travels in water. This project will let us demonstrate skills from across our degree, including machine learning, signal processing, algorithm design, and software engineering, while building a tool that could benefit researchers and conservation efforts.

## 2. Goals and Objectives

- **Goal 1: Build an AI capable of recognizing whale calls** ([epic:#8](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/8))
  - Objective 1.1: Put together a database of different whale calls to be used in training an AI, with at least 200 labeled clips for each of at least three whale species (including humpback) and a noise class that includes boat noise. ([story:#9](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/9))
  - Objective 1.2: Build an AI that is capable of recognizing specific noises, detecting whether a clip contains a whale call or only background noise with at least 80% accuracy on a held-out test set. ([story:#10](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/10))
  - Objective 1.3: Teach the AI to recognize different whale calls using the database, identifying the correct species with at least 75% accuracy on a held-out test set. ([story:#11](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/11))
  - Objective 1.4: Demonstrate that the AI is able to differentiate between whale calls and some other noises that could be somewhat similar, classifying humpback calls against boat noise with at least 85% accuracy on a held-out test set. ([story:#12](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/12))
  - Objective 1.5: Save a clip of the whale call to calculate the distance away it was created (possibly save to hard drive so researchers can keep it for alternate purposes), with every detected call saved along with its timestamp and hydrophone ID. ([story:#13](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/13))
- **Goal 2: Create a locator capable of detecting how far away a sound was created** ([epic:#14](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/14))
  - Objective 2.1: "Listen" to the sound clip provided by the AI and build the locator to first recognize which direction a sound is coming from, estimating the direction within 15 degrees in a simulated two-hydrophone setup. ([story:#15](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/15))
  - Objective 2.2: Add the capability to measure the distance from which the sound was created to the locator, estimating the distance within 10% of the true distance in a simulated setup. ([story:#16](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/16))
  - Objective 2.3: Demonstrate that the locator is able to determine the direction and distance that a sound was created from, meeting the targets of Objectives 2.1 and 2.2 in at least 80% of 20 simulated test scenarios. ([story:#17](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/17))
  - Objective 2.4: Reconfigure the calculations from Objective 2.2 to adjust how sound travels through the water (if first created around how sound travels in air), using the speed of sound in seawater (about 1,500 m/s) while still meeting the 2.1 and 2.2 targets. ([story:#18](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/18))

## 3. Proposed Approaches

> Describe your proposed approach to solve the problem, specifying how you
> will achieve the stated goals. List some possible strategies.

〈Your approach — **clear and concise**. State the strategy you chose, the
alternatives you considered, and the reasoning that decided between them.
Think of this as the argument, not the manual: a reader should finish this
section understanding *what* you will do and *why that* rather than the
alternatives.〉

**Keep the details out of this section.** Tooling, platforms, frameworks,
DBMS choices, environment setup, diagrams, and the work breakdown all belong
in §4 (Required Environment, Resources, and Planned Activities). If a
sentence here names a version number, a library, or a configuration, it
probably belongs in §4 — leave a pointer instead ("the implementation stack
is detailed in §4").

〈A few paragraphs, or a short list of candidate strategies with one line of
trade-off each. If it runs past a page, you are writing §4.〉

## 4. Required Environment, Resources, and Planned Activities

> Review the required and available resources and environment to complete
> your project. For example, server, platform, software tools, operating
> systems, DBMS, or any required skills.
>
> Describe the expected activities to achieve the stated goals, e.g.,
> software development process.

〈Your environment, resources, and planned activities.〉

**Diagrams belong in this section.** Include at minimum a high-level
architecture diagram and a system (context) diagram; add the ER/EER model and
a data-flow diagram where they help the reader understand what you are
building and what it depends on. Draw them with any graphical tool
(Lucidchart, draw.io, Miro, Mermaid, ERDPlus, Figma), keep the authoritative
copies in `docs/design/` with both editable source and exported image, and
reference them here.

〈Number every figure, caption it, and point at it from the prose — "Figure 1
shows the three deployment tiers and the trust boundary between them." A
figure the text never mentions is decoration. See `docs/design/DIAGRAMS.md`
for tools, conventions, and the rule that every box and arrow must be
verified against reality.〉

### Specification and design documents

**Every specification and design document the team writes is listed here**
with the objective it serves. This section is the index of the project's
technical detail: §3 holds the argument, §4 holds the documents that make it
buildable. CI gate G9 fails if a document exists in `docs/specs/` or
`docs/design/` that this section does not link.

| Document | Kind | Covers | Issues |
|---|---|---|---|
| [docs/specs/goal-2-locator.md](../docs/specs/goal-2-locator.md) | specification | Goal 2 locator: direction, distance, demo, speed of sound | #14, #15, #16, #17, #18 |
| 〈docs/design/architecture.md〉 | design | 〈system architecture + data model〉 | 〈#n〉 |

〈The scaffold ships `docs/specs/example-spec.md` and
`docs/design/example-design.md` as worked examples — read them, then delete
them once you have your own, and list yours here.〉

〈Replace these rows with your own. Each document names its epic and stories
in its own first lines too (gate G2), so the trail runs both ways.〉

### Planned activities — the work items

The goals and objectives live in §2 as epics and user stories. **This section
links every *other* work item: features, enhancements, bugs, tasks, and
sub-tasks** — the concrete activities that deliver those objectives. CI gate
G8 fails if such an issue exists that this section does not link.

| Issue | Type | Activity | Parent | Owner | Sprint |
|---|---|---|---|---|---|
| [task:#20](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/20) | task | Write the Sprint 1 review | — | Aylani | Sprint 1 |
| [task:#24](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/24) | task | Fix Goal 1 link formatting | [epic:#8](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/8) | Isabel | Sprint 1 |
| [task:#25](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/25) | task | Fix Goal 2 link formatting | [epic:#14](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/14) | Isabel | Sprint 1 |
| [task:#26](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/26) | task | Comparative analysis (§1.1) | — | Matt | Sprint 1 |
| [task:#33](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/33) | task | Merge main back into develop | — | Aylani | Sprint 1 |
| [task:#29](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/29) | task | Finish the Sprint 1 review | — | Aylani | Sprint 2 |
| [task:#31](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/31) | task | Fill meetings attended in the Sprint 1 review | — | Aylani | Sprint 2 |
| [task:#35](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/35) | task | Release 0.1 to main | — | Aylani | Sprint 2 |
| [task:#41](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/41) | task | Write the Goal 2 specification | [epic:#14](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/14) | Aylani | Sprint 2 |
| [task:#42](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/42) | task | Clean up prototype/ for a fresh-machine setup | [epic:#14](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/14) | Aylani | Sprint 2 |
| [task:#49](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/49) | task | Locator design doc | [epic:#14](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/14) | Aylani | Sprint 3 |
| [task:#50](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/50) | task | Locator works at the dataset's sample rate | [epic:#14](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/14) | Aylani | Sprint 3 |
| [task:#51](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/51) | task | Fix reference [1] in the prototype README | [epic:#14](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/14) | Aylani | Sprint 3 |
| [task:#52](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/52) | task | Sprint 3 review | — | Aylani | Sprint 3 |
| [task:#53](https://github.com/M-Kwatcher/CPSC490-G05-Fighting-Mongooses/issues/53) | task | List work items in proposal §4 | — | Aylani | Sprint 3 |


## 5. Project Outcomes

> Describe the outcomes or deliverables, e.g., final project report, user
> manuals, source code, data or database files, etc.
>
> Note: the deliverables always include the team GitHub repository, which
> must already contain prototype v0 (a thin end-to-end proof-of-concept,
> however small, running when this proposal is submitted). Briefly describe
> what your v0 demonstrates and how to run it.

〈**One or two paragraphs** explaining the project outcome overall — what will
exist when the project is finished, and what it will let someone do. Keep it
prose, not a checklist; name the deliverables inside the paragraphs, and say
briefly what prototype v0 demonstrates today and how to run it.〉

## 6. Project Timeline

> Identifies tasks (project objectives) to be performed, milestones to be
> met, and the estimated number of hours for each task.

〈**This is the plan for CPSC 491 next semester — the implementation timeline,
not this semester's proposal work.** Identify the tasks (your objectives from
§2), the milestones, and the estimated hours for each, in the order they will
be built. State the assumptions it rests on (sponsor availability, data
access, hardware).〉

| Task (objective) | Milestone | Owner | Est. hours | Spring phase |
|---|---|---|---|---|
| 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 |
| 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 | 〈…〉 |

〈Do **not** put this fall's four proposal sprints here — those live on the
project board and in `docs/sprint-reviews/`. This section answers "how does
the system actually get built next semester?"〉

## 7. AI Usage

> Per the course AI policy (see the syllabus, Use of AI Tools), disclose the
> AI tools used in preparing this proposal and the prototype: which tools,
> for what tasks (e.g., code generation, test writing, debugging,
> diagramming), and approximately what fraction of each artifact was
> AI-assisted.
>
> Reminder: the prose of this proposal must be your own writing. You remain
> fully responsible for the correctness of all AI-assisted work, including
> the prototype code.

〈Your disclosure. Naming the tool is not disclosure — name what it drafted,
what fraction of each artifact was AI-assisted, and how you verified it.〉

## 8. References

[1] M. L. Garcia, I. Tolkova, S. Madhusudhana, A. Rahaman, C. S. Baker, C. A. Mayo, C. A. Hudak, and H. Klinck, "Acoustic abundance estimation for critically endangered North Atlantic right whales in Cape Cod Bay, Massachusetts, USA," *Endangered Species Research*, vol. 56, pp. 101–115, 2025, doi: 10.3354/esr01384.

[2] Marine Mammal Protection Act of 1972, 16 U.S.C. § 1361 et seq.
