#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


LAYER_DOCS = {
    "backend": [
        "directory-structure.md",
        "database-guidelines.md",
        "error-handling.md",
        "logging-guidelines.md",
        "quality-guidelines.md",
    ],
    "frontend": [
        "directory-structure.md",
        "component-guidelines.md",
        "hook-guidelines.md",
        "state-management.md",
        "type-safety.md",
        "quality-guidelines.md",
    ],
}

GUIDE_DOCS = [
    "cross-layer-thinking-guide.md",
    "code-reuse-thinking-guide.md",
]

PROJECT_DOCS = [
    "overview.md",
    "commands.md",
    "glossary.md",
]

EXTRACTION_SOURCES = [
    "AGENTS.md",
    "CLAUDE.md",
    "CLAUDE.local.md",
    "CONTRIBUTING.md",
    ".github/copilot-instructions.md",
]


@dataclass
class ProjectShape:
    mode: str
    packages: list[str]
    layers: list[str]


def repo_path(raw: str | None) -> Path:
    path = Path(raw or ".").expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Repository does not exist: {path}")
    return path


def spec_root(repo: Path) -> Path:
    return repo / "docs" / "workflow" / "spec"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str, force: bool = False) -> bool:
    if path.exists() and not force:
        return False
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")
    return True


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def detect_workspace_packages(repo: Path) -> list[str]:
    packages: set[str] = set()

    package_json = repo / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        workspaces = data.get("workspaces", [])
        if isinstance(workspaces, dict):
            workspaces = workspaces.get("packages", [])
        if isinstance(workspaces, list):
            for pattern in workspaces:
                if not isinstance(pattern, str):
                    continue
                packages.update(_expand_workspace_pattern(repo, pattern))

    pnpm_workspace = repo / "pnpm-workspace.yaml"
    if pnpm_workspace.exists():
        for line in pnpm_workspace.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*-\s+['\"]?([^'\"]+)['\"]?\s*$", line)
            if match:
                packages.update(_expand_workspace_pattern(repo, match.group(1)))

    return sorted(packages)


def _expand_workspace_pattern(repo: Path, pattern: str) -> Iterable[str]:
    if "*" not in pattern:
        target = repo / pattern
        if target.is_dir():
            yield target.name
        return
    for match in repo.glob(pattern):
        if match.is_dir():
            yield match.name


def scan_existing_spec_shape(repo: Path) -> ProjectShape | None:
    root = spec_root(repo)
    if not root.exists():
        return None

    packages = []
    layers: set[str] = set()
    mode = "single"
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in {"project", "guides", "backend", "frontend"}:
            if child.name in {"backend", "frontend"}:
                layers.add(child.name)
            continue
        mode = "monorepo"
        packages.append(child.name)
        for nested in child.iterdir():
            if nested.is_dir():
                layers.add(nested.name)

    return ProjectShape(mode=mode, packages=packages, layers=sorted(layers))


def guess_project_shape(
    repo: Path,
    mode: str = "auto",
    packages_arg: list[str] | None = None,
    layers_arg: list[str] | None = None,
) -> ProjectShape:
    existing = scan_existing_spec_shape(repo)
    if existing:
        return existing

    packages = packages_arg or detect_workspace_packages(repo)
    if mode == "single":
        packages = []
    elif mode == "monorepo" and not packages:
        packages = ["app"]

    detected_layers = set(layers_arg or [])
    if not detected_layers:
        if _looks_like_frontend(repo):
            detected_layers.add("frontend")
        if _looks_like_backend(repo):
            detected_layers.add("backend")
    if not detected_layers:
        detected_layers = {"backend", "frontend"}

    return ProjectShape(
        mode="monorepo" if packages else "single",
        packages=sorted(packages),
        layers=sorted(detected_layers),
    )


def _looks_like_frontend(repo: Path) -> bool:
    markers = [
        "src/components",
        "app",
        "pages",
        "vite.config.ts",
        "next.config.js",
        "next.config.mjs",
    ]
    return any((repo / marker).exists() for marker in markers)


def _looks_like_backend(repo: Path) -> bool:
    markers = [
        "src/server",
        "src/api",
        "server",
        "api",
        "prisma",
        "drizzle",
    ]
    return any((repo / marker).exists() for marker in markers)


def find_cursor_rules(repo: Path) -> list[Path]:
    rules_dir = repo / ".cursor" / "rules"
    if not rules_dir.is_dir():
        return []
    return sorted(
        path for path in rules_dir.rglob("*") if path.is_file() and not path.name.startswith(".")
    )


def read_extraction_sources(repo: Path) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for rel in EXTRACTION_SOURCES:
        path = repo / rel
        if path.is_file():
            items.append((rel, path.read_text(encoding="utf-8")))
    for path in find_cursor_rules(repo):
        items.append((str(path.relative_to(repo)), path.read_text(encoding="utf-8")))
    return items


def normalize_title(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned or "Untitled Rule"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "entry"


def print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
