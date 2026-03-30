#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class PackageInfo:
    name: str
    path: str


@dataclass
class ProjectShape:
    mode: str
    packages: list[PackageInfo]
    layers: list[str]


def repo_path(raw: str | None) -> Path:
    path = Path(raw or ".").expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Repository does not exist: {path}")
    return path


def spec_root(repo: Path) -> Path:
    return repo / "docs" / "workflow" / "spec"


def print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def detect_workspace_packages(repo: Path) -> list[PackageInfo]:
    mapping: dict[str, str] = {}

    package_json = repo / "package.json"
    if package_json.exists():
        data = load_json(package_json)
        workspaces = data.get("workspaces", [])
        if isinstance(workspaces, dict):
            workspaces = workspaces.get("packages", [])
        if isinstance(workspaces, list):
            for pattern in workspaces:
                if isinstance(pattern, str):
                    for item in _expand_workspace_pattern(repo, pattern):
                        mapping[item.name] = item.path

    pnpm_workspace = repo / "pnpm-workspace.yaml"
    if pnpm_workspace.exists():
        for line in pnpm_workspace.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*-\s+['\"]?([^'\"]+)['\"]?\s*$", line)
            if match:
                for item in _expand_workspace_pattern(repo, match.group(1)):
                    mapping[item.name] = item.path

    return [PackageInfo(name=name, path=path) for name, path in sorted(mapping.items())]


def _expand_workspace_pattern(repo: Path, pattern: str) -> Iterable[PackageInfo]:
    if "*" not in pattern:
        target = repo / pattern
        if target.is_dir():
            yield PackageInfo(name=target.name, path=str(target.relative_to(repo)))
        return
    for match in sorted(repo.glob(pattern)):
        if match.is_dir():
            yield PackageInfo(name=match.name, path=str(match.relative_to(repo)))


def scan_existing_spec_shape(repo: Path) -> ProjectShape | None:
    root = spec_root(repo)
    if not root.exists():
        return None

    packages: list[PackageInfo] = []
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
        packages.append(PackageInfo(name=child.name, path=child.name))
        for nested in sorted(child.iterdir()):
            if nested.is_dir():
                layers.add(nested.name)

    return ProjectShape(mode=mode, packages=packages, layers=sorted(layers))


