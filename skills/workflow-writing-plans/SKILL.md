---
name: workflow-writing-plans
description: "Use when implementation needs a real execution plan before coding: multi-step changes, cross-file coordination, unclear sequencing, or handoff across sessions or agents; skip for lightweight local changes that can be implemented safely with a short inline plan"
---

# Writing Plans

## Overview

Write plans that are just detailed enough to guide correct implementation.

**Announce at start:** "I'm using the workflow-writing-plans skill to create the implementation plan."

Do not create a heavyweight plan for a task that can be implemented safely with a short checklist.

## Choose the Right Plan Weight

### Short inline plan

Use an inline plan in the conversation when the task is medium-sized but still local enough to keep in context.

Minimum contents:
- goal
- boundary
- main risks
- verification approach

### Full plan document

Write a standalone plan file when one or more are true:
- the work spans multiple subsystems
- execution will happen across sessions
- multiple agents or reviewers need a shared artifact
- the user explicitly wants a saved plan
- project policy requires durable planning docs

Default save location:
- `docs/workflow/plans/YYYY-MM-DD-<feature-name>.md`

## Scope Check

If the request really contains multiple independent efforts, split it into separate plans. Each plan should target one coherent piece of working software.

## Plan Content

Before listing tasks, map:
- which files will change
- which new files may be created
- which shared boundaries or APIs are at risk
- what verification will prove the work is done

Prefer plans that preserve local reasoning:
- group changes by responsibility
- keep related files together
- avoid unrelated refactors
- follow the existing codebase shape unless the current shape is itself part of the problem

## Task Granularity

Each task should be a meaningful checkpoint, not a pile of micro-steps and not an oversized milestone.

Good task shape:
- can be implemented and verified with one coherent round of work
- has clear files in scope
- has an explicit verification command or checklist

Avoid:
- tasks so small that the plan becomes ceremony
- tasks so large that failure leaves no obvious recovery point

## Full Plan Template

```markdown
# [Feature Name] Implementation Plan

**Goal:** [What this change accomplishes]

**Boundary:** [What is in scope and what is intentionally out of scope]

**Risks:** [Primary technical or product risks]

**Verification:** [Commands, scenarios, or checks that prove success]

## Task 1: [Name]

**Files:**
- Modify: `path/to/file`
- Create: `path/to/new-file`
- Verify: `command or scenario`

**Implementation notes:**
- [Key change]
- [Important constraint]

## Task 2: [Name]
...
```

Use exact file paths and concrete verification. Include snippets only when they materially reduce ambiguity. Do not bloat plans with full code listings unless the code itself is the point of the handoff.

## No Placeholder Thinking

These are plan failures:
- "TBD" / "TODO" / "implement later"
- "handle edge cases" without naming the edge cases
- "write tests" without saying what to verify
- "same as above" when the later task depends on hidden context

## Execution Handoff

After planning, choose execution mode based on the work:

- use `workflow-executing-plans` for complex but mostly sequential work
- use `workflow-subagent-driven-development` when tasks are genuinely independent and subagent coordination is worth the overhead
- skip both and implement directly if the plan has collapsed into a lightweight local change

Do not require a worktree unless isolation meaningfully reduces risk.
