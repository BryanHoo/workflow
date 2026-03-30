#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import classify_scope, git_changed_entries


class GitChangedEntriesTests(unittest.TestCase):
    def test_includes_untracked_files_alongside_tracked_changes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workflow-project-check-") as tmp:
            repo = Path(tmp)
            (repo / "src" / "api").mkdir(parents=True)
            (repo / "src" / "shared").mkdir(parents=True)

            self._git(repo, "init")
            self._git(repo, "config", "user.email", "test@example.com")
            self._git(repo, "config", "user.name", "Test User")

            tracked_file = repo / "src" / "api" / "users.ts"
            tracked_file.write_text("export const users = [];\n", encoding="utf-8")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-m", "init")

            tracked_file.write_text("export const users = [{ id: 1 }];\n", encoding="utf-8")
            untracked_file = repo / "src" / "shared" / "config.ts"
            untracked_file.write_text('export const API_URL = "x";\n', encoding="utf-8")

            entries = git_changed_entries(repo)
            paths = {entry["path"] for entry in entries}
            statuses = {entry["path"]: entry["status"] for entry in entries}

            self.assertEqual(paths, {"src/api/users.ts", "src/shared/config.ts"})
            self.assertEqual(statuses["src/shared/config.ts"], "??")

            scope = classify_scope(repo, task="", forced_package="", hinted_paths=[])

            self.assertEqual(
                scope["changedFiles"],
                ["src/api/users.ts", "src/shared/config.ts"],
            )
            self.assertIn("new_file", scope["riskTags"])
            self.assertIn("config_change", scope["riskTags"])
            self.assertIn("shared_code_change", scope["riskTags"])

    def _git(self, repo: Path, *args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
