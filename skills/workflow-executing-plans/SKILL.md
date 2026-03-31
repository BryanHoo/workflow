---
name: workflow-executing-plans
description: Use when you have a written or clearly stated implementation plan and the work is best executed in one session without heavy parallel coordination; this is the default execution path for complex but mostly sequential tasks
---

# Executing Plans

## Overview

Load the plan, review it critically, execute the work, and verify each checkpoint before moving on.

**Announce at start:** "I'm using the workflow-executing-plans skill to implement this plan."

This is the default execution path for non-trivial work that does **not** clearly benefit from subagent-driven parallelism.

It is also the fallback path when the plan would conceptually benefit from delegation, but the current environment does not support subagents or reliable parallel execution.

## Step 1: Load and Right-Size the Plan

1. Read the plan or the explicit task list
2. Check whether it is still the right size for the task
3. If the work has collapsed into a lightweight local change, compress the plan and implement directly
4. If the work is bigger or riskier than expected, pause and refine the plan before coding

Review for:
- missing context
- unclear boundaries
- hidden risks
- missing verification
- opportunities to simplify the approach

Raise substantive gaps before implementation. Do not blindly execute a bad plan.

If `docs/workflow/spec/` exists, invoke `workflow-project-spec` in load mode before implementation starts. Use its bundled `scripts/detect_spec_scope.py` to resolve the relevant spec files, then read those files before editing code.

## Step 2: Execute Sequentially

For each task or checkpoint:
1. mark it in progress
2. implement the scoped change
3. run the stated verification
4. update the plan or notes if reality changed
5. mark it complete only after evidence is in hand

Prefer targeted verification during execution and broader verification before completion.

If the task establishes a reusable convention, contract, or gotcha, update the relevant `docs/workflow/spec/` file before handoff by using `workflow-project-spec` in update mode.
If `docs/workflow/spec/` exists and code changed, use `workflow-project-check` before final completion claims so the final verification scope comes from the actual diff, not just the original plan.

## Step 3: Escalate Only When Needed

Switch away from this skill only if the task materially changes:
- use `workflow-subagent-driven-development` when the work breaks into genuinely independent chunks, parallel coordination is worth it, and the environment supports it
- use `workflow-writing-plans` again if the plan no longer reflects reality
- use `workflow-systematic-debugging` if execution turns into root-cause investigation

## Step 4: Complete Development

Before making success claims:
- if `docs/workflow/spec/` exists, use `workflow-project-check`
- use `workflow-verification-before-completion`

If the work is ready for branch completion or handoff:
- announce: "I'm using the workflow-finishing-a-development-branch skill to complete this work."
- use `workflow-finishing-a-development-branch`

## When to Stop and Ask for Help

Stop and ask when:
- a blocker prevents meaningful progress
- the plan is missing critical decisions
- verification keeps failing and the issue is no longer straightforward
- the task boundary has clearly expanded beyond the original agreement

Ask for clarification rather than guessing.

## Remember

- treat plans as guides, not scripts to follow blindly after reality changes
- keep execution sequential unless parallelism is clearly beneficial
- do not create a worktree by default; use one only when isolation helps
- never start implementation on main/master without explicit user consent

## Integration

Related workflow skills:
- `workflow-writing-plans` - creates or refines the plan this skill executes
- `workflow-systematic-debugging` - use when execution becomes real diagnosis work
- `workflow-project-check` - derives the final project-aware verification scope from the changed files
- `workflow-verification-before-completion` - required before claiming success
- `workflow-finishing-a-development-branch` - close out the branch after the work is verified
