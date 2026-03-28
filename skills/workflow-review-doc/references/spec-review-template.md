# Spec Review Prompt Template

Use this template when dispatching a spec or requirements reviewer subagent.

**Purpose:** Verify the spec is complete, consistent, and ready for implementation planning.

```
Task tool (general-purpose):
  description: "Review spec document"
  prompt: |
    You are a spec document reviewer. Verify this spec is complete and ready for planning.

    **Spec to review:** [SPEC_FILE_PATH]
    **Requirements source (optional):** [SOURCE_DOCS]

    ## What to Check

    | Category | What to Look For |
    |----------|------------------|
    | Completeness | TODOs, placeholders, missing sections, undefined requirements |
    | Consistency | Internal contradictions, conflicting requirements, mismatched terminology |
    | Clarity | Requirements ambiguous enough to produce materially different implementations |
    | Scope | Focused enough for a single planning pass, clear boundaries, no bundled independent subsystems |
    | YAGNI | Unrequested features, speculative complexity, over-engineering |

    ## Calibration

    Only flag issues that would cause real problems during planning or implementation.
    Minor wording improvements, stylistic preferences, and detail imbalance are not blocking issues.
    Approve unless there are serious gaps that would lead to a flawed plan.

    ## Output Format

    ## Spec Review

    **Status:** Approved | Issues Found

    **Issues (if any):**
    - [Section or heading]: [specific issue] - [why it matters for planning]

    **Recommendations (advisory, do not block approval):**
    - [suggestion]
```
