---
name: workflow-review-doc
description: Review working documents such as specs, implementation plans, requirements, proposals, RFCs, ADRs, and handoff docs before planning, implementation, approval, or delegation. Use when Codex needs a reusable document-review workflow, a reviewer subagent prompt, or a consistent rubric for completeness, consistency, clarity, scope, alignment, and buildability, including inline fallback review in environments without delegation.
---

# Workflow Review Doc

Review documents with a document-first workflow. Start from the actual artifact, calibrate for what would cause real downstream problems, and separate blocking issues from advisory suggestions.

## Review Workflow

1. Identify the review target.
   - Capture the document path, document type, intended reader, and the next action this document must support.
   - Examples: planning, implementation, approval, delegation, stakeholder alignment.
2. Gather source material only when it changes the judgment.
   - Spec reviews may need the requirements source.
   - Plan reviews usually need the spec they implement.
   - Proposal or RFC reviews may need constraints, prior decisions, or linked docs.
3. Calibrate what counts as blocking.
   - Flag only issues that would cause someone to build the wrong thing, make the wrong decision, get stuck, or approve unsafe scope.
   - Do not block on style preferences, mild wording improvements, or extra polish ideas.
4. Choose the narrowest rubric that fits the document.
   - For any document, start with completeness, consistency, clarity, and scope.
   - Add document-specific checks only when needed.
5. Produce a terse verdict.
   - Return `Approved` when the document is usable as-is.
   - Return `Issues Found` when specific blocking problems remain.
   - Keep advisory recommendations separate from blocking issues.

## Dispatch Rules

- Prefer reviewing the raw document and raw reference artifacts instead of summarizing them from memory.
- Do not leak your own conclusions into the reviewer prompt. Give the reviewer the artifact, the purpose, and the rubric.
- Tell the reviewer to approve unless serious gaps exist.
- Ask for file and section references whenever the document format makes that practical.
- If the document is short and the review is straightforward, review it inline instead of dispatching a subagent.
- If the environment does not support subagents, always review inline in the current session and preserve the same blocking-vs-advisory bar.

## Core Review Axes

- **Completeness:** Missing sections, placeholders, omitted prerequisites, or undefined dependencies.
- **Consistency:** Contradictions between sections, mismatched terminology, or conflicting behavior.
- **Clarity:** Ambiguity that could cause different reasonable readers to act differently.
- **Scope:** Overreach, bundled unrelated work, or a document too broad for its intended next step.
- **Alignment:** Drift from the source spec, requirements, or prior decisions.
- **Buildability / Actionability:** Whether the next person can execute without guessing.

## Document-Specific Guidance

- **Spec or requirements doc:** Focus on product scope, architecture boundaries, ambiguity, and whether the spec is ready for planning.
- **Implementation plan:** Focus on coverage of the spec, actionable decomposition, missing steps, placeholders, and whether an implementer could execute without getting stuck.
- **Proposal / RFC / ADR:** Focus on decision framing, alternatives, constraints, consequences, and unresolved risks.
- **Handoff doc:** Focus on operational clarity, assumptions, owner expectations, and next actions.

## Output Shape

Use this structure unless the user requested a different format:

```markdown
## Document Review

**Status:** Approved | Issues Found

**Issues (if any):**
- [Section or heading]: [specific issue] - [why it matters]

**Recommendations (advisory, do not block approval):**
- [suggestion]
```

## References

- Read `references/general-document-review.md` for the reusable generic reviewer prompt.
- Read `references/spec-review-template.md` for spec-oriented review calibration.
- Read `references/plan-review-template.md` for plan-oriented review calibration.
