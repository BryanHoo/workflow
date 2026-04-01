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
