# Task Routing

Use the lightest path that still preserves quality.

## Default Principles

- Prefer the shortest path that satisfies correctness, verification, and maintainability.
- Check whether work can be parallelized before defaulting to serial execution.
- Do not upgrade a task into a heavier workflow unless the current path stops being sufficient.
- Keep documentation in service of execution. Only persist specs or plans when the user asks, project policy requires it, or the artifact has clear reuse or handoff value.

## Task Classes

### 1. Read-only work

Use direct analysis for:
- code reading
- architecture explanation
- design critique
- question answering
- review without edits

If the task is investigating a real bug or failure and implementation has not started yet, use `workflow-systematic-debugging` before proposing fixes.

### 2. Lightweight implementation

Treat the task as lightweight when most of these are true:
- single file or small local change
- clear bug fix or behavior tweak
- config, copy, test, or small documentation update
- little or no shared API / schema / persistence impact
- direct verification is obvious

Default path:
1. Capture a minimal plan in working memory or brief notes: goal, boundary, risks, verification
2. Implement directly
3. Run targeted verification
4. Use review only if the change is risky, user-requested, or likely to benefit from another pass

Question-asking rule:
- Ask at most one blocking question first
- If the risk is controllable, state the assumption and proceed

### 3. Medium or large implementation

Use a heavier workflow when the task includes one or more of:
- unclear requirements or important product trade-offs
- multi-step implementation across several files or subsystems
- shared logic, public API, schema, persistence, concurrency, or migration impact
- work that benefits from handoff artifacts or cross-session coordination
- validation that is not obvious from a direct test command

Default path:
- use `workflow-brainstorming` when design, boundaries, or trade-offs need active refinement
- use `workflow-writing-plans` when a real execution plan is needed
- prefer `workflow-executing-plans` for complex work that is still mostly sequential
- use `workflow-subagent-driven-development` or `workflow-dispatching-parallel-agents` only when tasks are genuinely independent and the platform supports that mode reliably

## Escalate or De-escalate

Escalate to a heavier process when:
- the change expands beyond the original boundary
- shared contracts or cross-cutting behavior become involved
- verification coverage is weak
- the task stops being locally understandable

De-escalate to a lighter process when:
- the work collapses into a local fix
- the remaining risk is low and verification is direct
- extra documentation or orchestration would cost more than it returns

## Worktree Guidance

Use `workflow-using-git-worktrees` when isolation materially helps:
- current branch is dirty and conflicts with the task
- multiple branches or parallel efforts need isolation
- the change is risky enough that a clean workspace matters

Do not create a worktree by default for routine local changes on the current branch.

## Review and Verification

- Before claiming anything is complete, fixed, or passing, use `workflow-verification-before-completion`.
- Use `workflow-requesting-code-review` for major, risky, or merge-bound changes, or when a fresh pass is likely to catch mistakes.
- Use `workflow-receiving-code-review` when review feedback arrives and needs technical evaluation.
