# Update Policy

Spec updates are for durable project knowledge, not session logs.

## Update When

Update specs when a task establishes:
- a reusable convention
- a contract boundary or signature rule
- a non-obvious bug pattern
- a review rule that keeps recurring
- a cross-layer dependency that future changes must respect

## Do Not Update When

Skip updates for:
- typos and copy edits
- one-off local hacks
- obvious fixes with no reusable lesson
- temporary migration notes that will immediately disappear

## Protection Rules

- Never rewrite the whole spec tree during a routine update.
- Never overwrite an existing file without explicit user intent or `--force`.
- Prefer appending a focused section to the correct existing file.
- Read the target file before updating to avoid duplication.
- If a new file must be introduced, add it intentionally and then update the relevant `index.md`.

## Quality Bar

Each update should include:
- a precise title
- a short explanation of the rule
- why it matters
- at least one file or command example when available

Keep sections compact. A spec file should help future implementation, not become a diary.
