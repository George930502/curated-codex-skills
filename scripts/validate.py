"""Run the Codex skill validator against this repository's skills."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skills-dir",
        type=Path,
        help="directory containing the skills to validate (defaults to installed skills)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    source_skills = repo_root / "skills"
    codex_home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
    skills_dir = (args.skills_dir or codex_home / "skills").expanduser().resolve()
    validator = (
        codex_home
        / "skills"
        / ".system"
        / "skill-creator"
        / "scripts"
        / "quick_validate.py"
    )

    if not validator.is_file():
        print(f"Validator not found: {validator}", file=sys.stderr)
        return 2

    skill_names = sorted(path.name for path in source_skills.iterdir() if path.is_dir())
    failures = 0
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    for name in skill_names:
        skill = skills_dir / name
        if not skill.is_dir():
            print(f"Missing skill directory: {skill}", file=sys.stderr)
            failures += 1
            continue

        result = subprocess.run(
            [sys.executable, str(validator), str(skill)],
            check=False,
            env=env,
        )
        if result.returncode != 0:
            failures += 1

    print(f"VALIDATION_FAILED_COUNT={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
