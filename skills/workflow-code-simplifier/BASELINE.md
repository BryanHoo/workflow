# Baseline Scenarios

These RED-phase scenarios capture why `workflow-code-simplifier` was needed before the skill existed.

## Scenario 1: Explicit simplify request

Prompt:

> Simplify the recently changed code without changing behavior.

Observed baseline from the current workflow docs before this skill:
- `workflow-start` routed the task to a generic lightweight implementation path with no dedicated simplification rule.
- No workflow skill explicitly covered readability-only cleanup.
- The agent had no workflow-level cue to invoke a dedicated simplification pass.

Failure:
- Simplification remained an ad hoc behavior instead of a reusable workflow step.

## Scenario 2: TDD reaches green

Prompt:

> The failing test is green. Now clean up the implementation for readability only.

Observed baseline from the current workflow docs before this skill:
- `workflow-test-driven-development` said "REFACTOR - Clean Up" but did not connect that phase to a reusable workflow skill.
- `workflow-executing-plans` and `workflow-writing-plans` had no named checkpoint for behavior-preserving cleanup after green.

Failure:
- Cleanup timing was implied, but the workflow had no dedicated skill for how and when to perform it.
