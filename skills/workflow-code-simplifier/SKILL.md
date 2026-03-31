---
name: workflow-code-simplifier
description: Use when the task is to simplify code, clean up recently changed code, refactor for clarity, or improve readability without changing behavior, especially after tests are green or when non-behavioral cleanup should stay scoped and local
---

# Workflow Code Simplifier

## Overview

Simplify code without changing behavior.

Use it for non-behavioral cleanup after the task boundary is already understood. It complements `workflow-test-driven-development` and `workflow-verification-before-completion`; it does not replace them.

## When to Use

Use this skill when:
- the user asks to "simplify code", "clean up code", "refactor for clarity", or "improve readability"
- the code is already behaviorally correct and the remaining work is readability, consistency, or duplication cleanup
- a plan or TDD cycle has reached a green state and now needs a scoped refactor pass

Do not use this skill when:
- the real task is root-cause investigation; use `workflow-systematic-debugging`
- the change adds behavior or fixes a bug before a failing test exists; use `workflow-test-driven-development`
- the cleanup would widen scope into unrelated files, APIs, contracts, or architecture
- "simplification" is a cover for changing behavior, product decisions, or requirements

## Core Rules

- Preserve exact behavior. If behavior changes, stop and route back to the correct implementation workflow.
- Stay close to recently modified code unless the user explicitly expands scope.
- Prefer explicit, readable code over clever compression or fewer lines.
- Follow repo conventions from local instructions and nearby code.
- Remove redundancy, unnecessary nesting, and obvious comments, but keep helpful structure.
- Re-run the verification that protected the code before the cleanup pass.

## Quick Reference

| Situation | Action |
| --- | --- |
| User explicitly wants cleaner code | Invoke this skill directly |
| TDD has reached green | Use this skill for the REFACTOR step, then re-run tests |
| Cleanup would change behavior or contracts | Stop and route back to planning, debugging, or TDD |

## Refinement Process

1. Identify the touched code and its boundary.
2. Remove duplication, unnecessary nesting, and dense expressions.
3. Improve names, grouping, and control flow when that makes the code easier to read.
4. Keep abstractions only if they still earn their cost.
5. Re-run the relevant verification after the cleanup.

## Example

### Before

```typescript
const status = isLoading ? 'loading' : hasError ? 'error' : isComplete ? 'complete' : 'idle';
```

### After

```typescript
function getStatus(isLoading: boolean, hasError: boolean, isComplete: boolean): string {
  if (isLoading) return 'loading';
  if (hasError) return 'error';
  if (isComplete) return 'complete';
  return 'idle';
}
```

## Common Mistakes

- Mixing cleanup with behavior changes in the same pass
- Refactoring adjacent untouched files "while already here"
- Chasing fewer lines instead of clearer code

## Red Flags

- "I'll clean up this neighboring module too"
- "This small behavior tweak can ride along"
- "The tests passed before the refactor"

These mean stop, rescope, and verify again.
