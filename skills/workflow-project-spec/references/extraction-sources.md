# Extraction Sources

Initialization can draft a first-pass spec from existing repository instructions.

## Source Priority

Read sources in this order when they exist:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `CLAUDE.local.md`
4. `CONTRIBUTING.md`
5. `.github/copilot-instructions.md`
6. files under `.cursor/rules/`

These sources are heuristics, not truth. The generated spec must be tightened against actual code.

## What To Extract

Pull only durable implementation context:
- required commands
- path conventions
- naming rules
- framework choices
- testing and review expectations
- warnings and anti-patterns

Do not copy:
- conversational framing
- duplicated policy boilerplate
- temporary task instructions
- user-specific notes

## Destination Mapping

- repo overview and workflow notes -> `project/overview.md`
- command and verification rules -> `project/commands.md`
- backend conventions -> `backend/*.md` or `<package>/backend/*.md`
- frontend conventions -> `frontend/*.md` or `<package>/frontend/*.md`
- cross-cutting checklists -> `guides/*.md`

## Required Human Pass

After extraction:
- remove generic filler
- add real file examples
- fix any stale or conflicting instructions
- mark unknowns explicitly instead of guessing
