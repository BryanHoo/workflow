---
name: workflow-writing-plans
description: "Use when medium or heavy implementation needs a real execution plan before coding: multi-step changes, cross-file coordination, unclear sequencing, or handoff across sessions or agents; skip for lightweight implementation and medium work that is still safe with a short inline checklist"
---

# Writing Plans

## Overview

Write plans that are just detailed enough to guide correct implementation.

**Announce at start:** "I'm using the workflow-writing-plans skill to create the implementation plan."

If the repo contains `docs/workflow/spec/`, announce that you are also using `workflow-project-spec` to load the relevant project spec before finalizing the plan.
If the work will end with project-aware verification, announce that `workflow-project-check` will be used to derive the final verification scope from the actual diff.

Do not create a heavyweight plan for work that still fits `lightweight implementation` or a clear `medium implementation` checklist.
If `heavy implementation` still has unresolved architecture, migration, or rollout choices, run `workflow-brainstorming` before freezing the plan.

## Choose the Right Plan Weight

### Short inline plan

Use an inline plan in the conversation when the task belongs to `medium implementation` and still fits comfortably in session context.

Minimum contents:
- goal
- boundary
- main risks
- verification approach

### Full plan document

Write a standalone plan file when one or more are true:
- the task is clearly `heavy implementation`
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

When `docs/workflow/spec/` exists:
- invoke `workflow-project-spec` in load mode and run its bundled `scripts/detect_spec_scope.py` from the `workflow-project-spec` skill directory, not from the target repo
- read the returned index and detailed files before fixing scope, risks, and verification
- treat those files as project-specific constraints for the plan
- leave room in the verification section for `workflow-project-check` to refine the final command set from the real changed files

Prefer plans that preserve local reasoning:
- group changes by responsibility
- keep related files together
- avoid unrelated refactors
- follow the existing codebase shape unless the current shape is itself part of the problem
- when a task includes readability-only cleanup after behavior is already green, prefer one final `workflow-code-simplifier` pass near the end instead of inserting cleanup after every task

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

**Project Check:** [How `workflow-project-check` will be used before completion when `docs/workflow/spec/` exists]

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

- use `workflow-executing-plans` for most `heavy implementation` work and for `medium implementation` work whose checklist now needs explicit checkpoints
- use `workflow-subagent-driven-development` when tasks are genuinely independent, subagent coordination is worth the overhead, and the environment supports reliable delegation
- fall back to `workflow-executing-plans` when the tasks are independent in theory but the environment does not support subagents or parallel execution
- skip both and implement directly if the plan has collapsed into `lightweight implementation`

Do not require a worktree unless isolation meaningfully reduces risk.
