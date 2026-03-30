#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import normalize_title, read_text, repo_path, slugify


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a focused spec update")
    parser.add_argument("--repo", default=".", help="Target repository root")
    parser.add_argument("--target", required=True, help="Target markdown file")
    parser.add_argument("--title", required=True, help="Section title")
    parser.add_argument("--summary", required=True, help="Short reusable lesson")
    parser.add_argument(
        "--kind",
        choices=["convention", "decision", "pattern", "gotcha", "contract"],
        default="convention",
        help="Section type",
    )
    parser.add_argument(
        "--example-file",
        action="append",
        default=[],
        help="Concrete file path example",
    )
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="Verification or usage command example",
    )
    parser.add_argument("--index-file", help="Optional index file to update")
    parser.add_argument("--index-label", help="Optional label for the index entry")
    parser.add_argument(
        "--index-description",
        help="Optional description for the index entry",
    )
    parser.add_argument("--force", action="store_true", help="Create target file if missing")
    args = parser.parse_args()

    repo = repo_path(args.repo)
    target = Path(args.target)
    if not target.is_absolute():
        target = (repo / target).resolve()

    if not target.exists() and not args.force:
        raise SystemExit(f"Target does not exist: {target}. Read or create it intentionally first.")

    if not target.parent.exists():
        target.parent.mkdir(parents=True, exist_ok=True)

    if not target.exists():
        target.write_text(f"# {target.stem.replace('-', ' ').title()}\n", encoding="utf-8")

    existing = read_text(target)
    title = normalize_title(args.title)
    anchor = slugify(title)
    if title in existing:
        raise SystemExit(f"Section already exists: {title}")

    section = render_section(
        title=title,
        kind=args.kind,
        summary=args.summary.strip(),
        example_files=args.example_file,
        commands=args.command,
    )
    with target.open("a", encoding="utf-8") as handle:
        if not existing.endswith("\n"):
            handle.write("\n")
        handle.write(f"\n<!-- workflow-project-spec:{anchor} -->\n")
        handle.write(section)
        if not section.endswith("\n"):
            handle.write("\n")

    if args.index_file:
        _update_index(
            repo=repo,
            index_file=args.index_file,
            target=target,
            label=args.index_label or title,
            description=args.index_description or summary,
        )

    print(f"Updated {target.relative_to(repo)}")
    print(f"Added section: {title}")


def render_section(
    title: str,
    kind: str,
    summary: str,
    example_files: list[str],
    commands: list[str],
) -> str:
    labels = {
        "convention": "Convention",
        "decision": "Design Decision",
        "pattern": "Pattern",
        "gotcha": "Common Mistake",
        "contract": "Contract Rule",
    }
    display_title = _strip_existing_prefix(title, labels[kind])
    lines = [f"## {labels[kind]}: {display_title}", "", summary, ""]

    if example_files:
        lines.append("### Examples")
        lines.extend(f"- `{item}`" for item in example_files)
        lines.append("")

    if commands:
        lines.append("### Verification")
        lines.extend(f"- `{item}`" for item in commands)
        lines.append("")

    lines.append("### Why This Matters")
    lines.append("- Explain the failure mode or future confusion this section prevents.")
    lines.append("")
    return "\n".join(lines)


def _update_index(
    repo: Path,
    index_file: str,
    target: Path,
    label: str,
    description: str,
) -> None:
    index_path = Path(index_file)
    if not index_path.is_absolute():
        index_path = (repo / index_path).resolve()
    if not index_path.exists():
        raise SystemExit(f"Index file does not exist: {index_path}")

    existing = read_text(index_path)
    relative_target = target.relative_to(index_path.parent)
    relative_text = str(relative_target).replace("\\", "/")
    if not relative_text.startswith("."):
        relative_text = f"./{relative_text}"
    bullet = f"- [{label}]({relative_text}) | {description}"
    if bullet in existing:
        return

    with index_path.open("a", encoding="utf-8") as handle:
        if not existing.endswith("\n"):
            handle.write("\n")
        handle.write(f"\n{bullet}\n")


def _strip_existing_prefix(title: str, label: str) -> str:
    prefix = f"{label}:"
    if title.startswith(prefix):
        return title[len(prefix):].strip()
    return title


if __name__ == "__main__":
    main()
