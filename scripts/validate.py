"""Validate packaged Codex skills without relying on a user's Codex install."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys


FRONTMATTER = re.compile(r"\A---\r?\n(?P<body>.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
KEY_VALUE = re.compile(r"^(?P<key>[a-zA-Z][\w-]*):(?P<value>.*)$")
REQUIRED_INTERFACE_KEYS = ("display_name", "short_description", "default_prompt")


def parse_scalar(raw: str, source: Path, number: int) -> str | bool:
    value = raw.strip()
    if not value:
        raise ValueError(f"{source}:{number}: scalar value is required")
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"{source}:{number}: invalid quoted string") from error
        if not isinstance(parsed, str):
            raise ValueError(f"{source}:{number}: expected a string")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise ValueError(f"{source}:{number}: invalid quoted string")
        return value[1:-1].replace("''", "'")
    if value in ("true", "false"):
        return value == "true"
    if value[0] in "'\"" or value[-1] in "'\"":
        raise ValueError(f"{source}:{number}: invalid quoted string")
    if (
        value[0] in "[]{}&*!|>@`%"
        or value in ("null", "Null", "NULL", "~")
        or re.fullmatch(r"[-+]?(?:\d[\d_]*)(?:\.\d[\d_]*)?", value)
        or " #" in value
        or ": " in value
    ):
        raise ValueError(
            f"{source}:{number}: unsupported plain scalar; quote string values"
        )
    return value


def parse_flat_yaml(text: str, source: Path) -> dict[str, str | bool]:
    """Parse the flat scalar front matter used by Codex SKILL.md files."""
    values: dict[str, str | bool] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line != line.lstrip():
            raise ValueError(f"{source}:{number}: front-matter keys must not be indented")
        match = KEY_VALUE.match(line)
        if not match:
            raise ValueError(f"{source}:{number}: unsupported front-matter syntax")
        key = match.group("key")
        if key in values:
            raise ValueError(f"{source}:{number}: duplicate key {key!r}")
        values[key] = parse_scalar(match.group("value"), source, number)
    return values


def parse_openai_yaml(path: Path) -> dict[str, dict[str, str | bool]]:
    result: dict[str, dict[str, str | bool]] = {}
    section: str | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" in line:
            raise ValueError(f"{path}:{number}: tabs are not valid indentation")
        indent = len(line) - len(line.lstrip(" "))
        match = KEY_VALUE.match(line.lstrip(" "))
        if not match:
            raise ValueError(f"{path}:{number}: unsupported YAML syntax")
        key, raw = match.group("key"), match.group("value")
        if indent == 0:
            if raw.strip():
                raise ValueError(f"{path}:{number}: top-level {key!r} must be a mapping")
            if key in result:
                raise ValueError(f"{path}:{number}: duplicate key {key!r}")
            result[key] = {}
            section = key
        elif indent == 2 and section:
            if key in result[section]:
                raise ValueError(f"{path}:{number}: duplicate key {section}.{key}")
            result[section][key] = parse_scalar(raw, path, number)
        else:
            raise ValueError(f"{path}:{number}: only two-space mapping entries are supported")
    return result


def validate_openai_yaml(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        metadata = parse_openai_yaml(path)
    except ValueError as error:
        return [str(error)]
    interface = metadata.get("interface")
    if interface is None:
        return [f"{path}: missing interface mapping"]
    for key in REQUIRED_INTERFACE_KEYS:
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{path}: missing non-empty interface.{key}")
    policy = metadata.get("policy")
    if policy is not None and not isinstance(policy.get("allow_implicit_invocation"), bool):
        errors.append(f"{path}: policy.allow_implicit_invocation must be a boolean")
    unexpected = sorted(set(metadata) - {"interface", "policy"})
    if unexpected:
        errors.append(f"{path}: unsupported top-level keys: {', '.join(unexpected)}")
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
    name = metadata.get("name")
    if not isinstance(name, str) or name != skill.name:
        errors.append(f"{skill_file}: name must match directory {skill.name!r}")
    elif len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append(
            f"{skill_file}: name must be lowercase kebab-case and at most 64 characters"
        )
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_file}: description is required")
    elif len(description) > 1024:
        errors.append(f"{skill_file}: description exceeds 1024 characters")
    if "disable-model-invocation" in metadata and not isinstance(
        metadata["disable-model-invocation"], bool
    ):
        errors.append(f"{skill_file}: disable-model-invocation must be a boolean")

    openai_yaml = skill / "agents" / "openai.yaml"
    if openai_yaml.is_file():
        errors.extend(validate_openai_yaml(openai_yaml))
    return errors


def compare_packaged_skill(source: Path, candidate: Path) -> list[str]:
    """Require an installed catalog skill to match its packaged source exactly."""
    candidate_metadata = candidate.lstat()
    if candidate.is_symlink() or getattr(candidate_metadata, "st_file_attributes", 0) & 0x400:
        return [f"{candidate}: installed content differs from packaged source"]

    def manifest(root: Path) -> dict[Path, tuple[str, bytes | str | None]]:
        entries: dict[Path, tuple[str, bytes | str | None]] = {}
        for path in root.rglob("*"):
            relative = path.relative_to(root)
            metadata = path.lstat()
            if path.is_symlink() or getattr(metadata, "st_file_attributes", 0) & 0x400:
                try:
                    target: str | None = os.readlink(path)
                except OSError:
                    target = None
                entries[relative] = ("alias", target)
            elif stat.S_ISDIR(metadata.st_mode):
                entries[relative] = ("directory", None)
            elif stat.S_ISREG(metadata.st_mode):
                entries[relative] = ("file", path.read_bytes())
            else:
                entries[relative] = ("other", None)
        return entries

    if manifest(source) == manifest(candidate):
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
