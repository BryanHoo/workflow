---
name: workflow-project-check
description: Use when code has changed in a project with `docs/workflow/spec/` and you need a project-aware verification plan, including change-scope classification, relevant spec files, cross-layer checks, command suggestions, and whether the project spec should be updated before completion
---

# Project Check

Build a project-aware verification plan after code changes and before completion claims.

This skill does not replace tests, lint, or typecheck. It decides:
- what changed
- which `docs/workflow/spec/` files apply
- which verification commands should run
- which manual cross-layer checks are required
- whether reusable lessons should be written back into spec

Its classification vocabulary is also suitable upstream. When task paths or likely edit areas are already known, `workflow-start` and planning skills may reuse the same risk tags to choose an entry path before implementation begins.

## Core Rules

- Use this skill after code changes exist or when reviewing a diff.
- Require `docs/workflow/spec/`. If it is missing, initialize it first with `workflow-project-spec`.
- Treat this as a check planner, not as a generic code review.
- Pass the resulting command and checklist outputs into `workflow-verification-before-completion` before claiming success.

## Mode 1: Classify Change Scope

Use this first when the task needs scope-aware verification.

Run:

```bash
python3 scripts/classify_change_scope.py --repo "$PWD"
```

Useful options:

```bash
python3 scripts/classify_change_scope.py --repo "$PWD" --task "<task summary>"
python3 scripts/classify_change_scope.py --repo "$PWD" --paths src/api/user.ts src/components/UserForm.tsx
python3 scripts/classify_change_scope.py --repo "$PWD" --package web
python3 scripts/classify_change_scope.py --repo "$PWD" --json
```

The classifier determines:
- single-repo or monorepo mode
- relevant packages
- relevant layers
- changed files
- risk tags such as `cross_layer`, `contract_change`, `schema_change`, `config_change`, `new_file`, `shared_code_change`, `test_only`, or `docs_only`

Read [check-dimensions.md](references/check-dimensions.md) for what each risk tag means.

## Mode 2: Build Check Plan

Use this after classification to produce the actual verification plan.

Run:

```bash
python3 scripts/build_check_plan.py --repo "$PWD"
```

Useful options:

```bash
python3 scripts/build_check_plan.py --repo "$PWD" --task "<task summary>" --json
python3 scripts/build_check_plan.py --repo "$PWD" --paths packages/web/src/routes/users.tsx
python3 scripts/build_check_plan.py --repo "$PWD" --package api
```

The plan returns:
- spec indexes to read
- detailed spec files to read
- suggested verification commands
- manual checks grouped by risk
- whether spec update is required
- likely spec files to update

## Recommended Execution Flow

1. Run `classify_change_scope.py`
2. Run `build_check_plan.py`
3. Read the listed spec files
4. Run the suggested commands
5. Perform the manual checks for any reported risk tags
6. If `requiresSpecUpdate` is true, use `workflow-project-spec` in update mode
7. Only then use `workflow-verification-before-completion`

## When To Escalate

Escalate from local checks to cross-layer checks when any of these are true:
- both frontend and backend layers changed
- API, schema, migration, or contract files changed
- shared helpers, config, or env files changed
- new files were added in shared, core, or routing paths

## Output Expectations

When using this skill, report:
- changed scope summary
- risk tags
- spec files read
- commands run or still pending
- manual checks completed or still pending
- whether spec sync is required before completion

For workflow interaction rules, read [integration-contract.md](references/integration-contract.md).
