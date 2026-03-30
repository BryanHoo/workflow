#!/usr/bin/env python3
from __future__ import annotations

import argparse

from common import classify_scope, print_json, repo_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify changed scope for project checks")
    parser.add_argument("--repo", default=".", help="Target repository root")
    parser.add_argument("--task", default="", help="Task summary")
    parser.add_argument("--package", default="", help="Force package name")
    parser.add_argument("--paths", nargs="*", default=[], help="Changed or relevant paths")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    repo = repo_path(args.repo)
    result = classify_scope(repo, args.task, args.package, args.paths)

    if args.json:
        print_json(result)
        return

    print(f"Mode: {result['mode']}")
    if result["packages"]:
        print("Packages:")
        for pkg in result["packages"]:
            print(f"- {pkg['name']} ({pkg['path']})")
    if result["layers"]:
        print(f"Layers: {', '.join(result['layers'])}")
    print(f"Check mode: {result['checkMode']}")
    if result["riskTags"]:
        print(f"Risk tags: {', '.join(result['riskTags'])}")
    if result["changedFiles"]:
        print("Changed files:")
        for path in result["changedFiles"]:
            print(f"- {path}")


if __name__ == "__main__":
    main()
