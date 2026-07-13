"""Check repository invariants and local Markdown links."""

from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\((?P<target>[^)]+)\)")
OLD_REPOSITORY = "George930502/" + "prompt-review-and-dispatch"
REQUIRED_FILES = (
    "AGENTS.md",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "LICENSE",
    "README.md",
    "ROADMAP.md",
    "SECURITY.md",
    "SOURCES.md",
    "SUPPORT.md",
    "THIRD_PARTY_NOTICES.md",
    "VERSION",
    "docs/agents/issue-tracker.md",
    "docs/compatibility.md",
    "docs/releasing.md",
)
USES = re.compile(r"(?m)^\s*uses:\s*[^@\s]+@(?P<ref>[^\s#]+)")


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts and not path.is_symlink()
    )


def check_links() -> list[str]:
    errors: list[str] = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?ms)^```.*?^```\s*$", "", text)
        for match in LINK.finditer(text):
            target = match.group("target").strip().split(maxsplit=1)[0]
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            local = unquote(target.split("#", 1)[0])
            if local and not (path.parent / local).resolve().exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link {target!r}")
    return errors


def check_identity() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix == ".patch":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if OLD_REPOSITORY in text:
            errors.append(f"{path.relative_to(ROOT)}: contains old repository identity")
    return errors


def check_workflows() -> list[str]:
    errors: list[str] = []
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if not re.search(r"(?m)^permissions:\s*$", text):
            errors.append(f"{path.relative_to(ROOT)}: missing explicit permissions")
        for match in USES.finditer(text):
            if not re.fullmatch(r"[0-9a-f]{40}", match.group("ref")):
                errors.append(
                    f"{path.relative_to(ROOT)}: action is not pinned to a full commit SHA"
                )
    return errors


def check_install_destinations() -> list[str]:
    shell = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")
    powershell = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
    errors: list[str] = []
    if "SKILLS_INSTALL_DIR" not in shell or ".agents/skills" not in shell:
        errors.append("scripts/install.sh: user destination or test override is missing")
    if "[string]$Destination" not in powershell or "'.agents'" not in powershell:
        errors.append("scripts/install.ps1: user destination or test override is missing")
    if ".codex/skills" in shell or ".codex\\skills" in powershell:
        errors.append("installers must use the documented .agents/skills destination")
    return errors


def main() -> int:
    errors = [
        f"missing required file: {relative}"
        for relative in REQUIRED_FILES
        if not (ROOT / relative).is_file()
    ]
    errors.extend(check_links())
    errors.extend(check_identity())
    errors.extend(check_workflows())
    errors.extend(check_install_destinations())
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").is_file() else ""
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("VERSION must contain one SemVer core version")
    for error in errors:
        print(error, file=sys.stderr)
    print(f"REPOSITORY_CHECK_FAILED_COUNT={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
