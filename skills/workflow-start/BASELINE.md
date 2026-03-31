# Baseline Scenarios

These RED-phase scenarios capture why `workflow-start` needs an explicit user-visible routing rule.

## Scenario 1: Internal route selection stays implicit

Prompt:

> Fix this small local bug in one component.

Observed baseline from the current workflow docs before this update:
- `workflow-start` classified the task into a route internally.
- The skill told the agent how to choose the lightest workflow, but not to tell the user which route was selected.
- The agent could begin work immediately with no route announcement.

Failure:
- The user had no visibility into whether the task was being treated as read-only work, debugging, direct local implementation, or a planned path.

## Scenario 2: Route escalation is not explained

Prompt:

> Start with a small fix, then discover it changes a shared contract and touches multiple layers.

Observed baseline from the current workflow docs before this update:
- `references/task-routing.md` explained when to escalate or de-escalate.
- The docs did not require the agent to announce that the route had changed or why.
- Escalation could happen silently as an internal process adjustment.

Failure:
- The user could not see that the workflow had upgraded from a light path to a heavier one, or which risk signal caused that change.
