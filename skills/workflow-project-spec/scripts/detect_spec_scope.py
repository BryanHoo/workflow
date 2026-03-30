#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    LAYER_DOCS,
    guess_project_shape,
    print_json,
    repo_path,
    spec_root,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect relevant spec files")
    parser.add_argument("--repo", default=".", help="Target repository root")
    parser.add_argument("--task", default="", help="Task summary")
    parser.add_argument("--package", default="", help="Force package name")
    parser.add_argument("--paths", nargs="*", default=[], help="Changed or relevant paths")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    repo = repo_path(args.repo)
    shape = guess_project_shape(repo)
    root = spec_root(repo)

    packages = _detect_packages(shape, args.package, args.paths, args.task)
    layers = _detect_layers(args.paths, args.task, shape.layers)
    files = []
    indexes = []

    if shape.mode == "single":
        indexes.extend(_existing(root / layer / "index.md", repo) for layer in layers)
        for layer in layers:
            files.extend(_layer_files(root / layer, layer, repo))
    else:
        shared_guides = root / "guides" / "index.md"
        for package in packages:
            for layer in layers:
                indexes.append(_existing(root / package / layer / "index.md", repo))
                files.extend(_layer_files(root / package / layer, layer, repo))
        if shared_guides.exists():
            indexes.append(str(shared_guides.relative_to(repo)))

    project_docs = [
        str(path.relative_to(repo))
        for path in (root / "project").glob("*.md")
        if path.is_file()
    ]
    guide_files = [
        str(path.relative_to(repo))
        for path in (root / "guides").glob("*.md")
        if path.is_file()
    ]

    result = {
        "repo": str(repo),
        "mode": shape.mode,
        "packages": packages,
        "layers": layers,
        "indexes": [item for item in indexes if item],
        "projectDocs": sorted(project_docs),
        "guideDocs": sorted(guide_files),
        "files": sorted(set(files)),
    }

    if args.json:
        print_json(result)
        return

    print(f"Mode: {shape.mode}")
    if packages:
        print(f"Packages: {', '.join(packages)}")
    print(f"Layers: {', '.join(layers)}")
    if result["indexes"]:
        print("Indexes:")
        for item in result["indexes"]:
            print(f"- {item}")
    if result["projectDocs"]:
        print("Project docs:")
        for item in result["projectDocs"]:
            print(f"- {item}")
    if result["guideDocs"]:
        print("Guide docs:")
        for item in result["guideDocs"]:
            print(f"- {item}")
    if result["files"]:
        print("Detailed files:")
        for item in result["files"]:
            print(f"- {item}")


def _detect_packages(shape, forced: str, paths: list[str], task: str) -> list[str]:
    if shape.mode == "single":
        return []
    if forced:
        return [forced]

    hits = []
    haystack = " ".join(paths + [task]).lower()
    for package in shape.packages:
        if package.lower() in haystack:
            hits.append(package)
    return hits or shape.packages[:1]


def _detect_layers(paths: list[str], task: str, available_layers: list[str]) -> list[str]:
    text = " ".join(paths + [task]).lower()
    layers = set()
    frontend_tokens = ["ui", "component", "hook", "page", "frontend", "react", "css", "tailwind"]
    backend_tokens = ["api", "server", "backend", "db", "database", "migration", "route"]

    if any(token in text for token in frontend_tokens):
        layers.add("frontend")
    if any(token in text for token in backend_tokens):
        layers.add("backend")

    for path in paths:
        lower = path.lower()
        if any(part in lower for part in ["/components/", "/app/", "/pages/", ".tsx", ".jsx"]):
            layers.add("frontend")
        if any(part in lower for part in ["/api/", "/server/", "/routes/", "prisma/", "drizzle/"]):
            layers.add("backend")

    resolved = [layer for layer in ["backend", "frontend"] if layer in layers and layer in available_layers]
    return resolved or available_layers


def _layer_files(base: Path, layer: str, repo: Path) -> list[str]:
    names = LAYER_DOCS.get(layer, [])
    result = []
    for name in names:
        path = base / name
        if path.exists():
            result.append(str(path.relative_to(repo)))
    return result


def _existing(path: Path, repo: Path) -> str | None:
    return str(path.relative_to(repo)) if path.exists() else None


if __name__ == "__main__":
    main()
