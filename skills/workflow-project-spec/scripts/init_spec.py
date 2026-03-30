#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    GUIDE_DOCS,
    LAYER_DOCS,
    PROJECT_DOCS,
    guess_project_shape,
    print_json,
    read_extraction_sources,
    repo_path,
    spec_root,
    write_text,
)

AGENTS_BLOCK_START = "<!-- WORKFLOW-PROJECT-SPEC:START -->"
AGENTS_BLOCK_END = "<!-- WORKFLOW-PROJECT-SPEC:END -->"


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize docs/workflow/spec")
    parser.add_argument("--repo", default=".", help="Target repository root")
    parser.add_argument(
        "--mode",
        choices=["auto", "single", "monorepo"],
        default="auto",
        help="Spec layout mode",
    )
    parser.add_argument(
        "--packages",
        default="",
        help="Comma-separated package names for monorepo mode",
    )
    parser.add_argument(
        "--layers",
        default="",
        help="Comma-separated layers to create: backend,frontend",
    )
    parser.add_argument(
        "--no-extract",
        action="store_true",
        help="Skip importing hints from existing repo instructions",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    repo = repo_path(args.repo)
    packages = [item.strip() for item in args.packages.split(",") if item.strip()]
    layers = [item.strip() for item in args.layers.split(",") if item.strip()]
    shape = guess_project_shape(repo, mode=args.mode, packages_arg=packages, layers_arg=layers)
    created: list[str] = []
    skipped: list[str] = []
    updated: list[str] = []

    root = spec_root(repo)
    root.mkdir(parents=True, exist_ok=True)

    created += _write_project_docs(repo, shape, force=args.force, extract=not args.no_extract)
    created += _write_guides(repo, force=args.force)

    if shape.mode == "single":
        for layer in shape.layers:
            made, kept = _write_layer(repo, root / layer, layer, force=args.force)
            created += made
            skipped += kept
    else:
        for package in shape.packages:
            for layer in shape.layers:
                made, kept = _write_layer(
                    repo,
                    root / package / layer,
                    layer,
                    force=args.force,
                )
                created += made
                skipped += kept

    # Keep a lightweight entrypoint in AGENTS.md so future sessions discover the spec tree.
    agents_result = _write_agents_doc(repo, shape)
    if agents_result == "created":
        created.append("AGENTS.md")
    elif agents_result == "updated":
        updated.append("AGENTS.md")

    summary = {
        "repo": str(repo),
        "mode": shape.mode,
        "packages": shape.packages,
        "layers": shape.layers,
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "extractedSources": [] if args.no_extract else [name for name, _ in read_extraction_sources(repo)],
    }

    if args.json:
        print_json(summary)
        return

    print(f"Initialized spec in {root}")
    print(f"Mode: {shape.mode}")
    if shape.packages:
        print(f"Packages: {', '.join(shape.packages)}")
    print(f"Layers: {', '.join(shape.layers)}")
    if created:
        print("Created:")
        for item in created:
            print(f"- {item}")
    if updated:
        print("Updated:")
        for item in updated:
            print(f"- {item}")
    if skipped:
        print("Skipped existing:")
        for item in skipped:
            print(f"- {item}")


def _write_project_docs(repo: Path, shape, force: bool, extract: bool) -> list[str]:
    root = spec_root(repo)
    created: list[str] = []
    project_dir = root / "project"
    project_dir.mkdir(parents=True, exist_ok=True)

    extracted = read_extraction_sources(repo) if extract else []
    extracted_block = _render_extracted_sources(extracted)

    mapping = {
        "overview.md": _project_overview(shape.mode, shape.packages, extracted_block),
        "commands.md": _project_commands(),
        "glossary.md": _project_glossary(),
    }
    for name in PROJECT_DOCS:
        path = project_dir / name
        if write_text(path, mapping[name], force=force):
            created.append(str(path.relative_to(repo)))
    return created


def _write_guides(repo: Path, force: bool) -> list[str]:
    root = spec_root(repo)
    guides_dir = root / "guides"
    guides_dir.mkdir(parents=True, exist_ok=True)
    docs = {
        "index.md": _guides_index(),
        "cross-layer-thinking-guide.md": _cross_layer_guide(),
        "code-reuse-thinking-guide.md": _code_reuse_guide(),
    }
    created: list[str] = []
    for name in GUIDE_DOCS + ["index.md"]:
        path = guides_dir / name
        if write_text(path, docs[name], force=force):
            created.append(str(path.relative_to(repo)))
    return created


def _write_layer(
    repo: Path,
    layer_dir: Path,
    layer: str,
    force: bool,
) -> tuple[list[str], list[str]]:
    layer_dir.mkdir(parents=True, exist_ok=True)
    docs = _layer_docs(layer)
    created: list[str] = []
    skipped: list[str] = []
    for name, content in docs.items():
        path = layer_dir / name
        if write_text(path, content, force=force):
            created.append(str(path.relative_to(repo)))
        else:
            skipped.append(str(path.relative_to(repo)))
    return created, skipped


def _write_agents_doc(repo: Path, shape) -> str | None:
    agents_path = repo / "AGENTS.md"
    block = _agents_block(shape)
    existing = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    updated = _upsert_managed_block(existing, block)
    if updated == existing:
        return None
    agents_path.write_text(updated, encoding="utf-8")
    return "updated" if existing else "created"


def _upsert_managed_block(existing: str, block: str) -> str:
    # Replace only the managed block and leave any user-authored instructions untouched.
    if AGENTS_BLOCK_START in existing and AGENTS_BLOCK_END in existing:
        start = existing.index(AGENTS_BLOCK_START)
        end = existing.index(AGENTS_BLOCK_END) + len(AGENTS_BLOCK_END)
        before = existing[:start].rstrip()
        after = existing[end:].lstrip()
        parts = [part for part in [before, block, after] if part]
        return "\n\n".join(parts) + "\n"

    cleaned = existing.strip()
    if cleaned:
        return f"{cleaned}\n\n{block}\n"
    return f"{block}\n"


def _agents_block(shape) -> str:
    shared_docs = [
        "docs/workflow/spec/project/overview.md",
        "docs/workflow/spec/project/commands.md",
        "docs/workflow/spec/guides/index.md",
        "docs/workflow/spec/project/glossary.md",
    ]
    layer_indexes = _layer_index_paths(shape)
    shared_rows = "\n".join(f"- `{path}`" for path in shared_docs)
    layer_rows = "\n".join(f"- `{path}`" for path in layer_indexes)
    return f"""{AGENTS_BLOCK_START}
# Workflow Project Spec

This repository keeps durable implementation context in `docs/workflow/spec/`.

When a task needs project-specific context:
1. Read `docs/workflow/spec/project/overview.md`.
2. Read `docs/workflow/spec/project/commands.md`.
3. Read `docs/workflow/spec/guides/index.md`.
4. Read the relevant layer index listed below.
5. Read only the detailed spec files linked from those indexes.
6. Read `docs/workflow/spec/project/glossary.md` when domain language is ambiguous.

## Shared Spec Entry Points

{shared_rows}

## Available Layer Indexes

{layer_rows}

Keep this managed block so `workflow-project-spec` can refresh the spec entry points after re-initialization.
{AGENTS_BLOCK_END}"""


def _layer_index_paths(shape) -> list[str]:
    if shape.mode == "single":
        return [f"docs/workflow/spec/{layer}/index.md" for layer in shape.layers]

    paths: list[str] = []
    for package in shape.packages:
        for layer in shape.layers:
            paths.append(f"docs/workflow/spec/{package}/{layer}/index.md")
    return paths


def _layer_docs(layer: str) -> dict[str, str]:
    if layer == "backend":
        return {
            "index.md": _backend_index(),
            "directory-structure.md": _generic_doc("Backend Directory Structure"),
            "database-guidelines.md": _generic_doc("Database Guidelines"),
            "error-handling.md": _generic_doc("Error Handling"),
            "logging-guidelines.md": _generic_doc("Logging Guidelines"),
            "quality-guidelines.md": _generic_doc("Backend Quality Guidelines"),
        }
    return {
        "index.md": _frontend_index(),
        "directory-structure.md": _generic_doc("Frontend Directory Structure"),
        "component-guidelines.md": _generic_doc("Component Guidelines"),
        "hook-guidelines.md": _generic_doc("Hook Guidelines"),
        "state-management.md": _generic_doc("State Management"),
        "type-safety.md": _generic_doc("Type Safety"),
        "quality-guidelines.md": _generic_doc("Frontend Quality Guidelines"),
    }


def _render_extracted_sources(items: list[tuple[str, str]]) -> str:
    if not items:
        return "_No extraction sources found. Fill this section from the codebase._"
    sections = []
    for name, content in items:
        summary = "\n".join(
            line.strip() for line in content.splitlines() if line.strip()
        )
        clipped = summary[:800].strip()
        sections.append(f"## Source: `{name}`\n\n{clipped}")
    return "\n\n".join(sections)


def _project_overview(mode: str, packages: list[str], extracted_block: str) -> str:
    package_line = ", ".join(packages) if packages else "single-repo"
    return f"""# Project Overview

## Current Shape

- Mode: `{mode}`
- Packages: {package_line}

## What This Project Builds

Describe the product, primary users, and high-level architecture here.

## Entry Points

- Main app or service:
- Background jobs or workers:
- Tests and verification entry points:

## Extracted Hints

{extracted_block}

## Manual Tightening Needed

- Replace generic placeholders with concrete file examples.
- Remove anything that conflicts with current code.
- Add ownership boundaries and important integration points.
"""


def _project_commands() -> str:
    return """# Project Commands

Document the commands future sessions need before they change code.

## Setup

- Install:
- Dev server:

## Verification

- Unit tests:
- Lint:
- Typecheck:
- Build:

## Deployment or Release Notes

- Local preview:
- Release checklist:
"""


def _project_glossary() -> str:
    return """# Project Glossary

Capture domain terms, abbreviations, and important internal names.

## Terms

- Example term:
- Example acronym:
"""


def _guides_index() -> str:
    return """# Shared Guides

Use these guides together with project and layer specs.

## Guides

- [Cross-Layer Thinking Guide](./cross-layer-thinking-guide.md)
- [Code Reuse Thinking Guide](./code-reuse-thinking-guide.md)
"""


def _cross_layer_guide() -> str:
    return """# Cross-Layer Thinking Guide

Before implementing a multi-layer change, check:

- commands or APIs that call into the changed path
- config keys, env vars, and feature flags
- database and migration impact
- serialization and validation boundaries
- tests that prove the full path still works
"""


def _code_reuse_guide() -> str:
    return """# Code Reuse Thinking Guide

Before adding new code, check:

- whether the repo already has the same abstraction
- whether a package-local helper should stay local
- whether a shared helper would create accidental coupling
- whether extraction now will simplify future work
"""


def _backend_index() -> str:
    rows = "\n".join(
        f"- [{name.replace('.md', '').replace('-', ' ').title()}](./{name})"
        for name in LAYER_DOCS["backend"]
    )
    return f"""# Backend Spec Index

Read these before backend implementation.

## Pre-Development Checklist

{rows}
"""


def _frontend_index() -> str:
    rows = "\n".join(
        f"- [{name.replace('.md', '').replace('-', ' ').title()}](./{name})"
        for name in LAYER_DOCS["frontend"]
    )
    return f"""# Frontend Spec Index

Read these before frontend implementation.

## Pre-Development Checklist

{rows}
"""


def _generic_doc(title: str) -> str:
    return f"""# {title}

Describe the project's actual rules here.

## Current Convention

- Add concrete rules
- Add real file examples

## Anti-Patterns

- Record what to avoid and why

## Verification Notes

- List commands or checks that prove compliance
"""


if __name__ == "__main__":
    main()
