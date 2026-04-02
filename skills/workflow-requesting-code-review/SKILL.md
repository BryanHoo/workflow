---
name: workflow-requesting-code-review
description: Use when medium or heavy implementation is risky, merge-bound, or otherwise likely to benefit from a fresh technical pass; optional for lightweight implementation with direct verification
---

# Requesting Code Review

Dispatch workflow-code-reviewer subagent to catch issues before they cascade. The reviewer gets precisely crafted context for evaluation — never your session's history. This keeps the reviewer focused on the work product, not your thought process, and preserves your own context for continued work.

If the environment does not support reviewer subagents, run the same review inline in the current session using the same diff, requirements, and severity bar.

**Core principle:** Review early, review often.

## When to Request Review

**Usually required:**
- After completing `heavy implementation`
- Before merge to main
- When a subagent-driven workflow defines review checkpoints

**Optional but valuable:**
- Before shipping `medium implementation` behavior changes
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

**Usually unnecessary:**
- `lightweight implementation` with clear scope and direct verification
- copy, config, or similarly low-risk edits unless the user asks for review

If the repo contains `docs/workflow/spec/` and code changed, run `workflow-project-check` before requesting review so the reviewer sees a diff that has already passed the project-aware verification pass.

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA="$(git rev-parse HEAD~1)"; HEAD_SHA="$(git rev-parse HEAD)"  # or origin/main
```

**2. Dispatch code-reviewer subagent when supported:**

Use Task tool with workflow-code-reviewer type, fill template at `code-reviewer.md`

**Placeholders:**
- `{WHAT_WAS_IMPLEMENTED}` - What you just built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{BASE_SHA}` - Starting commit
- `{HEAD_SHA}` - Ending commit
- `{DESCRIPTION}` - Brief summary

**Fallback:** If no reliable subagent mechanism exists, use the same filled template as an inline review checklist in the current session. Review the diff directly, produce findings with the same severity discipline, and only continue after acting on the important feedback.

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

## Project-Aware Review Prep

Before requesting review in a repo with `docs/workflow/spec/`:
- use `workflow-project-check`
- run the required commands it identifies
- complete its manual checks
- update `docs/workflow/spec/` first if it says spec sync is required

Review should inspect a technically prepared diff, not substitute for missing local verification.

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA="$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')"; HEAD_SHA="$(git rev-parse HEAD)"

[Dispatch workflow-code-reviewer subagent]
  WHAT_WAS_IMPLEMENTED: Verification and repair functions for conversation index
  PLAN_OR_REQUIREMENTS: Task 2 from docs/workflow/plans/deployment-plan.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## Integration with Workflows

**Subagent-Driven Development:**
- Review after EACH task
- Catch issues before they compound
- Fix before moving to next task
- If subagents are unavailable, keep the same per-task review cadence inline in the current session

**Executing Plans:**
- Review after each batch (3 tasks)
- Get feedback, apply, continue
- If `docs/workflow/spec/` exists, run `workflow-project-check` before requesting the review
- If delegation is unavailable, perform the review inline before starting the next batch

**Ad-Hoc Development:**
- Review before merge
- Review when stuck

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

See template at: workflow-requesting-code-review/code-reviewer.md
