---
name: workflow-brainstorming
description: Use when medium or heavy implementation has non-trivial behavior change and still needs design refinement because boundaries, trade-offs, migration, rollout, or option choice are not fully clear before coding
---

# Brainstorming Ideas Into Designs

Use this skill to refine ambiguous or high-impact implementation work before writing code.

Start by understanding the current project context, then decide whether the task needs collaborative design work before coding. For `heavy implementation`, default to brainstorming unless boundaries, trade-offs, and rollout or migration choices are already explicit.

## When to Use

Use `workflow-brainstorming` when one or more are true:
- the request changes behavior in a non-trivial way
- requirements, success criteria, or boundaries are still unclear
- there are meaningful product or architecture trade-offs
- the work touches multiple subsystems or shared contracts
- the user wants help exploring options before implementation

Do **not** use this skill for routine local changes such as small bug fixes, copy edits, narrow config changes, narrow test updates, or other `lightweight implementation` work that can be implemented safely with a short plan.

If the work is already clear enough for `medium implementation`, skip brainstorming and move straight to a short explicit checklist or `workflow-writing-plans`, depending on the verification burden.

## Strong Triggers (Default Yes)

Run `workflow-brainstorming` by default when one or more are true:
- the route is already `heavy implementation` and any architecture or product trade-off is unresolved
- cross-layer changes include compatibility, migration, rollout, or rollback considerations
- more than one viable design exists and the choice affects cost, risk, or timeline
- the implementation direction depends on assumptions that are not yet validated

Skipping brainstorming in these cases requires explicit evidence that boundaries, trade-offs, and verification strategy are already settled.

## Lightweight Exception

If the task is `lightweight implementation` and the goal, boundary, risk, and verification are already clear:
1. capture a short plan inline
2. implement directly
3. verify directly

Do not force a separate design loop onto work that already fits `lightweight implementation` or a clear `medium implementation` checklist.

## Process

### 1. Explore project context

- inspect the existing code, docs, and recent relevant changes
- determine whether this is one task or several independent subsystems
- if it is too large for one design, decompose it before refining details

### 2. Ask only the highest-value questions

- ask questions only when the answer materially changes the design
- prefer one question at a time when the topic is genuinely open-ended
- for `medium implementation`, it is often better to present 2-3 concrete options with a recommendation instead of stretching the user through long discovery
- do not ask questions that can already be answered from the repo, prior context, or governing instructions

### 3. Propose options when trade-offs matter

- present 2-3 approaches when there is a real decision to make
- lead with the recommended option and explain why
- keep options concise and grounded in this codebase

### 4. Present the design at the right weight

Scale the output to the task:
- `medium implementation`: a short design summary may be enough
- `heavy implementation`: cover architecture, boundaries, data flow, failure cases, and verification

Ask for approval only when the design contains decisions the user should confirm. Do not create approval ceremony for straightforward work.

## Documentation

Persist a design doc only when one of these is true:
- the user explicitly asked for it
- project policy requires it
- the design will clearly help handoff, review, or future maintenance

Default location when saving:
- `docs/workflow/prd/YYYY-MM-DD-<topic>-design.md`

If no durable artifact is needed, keep the design in the conversation and move forward.

## Transition to Implementation

After design work:
- go directly to `lightweight implementation` when the work has collapsed into a small, well-bounded task
- go directly to `medium implementation` when a short checklist is enough to execute safely
- use `workflow-writing-plans` when `heavy implementation` or a coordination-heavy `medium implementation` still needs a real plan or handoff artifact

Do not automatically force every brainstormed task into a heavyweight plan document.

## Key Principles

- design should remove uncertainty, not create ceremony
- keep questions scarce and high leverage
- prefer the shortest path that makes the next implementation step obvious
- follow existing project patterns and only include refactoring that serves the current goal
- keep boundaries crisp so implementation and verification stay local when possible

## Visual Companion

A browser-based companion for showing mockups, diagrams, and visual options during workflow-brainstorming. Available as a tool, not a mode. Accepting the companion means it is available for questions that benefit from visual treatment; it does not mean every question goes through the browser.

**Offering the companion:** When upcoming discussion will benefit from visual content, offer it once for consent:
> "Some of what we're working on might be easier to explain if I can show it to you in a web browser. I can put together mockups, diagrams, comparisons, and other visuals as we go. This feature is still new and can be token-intensive. Want to try it? (Requires opening a local URL)"

**This offer MUST be its own message.** Do not combine it with clarifying questions or summaries. Wait for the user's response before continuing. If they decline, continue in text.

**Per-question decision:** Even after the user accepts, decide each time whether the browser is actually the best medium.

- use the browser for mockups, diagrams, visual comparisons, and layout discussion
- use the terminal for requirements, trade-offs, scope decisions, and other text-heavy discussion

If they agree to the companion, read the detailed guide before proceeding:
`skills/workflow-brainstorming/visual-companion.md`
