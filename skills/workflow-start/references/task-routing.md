# Task Routing

Use the lightest safe path that still preserves correctness, verification, and maintainability. When risk signals are ambiguous, bias toward earlier escalation and de-escalate only after boundaries are clear.

## Routing Model

Separate task type from implementation weight:

- `read-only analysis` means no edits
- `debugging or failure investigation` means diagnose first, then re-enter implementation through the correct tier
- implementation work must be classified into exactly one tier: `lightweight implementation`, `medium implementation`, or `heavy implementation`

This avoids collapsing most changes into only two execution paths.

## Default Principles

- Prefer the shortest path that still satisfies correctness, verification, and maintainability.
- Do not skip the medium tier by forcing bounded multi-file or shared-code work into either a local fix or a heavyweight planning flow.
- If uncertainty exists between `medium implementation` and `heavy implementation`, choose `heavy implementation` first and de-escalate later with evidence.
- Escalate based on known risk signals before coding; do not wait for implementation surprises to reveal that the route was too light.
- Keep documentation in service of execution. Persist specs or plans only when the user asks, project policy requires it, or the artifact has clear reuse or handoff value.
- Use one routing vocabulary from entry to completion so early triage and final verification talk about the same thing.
- Once the route is chosen, state the selected route and the concrete reason to the user before substantial work begins.
- If the route escalates or de-escalates later, state the new route and the reason for the change.

## Route Families

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
1. Use `workflow-systematic-debugging` before proposing implementation changes.
2. Capture the failing behavior, reproduction path, or missing evidence.
3. Once the likely cause is understood, explicitly reclassify the implementation as `lightweight`, `medium`, or `heavy`.

Treat debugging as a first-class route, not as an implementation tier.

## Implementation Tiers

### 1. Lightweight implementation

Use this tier when most of these are true:
- single file or very tight local cluster
- clear behavior tweak, narrow bug fix, or bounded non-behavioral cleanup
- docs, copy, tests, or small config work with limited blast radius
- no shared API, schema, persistence, migration, or rollout concern
- direct verification is obvious from one focused command or scenario
- no durable plan or explicit checkpoint list is needed

Default path:
1. Capture a minimal inline note: goal, boundary, main risk, verification.
2. If the task changes behavior and a failing automated check is practical, prefer `workflow-test-driven-development`.
3. If the task is explicitly readability-only cleanup or code simplification, use `workflow-code-simplifier`.
4. Implement directly in the current session.
5. Run targeted verification.
6. Use review only if the risk grows, the user asked for it, or the change becomes merge-bound.

Verification bar:
- targeted checks cover the changed surface
- manual verification is acceptable only when automated coverage is impractical and the scenario is stated explicitly
- if the boundary stops being local, escalate to `medium implementation`

### 2. Medium implementation

Use this tier when one or more of these are true:
- multiple related files change, but the work still fits inside one bounded slice
- shared code changes, but the blast radius is understandable
- caller-callee continuity, bounded contract change, or non-trivial config impact matters
- sequencing matters enough that a short explicit checklist is safer than ad hoc execution
- verification needs multiple focused checks instead of one obvious command
- design is mostly clear, but `lightweight implementation` is too loose
- impacted boundaries and verification checkpoints can be named before coding

Default path:
1. Write a short explicit inline plan or checklist covering files, risks, and verification checkpoints.
2. If the task changes behavior and a failing automated check is practical, prefer `workflow-test-driven-development` within the checkpoints.
3. Execute sequentially checkpoint by checkpoint in the current session.
4. Verify each checkpoint before moving on.
5. Use `workflow-writing-plans` only if the inline checklist stops being sufficient.
6. Use review when shared code, caller-callee continuity, or merge risk makes a second pass worthwhile.

Do not keep work in `medium implementation` when rollout strategy, migration safety, or architecture choice is still unresolved. Those are `heavy implementation` + `workflow-brainstorming` triggers.

Verification bar:
- each checkpoint has a concrete command or scenario
- caller-callee continuity, config continuity, or shared-code behavior is checked where relevant
- final verification covers the bounded subsystem, not just the last edited file
- if the work grows into cross-layer coordination, public contract changes, schema changes, or unclear design, escalate to `heavy implementation`

### 3. Heavy implementation

Use this tier when one or more of these are true:
- requirements, boundaries, or product trade-offs are still unclear
- multiple subsystems or layers must change together
- public or widely shared contracts are changing
- schema, persistence, migration, concurrency, rollout, or environment-wide config impact is involved
- durable planning or handoff artifacts have clear value
- verification spans multiple checkpoints, layers, or environments and is not obvious from a direct local command
- two or more medium-or-higher risk signals appear together and at least one boundary is uncertain

