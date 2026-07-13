"""Validate packaged Codex skills without relying on a user's Codex install."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


FRONTMATTER = re.compile(r"\A---\r?\n(?P<body>.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
KEY_VALUE = re.compile(r"^(?P<key>[a-zA-Z][\w-]*):\s*(?P<value>.*)$")
REQUIRED_INTERFACE_KEYS = ("display_name", "short_description", "default_prompt")


def parse_flat_yaml(text: str, source: Path) -> dict[str, str]:
    """Parse the flat scalar front matter used by Codex SKILL.md files."""
    values: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = KEY_VALUE.match(line)
        if not match:
            raise ValueError(f"{source}:{number}: unsupported front-matter syntax")
        key, value = match.group("key"), match.group("value").strip()
        if key in values:
            raise ValueError(f"{source}:{number}: duplicate key {key!r}")
        if not value:
            raise ValueError(f"{source}:{number}: {key!r} must have a scalar value")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values


def validate_openai_yaml(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if not re.search(r"(?m)^interface:\s*$", text):
        return [f"{path}: missing interface mapping"]
    for key in REQUIRED_INTERFACE_KEYS:
        match = re.search(rf'(?m)^\s{{2}}{key}:\s+(["\'])(.+)\1\s*$', text)
        if not match or not match.group(2).strip():
            errors.append(f"{path}: missing non-empty interface.{key}")
    policy = re.search(r"(?m)^policy:\s*$", text)
    if policy and not re.search(
        r"(?m)^\s{2}allow_implicit_invocation:\s+(?:true|false)\s*$", text
    ):
        errors.append(f"{path}: policy must declare allow_implicit_invocation")
    return errors


def validate_skill(skill: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill / "SKILL.md"
    if not skill_file.is_file():
        return [f"{skill}: missing SKILL.md"]

    text = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        return [f"{skill_file}: missing YAML front matter"]
    try:
        metadata = parse_flat_yaml(match.group("body"), skill_file)
    except ValueError as error:
        return [str(error)]

    allowed = {"name", "description", "disable-model-invocation"}
    unexpected = sorted(set(metadata) - allowed)
    if unexpected:
        errors.append(f"{skill_file}: unsupported keys: {', '.join(unexpected)}")
    if metadata.get("name") != skill.name:
        errors.append(f"{skill_file}: name must match directory {skill.name!r}")
    description = metadata.get("description", "").strip()
    if not description:
        errors.append(f"{skill_file}: description is required")
    elif len(description) > 1024:
        errors.append(f"{skill_file}: description exceeds 1024 characters")

    openai_yaml = skill / "agents" / "openai.yaml"
    if openai_yaml.is_file():
        errors.extend(validate_openai_yaml(openai_yaml))
    return errors


def compare_packaged_skill(source: Path, candidate: Path) -> list[str]:
    """Require an installed catalog skill to match its packaged source exactly."""
    source_files = {
        path.relative_to(source): path.read_bytes()
        for path in source.rglob("*")
        if path.is_file()
    }
    candidate_files = {
        path.relative_to(candidate): path.read_bytes()
        for path in candidate.rglob("*")
        if path.is_file()
    }
    if source_files == candidate_files:
        return []
    return [f"{candidate}: installed content differs from packaged source"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "skills",
        help="directory containing skills (defaults to this checkout's skills)",
    )
    args = parser.parse_args()
    skills_dir = args.skills_dir.expanduser().resolve()
    if not skills_dir.is_dir():
        print(f"Skills directory not found: {skills_dir}", file=sys.stderr)
        return 2

    source_skills = Path(__file__).resolve().parents[1] / "skills"
    expected_names = sorted(path.name for path in source_skills.iterdir() if path.is_dir())
    skills = [skills_dir / name for name in expected_names]
    if not skills:
        print(f"No skills found in: {skills_dir}", file=sys.stderr)
        return 2

    errors: list[str] = []
    for skill in skills:
        if not skill.is_dir():
            errors.append(f"Missing skill directory: {skill}")
            continue
        errors.extend(validate_skill(skill))
        if skills_dir != source_skills.resolve():
            errors.extend(compare_packaged_skill(source_skills / skill.name, skill))
    for error in errors:
        print(error, file=sys.stderr)
    print(f"VALIDATED_SKILL_COUNT={len(skills)}")
    print(f"VALIDATION_FAILED_COUNT={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