def guess_project_shape(repo: Path) -> ProjectShape:
    existing = scan_existing_spec_shape(repo)
    workspace_packages = detect_workspace_packages(repo)
    if existing:
        if existing.mode == "monorepo" and workspace_packages:
            path_map = {pkg.name: pkg.path for pkg in workspace_packages}
            existing.packages = [
                PackageInfo(name=pkg.name, path=path_map.get(pkg.name, pkg.path))
                for pkg in existing.packages
            ]
        return existing

    packages = workspace_packages
    layers = []
    if _looks_like_backend(repo):
        layers.append("backend")
    if _looks_like_frontend(repo):
        layers.append("frontend")
    if not layers:
        layers = ["backend", "frontend"]
    return ProjectShape(
        mode="monorepo" if packages else "single",
        packages=packages,
        layers=layers,
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


def git_changed_entries(repo: Path) -> list[dict[str, str]]:
    diff_entries = _git_diff_name_status(repo)
    status_entries = _git_status_porcelain(repo)
    merged: dict[str, dict[str, str]] = {}

    # Prefer diff-derived statuses for tracked files, then append status-only
    # entries such as untracked files that `git diff` does not report.
    for entry in diff_entries:
        merged[entry["path"]] = entry
    for entry in status_entries:
        merged.setdefault(entry["path"], entry)

    return list(merged.values())


def _git_diff_name_status(repo: Path) -> list[dict[str, str]]:
    stdout = _run_git(["diff", "--name-status", "--relative", "HEAD"], repo)
    result = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            result.append({"status": parts[0], "path": parts[-1]})
    return result


def _git_status_porcelain(repo: Path) -> list[dict[str, str]]:
    # `-uall` expands untracked directories to file-level paths so follow-up
    # classification can detect config/shared file changes precisely.
    stdout = _run_git(["status", "--porcelain", "--untracked-files=all"], repo)
    result = []
    for line in stdout.splitlines():
        if len(line) < 4:
            continue
        status = line[:2].strip() or "M"
        path = line[3:].strip()
        if path:
            result.append({"status": status, "path": path})
    return result


def _run_git(args: list[str], repo: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout


def detect_layers(paths: list[str], task: str, available_layers: list[str]) -> list[str]:
    lower_text = " ".join(paths + [task]).lower()
    if all(is_doc_path(path) for path in paths if path):
        return []

    layers = set()
    frontend_tokens = ["ui", "component", "hook", "page", "frontend", "react", "css", "tailwind"]
    backend_tokens = ["api", "server", "backend", "db", "database", "migration", "route"]

    if any(token in lower_text for token in frontend_tokens):
        layers.add("frontend")
    if any(token in lower_text for token in backend_tokens):
        layers.add("backend")

    for path in paths:
        lower = path.lower()
        if any(token in lower for token in ["/components/", "/app/", "/pages/", ".tsx", ".jsx"]):
            layers.add("frontend")
        if any(token in lower for token in ["/api/", "/server/", "/routes/", "prisma/", "drizzle/", ".sql"]):
            layers.add("backend")

    ordered = [layer for layer in ["backend", "frontend"] if layer in layers and layer in available_layers]
    return ordered or available_layers


def detect_packages(shape: ProjectShape, forced: str, paths: list[str], task: str) -> list[PackageInfo]:
    if shape.mode == "single":
        return []
    if forced:
        return [pkg for pkg in shape.packages if pkg.name == forced] or [PackageInfo(name=forced, path=forced)]

    hits: list[PackageInfo] = []
    haystack = " ".join(paths + [task]).lower()
    for pkg in shape.packages:
        if pkg.name.lower() in haystack:
            hits.append(pkg)
            continue
        pkg_prefix = f"{pkg.path}/".lower()
        if any(path.lower().startswith(pkg_prefix) for path in paths):
            hits.append(pkg)
    return hits or shape.packages[:1]


def classify_scope(
    repo: Path,
    task: str,
    forced_package: str,
    hinted_paths: list[str],
) -> dict:
    entries = git_changed_entries(repo)
    paths = hinted_paths or [entry["path"] for entry in entries]
    unique_paths = sorted(dict.fromkeys(path for path in paths if path))
    shape = guess_project_shape(repo)
    packages = detect_packages(shape, forced_package, unique_paths, task)
    layers = detect_layers(unique_paths, task, shape.layers)
    tags = detect_risk_tags(unique_paths, entries, layers)

    if "docs_only" in tags:
        check_mode = "docs"
    elif "test_only" in tags:
        check_mode = "tests"
    elif "cross_layer" in tags:
        check_mode = "local+cross-layer"
    else:
        check_mode = "local"

    return {
        "repo": str(repo),
        "mode": shape.mode,
        "packages": [{"name": pkg.name, "path": pkg.path} for pkg in packages],
        "layers": layers,
        "changedFiles": unique_paths,
        "changedEntries": entries,
        "riskTags": sorted(tags),
        "checkMode": check_mode,
    }


def detect_risk_tags(paths: list[str], entries: list[dict[str, str]], layers: list[str]) -> set[str]:
    tags = {"local_quality"}
    if not paths:
        return tags

    if all(is_doc_path(path) for path in paths):
        return {"docs_only"}
    if all(is_test_path(path) for path in paths):
        return {"test_only"}

    if len(layers) > 1:
        tags.add("cross_layer")

    if any(is_contract_path(path) for path in paths):
        tags.add("contract_change")
        tags.add("cross_layer")

    if any(is_schema_path(path) for path in paths):
        tags.add("schema_change")
        tags.add("contract_change")
        tags.add("cross_layer")

    if any(is_config_path(path) for path in paths):
        tags.add("config_change")
        tags.add("cross_layer")

    if any(is_shared_path(path) for path in paths):
        tags.add("shared_code_change")

    if any(entry["status"].startswith("A") or entry["status"] == "??" for entry in entries):
        tags.add("new_file")

    return tags


def is_doc_path(path: str) -> bool:
    lower = path.lower()
    return lower.endswith(".md") or lower.startswith("docs/") or "/docs/" in lower


def is_test_path(path: str) -> bool:
    lower = path.lower()
    return any(
        token in lower
        for token in ["/test/", "/tests/", ".test.", ".spec.", "__tests__", "fixtures/"]
    )


def is_contract_path(path: str) -> bool:
    lower = path.lower()
    return any(
        token in lower
        for token in ["route", "/api/", "handler", "controller", "schema", "dto", "serializer", "graphql"]
    )


def is_schema_path(path: str) -> bool:
    lower = path.lower()
    return any(
        token in lower
        for token in ["migration", "prisma", "drizzle", "/db/", ".sql", "schema.ts", "schema.prisma"]
    )


def is_config_path(path: str) -> bool:
    lower = path.lower()
    config_names = [
        ".env",
        "config",
        "settings",
        "tsconfig",
        "vite.config",
        "next.config",
        "eslint",
        "prettier",
        "vitest.config",
        "jest.config",
    ]
    return any(token in lower for token in config_names)


def is_shared_path(path: str) -> bool:
    lower = path.lower()
    return any(
        token in lower
        for token in ["/shared/", "/common/", "/lib/", "/utils/", "/core/", "/hooks/", "/constants/"]
    )


def collect_spec_files(repo: Path, packages: list[dict], layers: list[str]) -> dict[str, list[str]]:
    root = spec_root(repo)
    indexes: list[str] = []
    files: list[str] = []
    project_docs = [
        str(path.relative_to(repo))
        for path in sorted((root / "project").glob("*.md"))
        if path.is_file()
    ]
    guide_docs = [
        str(path.relative_to(repo))
        for path in sorted((root / "guides").glob("*.md"))
        if path.is_file()
    ]

    if not root.exists():
        return {
            "indexes": [],
            "files": [],
            "projectDocs": project_docs,
            "guideDocs": guide_docs,
        }

    if packages:
        for pkg in packages:
            for layer in layers:
                base = root / pkg["name"] / layer
                index = base / "index.md"
                if index.exists():
                    indexes.append(str(index.relative_to(repo)))
                files.extend(
                    str(path.relative_to(repo))
                    for path in sorted(base.glob("*.md"))
                    if path.is_file() and path.name != "index.md"
                )
    else:
        for layer in layers:
            base = root / layer
            index = base / "index.md"
            if index.exists():
                indexes.append(str(index.relative_to(repo)))
            files.extend(
                str(path.relative_to(repo))
                for path in sorted(base.glob("*.md"))
                if path.is_file() and path.name != "index.md"
            )

    guides_index = root / "guides" / "index.md"
    if guides_index.exists():
        indexes.append(str(guides_index.relative_to(repo)))

    return {
        "indexes": sorted(dict.fromkeys(indexes)),
        "files": sorted(dict.fromkeys(files)),
        "projectDocs": project_docs,
        "guideDocs": guide_docs,
    }


def detect_package_manager(repo: Path) -> str:
    if (repo / "pnpm-lock.yaml").exists() or (repo / "pnpm-workspace.yaml").exists():
        return "pnpm"
    if (repo / "package-lock.json").exists():
        return "npm"
    return "pnpm"


def load_package_scripts(package_dir: Path) -> set[str]:
    data = load_json(package_dir / "package.json")
    scripts = data.get("scripts", {})
    return set(scripts) if isinstance(scripts, dict) else set()