Default path:
- use `workflow-brainstorming` by default when design, boundaries, migration choices, or trade-offs need active refinement
- use `workflow-writing-plans` when a real execution plan is needed
- prefer `workflow-executing-plans` for the default sequential implementation path
- use `workflow-project-spec` whenever repo-specific implementation context should be initialized, loaded, or refreshed from `docs/workflow/spec/`
- use `workflow-using-git-worktrees` only when isolation materially reduces risk
- use `workflow-requesting-code-review` when the change is major, risky, or merge-bound

Heavy implementation is defined by stronger planning and verification requirements, not by defaulting to subagents.

Verification bar:
- execution follows explicit checkpoints instead of implicit local reasoning
- cross-layer behavior, compatibility, and rollout-sensitive paths are verified where relevant
- schema or persistence changes include compatibility or migration validation
- if the remaining work collapses into a bounded subsystem slice, de-escalate to `medium implementation`

## User-visible Route Announcement

When the route is determined:
1. Name the route explicitly.
2. State the concrete signals that selected it.
3. Use the active session language policy when phrasing the explanation.
4. Keep the explanation brief and actionable.
5. If debugging turns into implementation, announce both the transition and the selected implementation tier.

Good examples:
- "当前走 lightweight implementation，因为改动边界局部、验证路径直接，而且没有 shared contract 信号。"
- "当前走 medium implementation，因为会改动 shared code 和调用方校验逻辑，虽然范围受控，但不能按单文件修补处理。"
- "当前走 heavy implementation，因为这个改动涉及 cross-layer coordination、config rollout 和更高的验证要求。"

Bad examples:
- "我先按合适的流程处理。"
- "我会开始处理这个任务。"

The point is visibility: routing should be understandable to the user, not just correct internally.

## Shared Routing Signals

When task paths, a diff, or known files are available, reuse the same dimensions as `workflow-project-check`.

- `docs_only` or `test_only`: usually stay `lightweight` unless the user explicitly asks for broader process
- `cross_layer`: usually `heavy`; keep it at `medium` only when boundaries are explicit, caller impact is known, and rollout risk is low
- `contract_change`: upgrade to at least `medium`; use `heavy` when the contract is public, widely shared, has unknown caller impact, or needs compatibility strategy
- `schema_change`: usually `heavy`
- `config_change`: usually at least `medium`; use `heavy` when the config affects rollout, environments, or multiple layers
- `shared_code_change`: treat as at least `medium` even if the diff is mechanically small
- `new_file`: reconsider abstraction boundaries; often at least `medium` when the new file introduces reusable behavior
- two or more non-light signals together (`shared_code_change`, `cross_layer`, `contract_change`, `config_change`, `schema_change`) should default to `heavy` at entry

If `workflow-project-check` would later produce `checkMode=local+cross-layer`, the task usually should not have stayed `lightweight`.

## Behavior vs Cleanup

- behavior change: prefer TDD or debugging-first flow when a failing check or reproduction is practical
- non-behavioral cleanup after green: keep the route as light as the boundary allows, and use `workflow-code-simplifier` for the cleanup pass

## Escalate or De-escalate

Escalate from `lightweight` to `medium` when:
- the change expands beyond a tight local boundary
- shared code or caller-callee continuity becomes relevant
- verification needs multiple focused checks

Escalate from `medium` to `heavy` when:
- requirements or design boundaries become unclear
- cross-layer coordination or public contract changes appear
- schema, persistence, migration, rollout, or environment-wide config impact appears
- durable planning artifacts become necessary
- the checklist no longer captures boundaries, compatibility assumptions, or verification scope with confidence

If medium vs heavy is uncertain, escalate first and de-escalate only after ambiguity is removed.

De-escalate from `heavy` to `medium` when:
- design questions are resolved
- the remaining work is a bounded subsystem slice with explicit checkpoints

De-escalate from `medium` to `lightweight` when:
- the work collapses back into a local fix
- the remaining risk is low and verification is once again direct

## Worktree Guidance

Use `workflow-using-git-worktrees` when isolation materially helps:
- current branch is dirty and conflicts with the task
- multiple branches need isolation
- the change is risky enough that a clean workspace matters

Do not create a worktree by default for routine `lightweight` or `medium` changes.

## Review and Verification

- Before claiming anything is complete, fixed, or passing, use `workflow-verification-before-completion`.
- Use `workflow-requesting-code-review` for `heavy` changes, and for `medium` changes when a fresh pass is likely to catch shared-code or continuity issues.
- Use `workflow-receiving-code-review` when review feedback arrives and needs technical evaluation.
