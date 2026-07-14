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
    def assert_skill_error(self, name: str, skill_file: str, expected: str) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / name
            skill.mkdir()
            (skill / "SKILL.md").write_text(skill_file, encoding="utf-8")
            self.assertTrue(
                any(expected in error for error in validate.validate_skill(skill))
            )

    def test_all_packaged_skills_are_valid(self) -> None:
        skills = sorted((ROOT / "skills").iterdir())
        failures = [error for skill in skills if skill.is_dir() for error in validate.validate_skill(skill)]
        self.assertEqual([], failures)

    def test_packaged_comparison_includes_empty_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            candidate = Path(temporary) / "candidate"
            (source / "empty").mkdir(parents=True)
            candidate.mkdir()

            self.assertTrue(validate.compare_packaged_skill(source, candidate))
            (candidate / "empty").mkdir()
            self.assertEqual([], validate.compare_packaged_skill(source, candidate))

    def test_directory_name_must_match_skill_name(self) -> None:
        self.assert_skill_error(
            "wrong-name",
            "---\nname: actual-name\ndescription: A useful skill.\n---\n",
            "name must match",
        )

    def test_skill_name_must_be_bounded_lowercase_kebab_case(self) -> None:
        self.assert_skill_error(
            "Bad--Name",
            "---\nname: Bad--Name\ndescription: A useful skill.\n---\n",
            "lowercase kebab-case",
        )
        long_name = "a" * 65
        self.assert_skill_error(
            long_name,
            f"---\nname: {long_name}\ndescription: A useful skill.\n---\n",
            "at most 64 characters",
        )

    def test_description_is_required(self) -> None:
        self.assert_skill_error(
            "missing-description",
            '---\nname: missing-description\ndescription: ""\n---\n',
            "description is required",
        )

    def test_unterminated_quoted_description_is_rejected(self) -> None:
        self.assert_skill_error(
            "bad-quote",
            '---\nname: bad-quote\ndescription: "unterminated\n---\n',
            "invalid quoted string",
        )

    def test_malformed_plain_scalar_is_rejected(self) -> None:
        self.assert_skill_error(
            "bad-plain-scalar",
            "---\nname: bad-plain-scalar\ndescription: [unterminated\n---\n",
            "unsupported plain scalar",
        )

    def test_disable_model_invocation_must_be_boolean(self) -> None:
        self.assert_skill_error(
            "bad-policy",
            "---\nname: bad-policy\ndescription: Test.\ndisable-model-invocation: banana\n---\n",
            "must be a boolean",
        )

    def test_interface_fields_cannot_live_under_another_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "openai.yaml"
            path.write_text(
                'interface:\nother:\n  display_name: "Wrong"\n  short_description: "Wrong"\n  default_prompt: "Wrong"\n',
                encoding="utf-8",
            )
            errors = validate.validate_openai_yaml(path)
            self.assertTrue(any("interface.display_name" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
