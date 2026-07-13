from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
assert SPEC and SPEC.loader
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


class ValidationTests(unittest.TestCase):
    def test_all_packaged_skills_are_valid(self) -> None:
        skills = sorted((ROOT / "skills").iterdir())
        failures = [error for skill in skills if skill.is_dir() for error in validate.validate_skill(skill)]
        self.assertEqual([], failures)

    def test_directory_name_must_match_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "wrong-name"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: actual-name\ndescription: A useful skill.\n---\n",
                encoding="utf-8",
            )
            self.assertTrue(any("name must match" in error for error in validate.validate_skill(skill)))

    def test_description_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "missing-description"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: missing-description\ndescription: \"\"\n---\n",
                encoding="utf-8",
            )
            self.assertTrue(any("description is required" in error for error in validate.validate_skill(skill)))


if __name__ == "__main__":
    unittest.main()
