# Plan Review Prompt Template

Use this template when dispatching an implementation plan reviewer subagent.

**Purpose:** Verify the plan is complete, aligned to the source spec, and actionable for implementation.

```
Task tool (general-purpose):
  description: "Review plan document"
  prompt: |
    You are a plan document reviewer. Verify this plan is complete and ready for implementation.

    **Plan to review:** [PLAN_FILE_PATH]
    **Spec for reference:** [SPEC_FILE_PATH]

    ## What to Check

    | Category | What to Look For |
    |----------|------------------|
    | Completeness | TODOs, placeholders, incomplete tasks, missing setup, missing validation steps |
    | Spec Alignment | Plan covers the spec requirements, with no major drift or scope creep |
    | Task Decomposition | Tasks have clear boundaries, correct ordering, and actionable steps |
    | Buildability | Could an implementer follow this plan without getting stuck or guessing? |
    | Consistency | Types, names, paths, and commands stay consistent across tasks |

    ## Calibration

    Only flag issues that would cause real problems during implementation.
    An implementer building the wrong thing, missing a requirement, or getting stuck is a real issue.
    Minor wording, stylistic preferences, and nice-to-have suggestions are not blocking issues.
    Approve unless there are serious gaps, contradictions, placeholders, or vague steps.

    ## Output Format

    ## Plan Review

    **Status:** Approved | Issues Found

    **Issues (if any):**
    - [Task or section]: [specific issue] - [why it matters for implementation]

    **Recommendations (advisory, do not block approval):**
    - [suggestion]
```
