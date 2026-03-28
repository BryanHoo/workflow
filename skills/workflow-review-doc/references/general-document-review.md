# General Document Review Prompt Template

Use this template when dispatching a reviewer for a working document.

**Purpose:** Verify the document is usable for its intended next step without guessing, contradictory interpretation, or hidden missing work.

```
Task tool (general-purpose):
  description: "Review working document"
  prompt: |
    You are reviewing a working document before handoff.

    **Document to review:** [DOCUMENT_PATH]
    **Document type:** [spec | plan | proposal | RFC | ADR | handoff | other]
    **Intended reader:** [engineer | reviewer | approver | stakeholder | other]
    **Next action this document must support:** [planning | implementation | approval | delegation | alignment]

    ## Optional Reference Material

    [REFERENCE_DOCS_OR_NOTES]

    ## What to Check

    | Category | What to Look For |
    |----------|------------------|
    | Completeness | Missing sections, TODOs, placeholders, undefined dependencies |
    | Consistency | Contradictions, mismatched terminology, conflicting instructions |
    | Clarity | Ambiguity likely to make two reasonable readers act differently |
    | Scope | Unrelated bundled work, missing boundaries, over-engineering |
    | Actionability | Whether the intended reader can actually use this document next |

    ## Calibration

    Only flag issues that would cause a real downstream problem.
    Do not block on minor wording, stylistic preferences, or extra polish ideas.
    Approve unless serious gaps remain.

    ## Output Format

    ## Document Review

    **Status:** Approved | Issues Found

    **Issues (if any):**
    - [Section or heading]: [specific issue] - [why it matters]

    **Recommendations (advisory, do not block approval):**
    - [suggestion]
```
