# Integration Contract

`workflow-project-check` is intended to sit between implementation and final verification.

## Upstream Skills

### `workflow-project-spec`

Use it before or during project checks to ensure `docs/workflow/spec/` exists and stays current.

- missing `docs/workflow/spec/` -> initialize with `workflow-project-spec`
- reusable lesson discovered -> update with `workflow-project-spec`

### `workflow-executing-plans`

Call `workflow-project-check` after implementation checkpoints stabilize and before final completion claims.

### `workflow-writing-plans`

Use the likely verification commands and likely spec update targets to strengthen the plan's verification section.

### `workflow-start`

When file paths, repo shape, or a partial diff are already known early, `workflow-start` may reuse the same scope language from `workflow-project-check` to decide whether work stays direct or upgrades into a planned path.

- `docs_only` and `test_only` usually stay light
- `cross_layer`, `contract_change`, `schema_change`, and most `config_change` work should upgrade
- `shared_code_change` should raise the assumed blast radius even when the diff is small

## Downstream Skill

### `workflow-verification-before-completion`

Use it after the check plan is executed.

`workflow-project-check` decides:
- what to verify
- what to read
- which manual checks apply

`workflow-verification-before-completion` decides:
- whether fresh evidence actually exists
- whether completion claims are allowed

## Expected Handoff

The ideal handoff from `workflow-project-check` includes:
- scope summary
- risk tags
- commands to run
- manual checks still pending
- spec update requirement

Do not collapse this into a vague statement like "run tests and lint".
