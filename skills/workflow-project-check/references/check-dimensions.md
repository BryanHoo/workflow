# Check Dimensions

`workflow-project-check` uses risk tags to decide which verification dimensions apply.

## Core Dimensions

### `local_quality`

Apply when code changed in a single layer and there is no strong cross-layer signal.

Check:
- lint
- typecheck
- package tests
- relevant layer quality guidelines

### `cross_layer`

Apply when multiple layers changed or a change likely propagates across boundaries.

Check:
- call path from entry point to side effect
- type or schema continuity
- error handling across boundaries
- caller and callee both updated

### `contract_change`

Apply when routes, APIs, handlers, schemas, DTOs, serializers, or request-response shapes change.

Check:
- request fields
- response fields
- validation
- callers updated
- contract-related spec sync

### `schema_change`

Apply when migrations, ORM schema files, SQL, repository models, or storage shape changes occur.

Check:
- migration exists when needed
- query call sites still match
- tests cover new shape
- database guideline docs need updates

### `config_change`

Apply when `.env`, config files, feature flags, build config, or deployment settings change.

Check:
- all consumers updated
- defaults and validation are correct
- local and CI commands still work
- commands or project overview docs need updates

### `shared_code_change`

Apply when shared utilities, constants, hooks, helpers, core modules, or common libraries change.

Check:
- impact radius
- duplicate implementations
- naming and placement consistency
- whether more call sites need updates

### `new_file`

Apply when a new source file is added.

Check:
- import paths
- correct directory placement
- whether the abstraction belongs in shared or local scope
- whether spec should mention the new pattern

### `test_only`

Apply when all changed files are tests or fixtures.

Check:
- test intent matches the change
- no production assumptions became stale
- broader cross-layer checks are usually unnecessary

### `docs_only`

Apply when all changed files are docs or markdown assets.

Check:
- links and commands are still correct
- if docs describe code behavior, verify they match reality

## Escalation Guidance

- `contract_change`, `schema_change`, `config_change`, and `shared_code_change` usually imply `requiresSpecUpdate`
- `test_only` and `docs_only` usually do not
- `cross_layer` means manual checks are mandatory even if tests pass
