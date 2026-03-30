#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    classify_scope,
    collect_spec_files,
    detect_package_manager,
    load_package_scripts,
    print_json,
    repo_path,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a project-aware verification plan")
    parser.add_argument("--repo", default=".", help="Target repository root")
    parser.add_argument("--task", default="", help="Task summary")
    parser.add_argument("--package", default="", help="Force package name")
    parser.add_argument("--paths", nargs="*", default=[], help="Changed or relevant paths")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    repo = repo_path(args.repo)
    scope = classify_scope(repo, args.task, args.package, args.paths)
    spec = collect_spec_files(repo, scope["packages"], scope["layers"])
    commands = build_commands(repo, scope)
    manual_checks = build_manual_checks(scope["riskTags"])
    requires_spec_update = should_require_spec_update(scope)
    spec_targets = suggest_spec_targets(scope, spec["files"])

    result = {
        "repo": str(repo),
        "scope": {
            "mode": scope["mode"],
            "packages": scope["packages"],
            "layers": scope["layers"],
            "riskTags": scope["riskTags"],
            "checkMode": scope["checkMode"],
            "changedFiles": scope["changedFiles"],
        },
        "specIndexes": spec["indexes"],
        "specFiles": prioritize_spec_files(spec["files"]),
        "projectDocs": spec["projectDocs"],
        "guideDocs": spec["guideDocs"],
        "commands": commands,
        "manualChecks": manual_checks,
        "requiresSpecUpdate": requires_spec_update,
        "specUpdateTargets": spec_targets,
    }

    if args.json:
        print_json(result)
        return

    print(f"Check mode: {scope['checkMode']}")
    if result["specIndexes"]:
        print("Spec indexes:")
        for item in result["specIndexes"]:
            print(f"- {item}")
    if result["specFiles"]:
        print("Spec files:")
        for item in result["specFiles"]:
            print(f"- {item}")
    if result["commands"]:
        print("Suggested commands:")
        for cmd in result["commands"]:
            print(f"- {cmd}")
    if result["manualChecks"]:
        print("Manual checks:")
        for item in result["manualChecks"]:
            print(f"- {item}")
    print(f"Requires spec update: {'yes' if requires_spec_update else 'no'}")
    if spec_targets:
        print("Likely spec update targets:")
        for item in spec_targets:
            print(f"- {item}")


def build_commands(repo: Path, scope: dict) -> list[str]:
    manager = detect_package_manager(repo)
    packages = scope["packages"]
    commands: list[str] = []

    if scope["riskTags"] == ["docs_only"]:
        return []

    if not packages:
        commands.extend(_package_commands(repo, ".", manager))
        return dedupe(commands)

    for pkg in packages:
        commands.extend(_package_commands(repo, pkg["path"], manager))
    return dedupe(commands)


def _package_commands(repo: Path, package_path: str, manager: str) -> list[str]:
    package_dir = repo if package_path == "." else repo / package_path
    scripts = load_package_scripts(package_dir)
    if not scripts:
        return []

    prefix = "pnpm" if manager == "pnpm" else "npm run"
    if package_path != "." and manager == "pnpm":
        prefix = f"pnpm --dir {package_path}"

    commands: list[str] = []
    for script_name in ["lint", "typecheck", "check-types", "test", "build"]:
        if script_name in scripts:
            commands.append(f"{prefix} {script_name}")
    return commands


def build_manual_checks(risk_tags: list[str]) -> list[str]:
    checks: list[str] = []
    if "cross_layer" in risk_tags:
        checks.extend(
            [
                "Trace data and control flow across all touched layers.",
                "Confirm callers and callees were updated together.",
                "Check error handling and loading states at each boundary.",
            ]
        )
    if "contract_change" in risk_tags:
        checks.extend(
            [
                "Confirm request and response field names still match all consumers.",
                "Check validation, serialization, and API callers for drift.",
            ]
        )
    if "schema_change" in risk_tags:
        checks.extend(
            [
                "Confirm migrations, schema definitions, and query call sites are aligned.",
                "Check seed data or fixtures if the storage shape changed.",
            ]
        )
    if "config_change" in risk_tags:
        checks.extend(
            [
                "Check env keys, defaults, and all config consumers.",
                "Verify local and CI command assumptions still hold.",
            ]
        )
    if "shared_code_change" in risk_tags:
        checks.extend(
            [
                "Check impact radius for shared helpers, constants, or utilities.",
                "Search for duplicate logic or missed update sites.",
            ]
        )
    if "new_file" in risk_tags:
        checks.extend(
            [
                "Confirm the new file belongs in this directory and abstraction layer.",
                "Check import paths and dependency direction.",
            ]
        )
    if "test_only" in risk_tags:
        checks.append("Confirm the tests still describe current behavior instead of stale assumptions.")

    return dedupe(checks)


def should_require_spec_update(scope: dict) -> bool:
    tags = set(scope["riskTags"])
    if "docs_only" in tags or "test_only" in tags:
        return False
    return bool(tags.intersection({"cross_layer", "contract_change", "schema_change", "config_change", "shared_code_change"}))


def suggest_spec_targets(scope: dict, spec_files: list[str]) -> list[str]:
    tags = set(scope["riskTags"])
    layers = scope["layers"]
    changed_files = scope["changedFiles"]
    targets: list[str] = []

    if "schema_change" in tags:
        targets.extend(_matching_spec_files(spec_files, "database-guidelines.md"))
    if "contract_change" in tags:
        targets.extend(_matching_spec_files(spec_files, "error-handling.md"))
        targets.extend(_matching_spec_files(spec_files, "quality-guidelines.md"))
    if "config_change" in tags:
        targets.extend(_matching_project_like_targets(spec_files, changed_files))
    if "shared_code_change" in tags and "frontend" in layers:
        targets.extend(_matching_spec_files(spec_files, "component-guidelines.md"))
        targets.extend(_matching_spec_files(spec_files, "state-management.md"))
    if "shared_code_change" in tags and "backend" in layers:
        targets.extend(_matching_spec_files(spec_files, "directory-structure.md"))
        targets.extend(_matching_spec_files(spec_files, "quality-guidelines.md"))
    if "cross_layer" in tags:
        targets.extend(_matching_spec_files(spec_files, "quality-guidelines.md"))

    return dedupe(targets)


def _matching_spec_files(spec_files: list[str], suffix: str) -> list[str]:
    return [path for path in spec_files if path.endswith(suffix)]


def _matching_project_like_targets(spec_files: list[str], changed_files: list[str]) -> list[str]:
    matches = [path for path in spec_files if path.endswith("quality-guidelines.md")]
    if any("state" in path.lower() or "store" in path.lower() for path in changed_files):
        matches.extend([path for path in spec_files if path.endswith("state-management.md")])
    return matches


def prioritize_spec_files(spec_files: list[str]) -> list[str]:
    def priority(path: str) -> tuple[int, str]:
        if path.endswith("quality-guidelines.md"):
            return (0, path)
        if path.endswith("error-handling.md"):
            return (1, path)
        if path.endswith("database-guidelines.md"):
            return (2, path)
        if path.endswith("state-management.md"):
            return (3, path)
        return (4, path)

    return sorted(spec_files, key=priority)


def dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


if __name__ == "__main__":
    main()
