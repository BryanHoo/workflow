# Spec Layout

Use `docs/workflow/spec/` as a lightweight, durable context layer for project-specific implementation knowledge.

## Directory Shapes

### Single-repo

```text
docs/workflow/spec/
├── project/
│   ├── overview.md
│   ├── commands.md
│   └── glossary.md
├── backend/
│   ├── index.md
│   ├── directory-structure.md
│   ├── database-guidelines.md
│   ├── error-handling.md
│   ├── logging-guidelines.md
│   └── quality-guidelines.md
├── frontend/
│   ├── index.md
│   ├── directory-structure.md
│   ├── component-guidelines.md
│   ├── hook-guidelines.md
│   ├── state-management.md
│   ├── type-safety.md
│   └── quality-guidelines.md
└── guides/
    ├── index.md
    ├── cross-layer-thinking-guide.md
    └── code-reuse-thinking-guide.md
```

### Monorepo

```text
docs/workflow/spec/
├── project/
├── guides/
├── api/
│   └── backend/
└── web/
    └── frontend/
```

Package directories are the first level below `docs/workflow/spec/`. Shared guides and project docs stay global.

## What Goes Where

### `project/`

Use for repo-wide context that other files depend on:
- product and architecture overview
- important commands
- domain glossary
- entry points and ownership boundaries

### `backend/` and `frontend/`

Use for implementation rules:
- file placement
- contract shape
- naming and typing rules
- review and testing requirements
- anti-patterns and common mistakes

### `guides/`

Use for thinking aids:
- cross-layer checks
- reuse checks
- rollout and migration prompts

Keep guides shorter and more checklist-oriented than code-spec files.

## Index Contract

Each layer directory should have an `index.md` that:
- lists the available documents
- tells the agent what to read before development
- points to the most important files first

The index is navigation, not the entire source of truth.

## Scope Rules

- Prefer shared project docs unless package behavior truly differs.
- Prefer package-specific layers in monorepos when commands, APIs, or conventions differ.
- Read shared `guides/` together with package-specific layer docs.
- Avoid duplicating the same rule into every package. Put shared rules in `project/` or `guides/`.
