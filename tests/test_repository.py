from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_repository", ROOT / "scripts" / "check_repository.py"
)
assert SPEC and SPEC.loader
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


class RepositoryTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self) -> None:
        self.assertEqual([], checks.check_links())

    def test_old_repository_url_is_absent(self) -> None:
        self.assertEqual([], checks.check_identity())

    def test_workflows_use_least_privilege_and_pinned_actions(self) -> None:
        self.assertEqual([], checks.check_workflows())

    def test_installers_use_documented_isolatable_destination(self) -> None:
        self.assertEqual([], checks.check_install_destinations())

    def test_native_decisions_share_one_enforced_contract(self) -> None:
        self.assertEqual([], checks.check_native_input_contract())

    def test_skill_catalog_matches_directories(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        skills = sorted(path.name for path in (ROOT / "skills").iterdir() if path.is_dir())
        for skill in skills:
            self.assertIn(f"`{skill}`", readme)


if __name__ == "__main__":
    unittest.main()
