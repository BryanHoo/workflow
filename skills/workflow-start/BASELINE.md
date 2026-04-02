# Baseline Scenarios

These RED-phase scenarios capture why the old `workflow-start` routing model needed a full rewrite instead of another local tweak.

## Scenario 1: Most implementation work collapses into only two paths

Prompt:

> Update shared validation logic used by two callers, add one regression test, and keep the change easy to review.

Observed baseline from the old routing docs:
- The top-level taxonomy was `read-only analysis`, `debugging or failure investigation`, `direct local implementation`, and `planned implementation`.
- In practice, implementation work was forced into either `direct local implementation` or `planned implementation`.
- There was no stable middle route for bounded but non-trivial work such as shared-code edits, multi-file local changes, or caller-callee continuity checks.

Failure:
- The agent could under-route the task as a local change or over-route it into the same bucket used for much heavier work.
- The routing model did not provide a distinct implementation path with its own verification bar for medium-complexity changes.

## Scenario 2: Heavy work shares the same path as routine planned work

Prompt:

> Change a shared contract, update config defaults, and coordinate the rollout across multiple layers.

Observed baseline from the old routing docs:
- `planned implementation` covered both moderate coordination work and genuinely heavy, cross-layer work.
- The docs named optional supporting skills, but did not define a separate heavy route with stronger expectations for design clarity, planning, and verification.
- The result was a wide bucket where the route name stayed the same even when the blast radius changed significantly.

Failure:
- The routing system lacked a dedicated heavy implementation lane.
- High-risk work could be handled with the same ceremony as medium work, weakening correctness and maintainability guarantees.

## Scenario 3: Debugging is a route, but not a bridge into implementation tiers

Prompt:

> Investigate a flaky failure, identify the cause, then implement the fix safely.

Observed baseline from the old routing docs:
- `debugging or failure investigation` was treated as its own first-class route.
- The docs did not clearly say how to re-enter implementation after the cause was understood.
- That left the transition from diagnosis to execution implicit.

Failure:
- After debugging, the agent had no explicit instruction to choose between lightweight, medium, or heavy implementation.
- Correct diagnosis could still lead to inconsistent execution rigor.

## Scenario 4: Route selection and route changes are not visible enough to the user

Prompt:

> Start with a small fix, then discover it changes a shared contract and touches multiple layers.

Observed baseline from the old routing docs:
- `references/task-routing.md` discussed escalation and de-escalation.
- `workflow-start` mentioned user-visible routing, but the vocabulary still centered on the old route names rather than a clean three-tier implementation model.
- A route change could still read like an internal process adjustment instead of a visible shift in execution rigor.

Failure:
- The user could not reliably tell whether the task was currently being handled as lightweight, medium, or heavy implementation.
- The route announcement did not expose the intended verification and coordination bar clearly enough.

## Scenario 5: Cross-layer work is still easy to keep in medium too long

Prompt:

> Add tenant-level notification preferences across UI, API, and worker processing, keep backward compatibility, and support staged rollout.

Observed baseline from the current routing docs:
- The core principle repeatedly says to choose the lightest path and only upgrade when the current path stops being sufficient.
- Shared signals describe `cross_layer`, `contract_change`, and rollout-sensitive `config_change` as often heavy, but not with a hard tie-break rule.
- Medium guidance can be interpreted as acceptable as long as a short checklist exists, even when the checklist hides cross-layer coupling risk.

Failure:
- The agent can rationalize starting in `medium implementation` and delay `heavy implementation` until after code-level surprises appear.
- Heavy-grade planning and verification can start too late for changes that already had rollout and compatibility risk at triage time.

## Scenario 6: Heavy tasks can skip brainstorming through false certainty

Prompt:

> Redesign sync conflict resolution across mobile client, backend API, and persistence model, including migration safety and rollback strategy.

Observed baseline from the current routing docs:
- Heavy guidance says to use `workflow-brainstorming` when requirements or trade-offs are unclear, but does not define stronger triggers for ambiguous high-impact decisions.
- The docs emphasize avoiding unnecessary brainstorming and ceremony, which is useful for small work but leaves room to skip design discussion in risky work.
- Red flags warn against forcing brainstorming on everything, but do not include the opposite warning about skipping brainstorming despite unresolved architecture choices.

Failure:
- The agent can claim the design is already clear and proceed without an explicit option/trade-off pass.
- High-impact implementation can start without validating boundaries, migration assumptions, or rollback shape with the user.

## GREEN Verification Replay (After Rule Updates)

### Replay A: tenant notification preferences across UI/API/worker with staged rollout

Expected route after updates:
- classify as `heavy implementation` at entry because `cross_layer` + contract/compatibility + rollout-sensitive concerns combine into non-light signals
- use `workflow-brainstorming` if compatibility, rollout, or option trade-offs are still unresolved
- proceed to `workflow-writing-plans` only after design assumptions are explicit

### Replay B: conflict-resolution redesign with migration and rollback safety

Expected route after updates:
- classify as `heavy implementation` due migration and persistence risk
- trigger `workflow-brainstorming` by default because trade-offs and rollback shape are architecture-level decisions
- freeze execution plan only after brainstorming clarifies boundaries and verification strategy
