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

    def test_native_retry_contract_rejects_negation(self) -> None:
        contract = (ROOT / "skills" / "grilling" / "NATIVE-INPUT.md").read_text(
            encoding="utf-8"
        )
        negated = contract.replace(
            "Repeat without a retry limit",
            "Do not repeat without a retry limit",
        )
        self.assertFalse(checks.has_canonical_native_retry_lifecycle(negated))

    def test_native_contract_requires_english_controls(self) -> None:
        contract = (ROOT / "skills" / "grilling" / "NATIVE-INPUT.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual([], checks.native_input_text_errors(contract))
        missing_label = contract.replace("Approve (Recommended)", "Approve")
        self.assertNotEqual([], checks.native_input_text_errors(missing_label))
        for former_label in checks.FORMER_NATIVE_LABELS:
            with self.subTest(former_label=former_label):
                changed = contract + "\n" + former_label
                self.assertNotEqual([], checks.native_input_text_errors(changed))

    def test_approval_protocol_requires_exact_english_approval(self) -> None:
        protocol = (
            ROOT
            / "skills"
            / "prompt-review-and-dispatch"
            / "references"
            / "approval-protocol.md"
        ).read_text(encoding="utf-8")
        self.assertEqual([], checks.approval_protocol_errors(protocol))
        normalized = " ".join(protocol.split())
        for rule in checks.APPROVAL_RULES:
            with self.subTest(rule=rule):
                changed = normalized.replace(rule, "removed", 1)
                self.assertNotEqual([], checks.approval_protocol_errors(changed))

    def test_skill_catalog_matches_directories(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        skills = sorted(path.name for path in (ROOT / "skills").iterdir() if path.is_dir())
        for skill in skills:
            self.assertIn(f"`{skill}`", readme)


if __name__ == "__main__":
    unittest.main()
