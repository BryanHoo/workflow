# Task Routing

Use the lightest path that still preserves quality.

## Default Principles

- Prefer the shortest path that satisfies correctness, verification, and maintainability.
- Check whether work can be parallelized before defaulting to serial execution.
- Do not upgrade a task into a heavier workflow unless the current path stops being sufficient.
- Keep documentation in service of execution. Only persist specs or plans when the user asks, project policy requires it, or the artifact has clear reuse or handoff value.
- Use one classification vocabulary from entry to completion. When task paths, diff, or repo shape are available, reuse the same signals later surfaced by `workflow-project-check`.

## Task Classes

### 1. Read-only analysis

Use direct analysis for:
- code reading
- architecture explanation
- design critique
- question answering
- review without edits

### 2. Debugging or failure investigation

Use a debugging-first path when the task is about:
- a real bug, regression, flaky test, or production failure
- a mismatch between expected and actual behavior
- diagnosing a cause before deciding on the fix

Default path:
1. Use `workflow-systematic-debugging` before proposing implementation changes
2. Capture the failing behavior, reproduction path, or missing evidence
3. Only move into implementation once the likely cause is understood

Treat debugging as a first-class route, not just a subtype of implementation.

### 3. Direct local implementation

Treat the task as direct local implementation when most of these are true:
- single file or small local change
- clear bug fix, behavior tweak with obvious boundary, or non-behavioral cleanup
- config, copy, test, or small documentation update with limited blast radius
- little or no shared API / schema / persistence / config impact
- direct verification is obvious
- no strong cross-layer or shared-contract signal

Default path:
1. Capture a minimal plan in working memory or brief notes: goal, boundary, risks, verification
2. If the task changes behavior and a failing automated check can be written first, prefer `workflow-test-driven-development`
3. Implement directly
4. Run targeted verification
5. Use review only if the change is risky, user-requested, or likely to benefit from another pass

Question-asking rule:
- Ask at most one blocking question first
- If the risk is controllable, state the assumption and proceed

### 4. Planned implementation

Use a planned path when the task includes one or more of:
- unclear requirements or important product trade-offs
- multi-step implementation across several files or subsystems
- shared logic, public API, schema, persistence, concurrency, migration, or config impact
- explicit cross-layer coordination between callers and callees
- work that benefits from handoff artifacts or cross-session coordination
- validation that is not obvious from a direct test command

Default path:
- use `workflow-brainstorming` when design, boundaries, or trade-offs need active refinement
- use `workflow-writing-plans` when a real execution plan is needed
- prefer `workflow-executing-plans` for complex work that is still mostly sequential
- use `workflow-subagent-driven-development` or `workflow-dispatching-parallel-agents` only when tasks are genuinely independent and the platform supports that mode reliably

## Shared Routing Signals

When task paths, a diff, or known files are available, reuse the same dimensions as `workflow-project-check`.

- `docs_only` or `test_only`: usually stay on the direct path unless the user explicitly asks for broader process
- `cross_layer`: upgrade to planned implementation and require cross-layer verification later
- `contract_change`: upgrade to planned implementation and verify caller-callee continuity
- `schema_change`: upgrade to planned implementation and treat storage compatibility as part of the design
- `config_change`: usually upgrade to planned implementation unless the scope is demonstrably local
- `shared_code_change`: treat as at least medium risk even if the edit is mechanically small
- `new_file`: reconsider placement, abstraction boundary, and whether the new pattern should remain local

If `workflow-project-check` would later produce `checkMode=local+cross-layer`, the task usually should not have stayed on the lightest direct path.

## Behavior vs Cleanup

- Behavior change: prefer TDD or debugging-first flow when a failing check or reproduction is practical
- Non-behavioral cleanup after green: keep the path light if the boundary remains local and verification is still direct

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

When in doubt, prefer explicit escalation for contract, schema, config, and cross-layer work; prefer de-escalation for docs-only, test-only, and narrow cleanup work.

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
