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
    "docs/testing-strategy.md",
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
    workflow_root = ROOT / ".github" / "workflows"
    for path in sorted((*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml"))):
        text = path.read_text(encoding="utf-8")
        if not re.search(r"(?m)^permissions:\s*$", text):
            errors.append(f"{path.relative_to(ROOT)}: missing explicit permissions")
        for match in USES.finditer(text):
            if not re.fullmatch(r"[0-9a-f]{40}", match.group("ref")):
                errors.append(
                    f"{path.relative_to(ROOT)}: action is not pinned to a full commit SHA"
                )
        if "actions/checkout@" in text and "persist-credentials: false" not in text:
            errors.append(f"{path.relative_to(ROOT)}: checkout must disable credential persistence")
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
    for guard in (
        "Refusing to install skills into the filesystem root",
        "Refusing to install into the packaged source catalog",
        "Refusing to install through an unresolved parent segment",
    ):
        if guard not in shell or guard not in powershell:
            errors.append(f"installers must both enforce safety guard: {guard}")
    return errors


def check_native_input_contract() -> list[str]:
    contract_path = ROOT / "skills" / "grilling" / "NATIVE-INPUT.md"
    if not contract_path.is_file():
        return [f"missing required file: {contract_path.relative_to(ROOT)}"]
    contract = contract_path.read_text(encoding="utf-8")
    required = (
        "request_user_input",
        "autoResolutionMs",
        "- Grilling:",
        "- Alignment:",
        "- Approval:",
        "- Rejection:",
        "Repeat without a retry limit",
        "do not finish the turn in",
        "Only the host stopping the task",
    )
    errors = [
        f"{contract_path.relative_to(ROOT)}: missing required native-input rule {rule!r}"
        for rule in required
        if rule not in contract
    ]
    consumers = (
        "skills/domain-modeling/SKILL.md",
        "skills/grilling/SKILL.md",
        "skills/prompt-master-gpt5/SKILL.md",
        "skills/prompt-review-and-dispatch/SKILL.md",
        "skills/prompt-review-and-dispatch/references/approval-protocol.md",
    )
    for relative in consumers:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
        elif "NATIVE-INPUT.md" not in path.read_text(encoding="utf-8"):
            errors.append(f"{relative}: must reference the native-input contract")
    approval_path = ROOT / consumers[-1]
    if approval_path.is_file():
        approval = approval_path.read_text(encoding="utf-8")
        for rule in ("list_threads", "read_thread", "state: blocked", "Do not guess an identity"):
            if rule not in approval:
                errors.append(f"{consumers[-1]}: missing destination-identity rule {rule!r}")
    return errors


def main() -> int:
    version_file = ROOT / "VERSION"
    errors = [
        f"missing required file: {relative}"
        for relative in REQUIRED_FILES
        if not (ROOT / relative).is_file()
    ]
    errors.extend(check_links())
    errors.extend(check_identity())
    errors.extend(check_workflows())
    errors.extend(check_install_destinations())
    errors.extend(check_native_input_contract())
    version = version_file.read_text(encoding="utf-8").strip() if version_file.is_file() else ""
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("VERSION must contain one SemVer core version")
    elif not (ROOT / "docs" / "specs" / f"production-v{version}.md").is_file():
        errors.append(f"missing release spec for VERSION {version}")
    for error in errors:
        print(error, file=sys.stderr)
    print(f"REPOSITORY_CHECK_FAILED_COUNT={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
