---
name: workflow-project-spec
description: Use when a project needs durable reusable implementation context in `docs/workflow/spec/`, including initializing spec files from an existing repo, loading only the relevant spec documents before planning or coding, and updating those specs after new conventions, contracts, or gotchas are discovered
---

# Project Spec

Create and maintain project-scoped spec files that give future sessions high-signal context without dragging in a heavyweight framework.

Use `docs/workflow/spec/` as the durable home for:
- project overview and commands
- backend and frontend implementation conventions
- shared engineering guides
- monorepo package-specific variants when needed

## Core Rules

- Treat `docs/workflow/spec/` as user-owned project knowledge. Do not overwrite existing files unless explicitly told or `--force` is used.
- Read index files first, then load only the detailed files relevant to the current task.
- Update specs when a task establishes a reusable rule, contract, or non-obvious lesson. Do not churn specs for trivial edits.
- Keep specs concrete. Prefer commands, paths, signatures, examples, anti-patterns, and verification notes over abstract principles.

## Modes

### 1. Initialize spec

Use when a repo does not yet have `docs/workflow/spec/`, or when it needs a first pass generated from existing project instructions.

Run:

```bash
python3 scripts/init_spec.py --repo "$PWD"
```

Useful options:

```bash
python3 scripts/init_spec.py --repo "$PWD" --mode monorepo
python3 scripts/init_spec.py --repo "$PWD" --packages api,web,docs
python3 scripts/init_spec.py --repo "$PWD" --layers backend,frontend
python3 scripts/init_spec.py --repo "$PWD" --no-extract
python3 scripts/init_spec.py --repo "$PWD" --force
```

What it does:
- creates a single-repo or monorepo `docs/workflow/spec/` skeleton
- creates `project/`, `guides/`, and relevant layer folders
- adds or refreshes a managed `AGENTS.md` block that points future sessions at the generated spec entry points
- attempts to extract initial context from `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md`, `CONTRIBUTING.md`, `.github/copilot-instructions.md`, and `.cursor/rules/`
- never overwrites existing spec content unless `--force` is passed

After initialization:
- read the generated files
- tighten placeholders using real code examples from the repo
- remove sections that do not apply

For file layout and scope rules, read [spec-layout.md](references/spec-layout.md).
For extraction behavior and source priority, read [extraction-sources.md](references/extraction-sources.md).

### 2. Load relevant spec

Use before brainstorming, planning, or coding so the task starts with repo-specific context.

Run:

```bash
python3 scripts/detect_spec_scope.py --repo "$PWD" --task "<task summary>"
```

Or use path hints:

```bash
python3 scripts/detect_spec_scope.py --repo "$PWD" --paths src/api/users.ts tests/users.test.ts
```

The script returns:
- detected project mode
- relevant packages
- relevant spec indexes
- detailed files to read next

Load order:
1. read the reported `index.md` files
2. read the detailed files listed under `files`
3. use only those constraints in planning or implementation

If the result is ambiguous:
- pass `--package <name>` in monorepos
- add better path hints
- fall back to reading shared guides plus the most likely package layer

### 3. Update spec

Use after implementation, debugging, or review when the work produced a reusable decision.

Run:

```bash
python3 scripts/update_spec.py \
  --repo "$PWD" \
  --target docs/workflow/spec/backend/error-handling.md \
  --title "Common mistake: API handlers swallow validation errors" \
  --summary "Validation errors must be mapped to 400 responses and logged once at the boundary." \
  --example-file src/server/routes/user.ts \
  --kind gotcha
```

You can also update package-scoped specs:

```bash
python3 scripts/update_spec.py \
  --repo "$PWD" \
  --target docs/workflow/spec/web/frontend/state-management.md \
  --title "Convention: async form state lives in route-level actions" \
  --summary "Do not duplicate submission state in local component state when the route action already owns the lifecycle." \
  --kind convention
```

Update process:
1. read the target spec file first
2. confirm the lesson is reusable and non-trivial
3. append a focused section with the script
4. if a new file or category was introduced, pass `--index-file`, `--index-label`, and `--index-description` so the corresponding `index.md` stays navigable

For update criteria and protection policy, read [update-policy.md](references/update-policy.md).

## Single-Repo vs Monorepo

- Single-repo: `docs/workflow/spec/backend`, `docs/workflow/spec/frontend`, `docs/workflow/spec/guides`, `docs/workflow/spec/project`
- Monorepo: `docs/workflow/spec/<package>/backend`, `docs/workflow/spec/<package>/frontend`, shared `docs/workflow/spec/guides`, shared `docs/workflow/spec/project`

Use package-scoped specs only when different packages really have different conventions. Do not create needless duplication.

## Practical Routing

- New repo or missing spec: initialize first
- Planning or coding in a repo with specs: load first
- Finished a feature and learned something reusable: update before handing off

## Output Expectations

When using this skill, report:
- which mode you used
- which spec files were created, read, or updated
- any ambiguity in package scope
- any follow-up manual tightening still needed
