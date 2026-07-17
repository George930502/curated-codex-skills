"""Check repository invariants and local Markdown links."""

from __future__ import annotations

import hashlib
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
NATIVE_RETRY_LIFECYCLE = (
    "If `request_user_input` returns without a selected option while the task is still "
    "active, immediately call it again with the same question and options. Repeat "
    "without a retry limit; do not finish the turn in an awaiting state that requires "
    "a prose reply."
)
NATIVE_INPUT_RULES = (
    "request_user_input",
    "autoResolutionMs",
    "- Grilling:",
    "- Alignment:",
    "- Approval:",
    "- Rejection:",
    "Aligned (Recommended)",
    "Needs revision",
    "Approve (Recommended)",
    "Reject",
    "in English, regardless of the conversation language",
    "Normal assistant prose remains language-adaptive",
    "host-controlled",
    "Only the host stopping the task",
)
FORMER_NATIVE_LABELS = (
    "\u76ee\u7684\u5df2\u5c0d\u9f4a",
    "\u4ecd\u9700\u91d0\u6e05",
    "\u540c\u610f (Recommended)",
    "\u4e0d\u540c\u610f",
    "`\u540c\u610f`",
)
APPROVAL_RULES = (
    "Only `Approve (Recommended)` authorizes current-conversation execution or background dispatch",
    "On `Reject`, run the native rejection gate",
    "Approval-gate `Other` is already the verbatim reason and does not authorize "
    "execution or dispatch",
    "prompt: draft (unchanged)",
)
NO_THREAD_LOOKUP_RULE = "do not call `list_threads`, `read_thread`, or `wait_threads`"
SAME_TASK_RULE = "same running Codex task"
NO_INLINE_THREAD_RULE = (
    "do not call `list_threads`, `read_thread`, `wait_threads`, "
    "`send_message_to_thread`, `create_thread`, `fork_thread`, or `handoff_thread`"
)
INLINE_RULES = (
    "For `current-conversation`, use the current task as the destination",
    NO_THREAD_LOOKUP_RULE,
    SAME_TASK_RULE,
    "This is not a second synthetic user message",
    NO_INLINE_THREAD_RULE,
    "verified same-task continuation",
    "does not replace or weaken the verified background-dispatch gate",
    "approved prompt's success criteria have actual result, artifact, or test evidence",
    "Do not set `state: complete` merely when continuation begins",
    "`executed_draft_sha256` equals `draft_sha256`",
    "Compute `draft_sha256` as SHA-256 of `draft.encode(\"utf-8\")` without normalization",
    "compute `executed_draft_sha256` from the exact UTF-8 bytes about to be executed or sent",
    "If either hash cannot be computed from exact bytes or the hashes differ, set `state: blocked`",
    "never self-report equality",
    "Use the installed `scripts/hash_prompt.py` from this skill directory with the exact bytes on stdin",
    "it reads `stdin.buffer` without normalization",
    "clears the audit, draft, `draft_sha256`, `executed_draft_sha256`, approval",
    "After any such invalidation, reset approval to `pending` before creating or approving a new draft",
    "If the installed helper is unavailable, set `state: blocked` rather than using an equivalent capability or self-reporting a hash",
    "Whenever the draft is replaced or invalidated for any reason, clear `draft`, `draft_sha256`, `executed_draft_sha256`, approval, and all execution evidence before creating or approving a new draft",
    "reset approval to pending before returning that reason to grilling",
)
BACKGROUND_RULES = (
    "Use this section only after the user explicitly requested and approved",
    "`execution_mode: background-task`",
    "Call `send_message_to_thread` once",
    "background dispatch cannot complete without both the verified send evidence and the comparison",
)
SKILL_INLINE_RULES = (
    "Default to `current-conversation` execution",
    "Use `background-task` only when the user explicitly asks for another Codex task or",
    NO_THREAD_LOOKUP_RULE,
    NO_INLINE_THREAD_RULE,
    SAME_TASK_RULE,
    "does not weaken the verified-dispatch gate",
    "verified evidence of the same-task continuation",
    "Inline completion requires verified evidence of the same-task continuation and the approved prompt's success criteria",
)
PROMPT_REVIEW_CONTRADICTIONS = (
    "For current-conversation, call `send_message_to_thread`",
    "For `current-conversation`, call `send_message_to_thread`",
    "current-conversation mode may call `send_message_to_thread`",
    "current-conversation mode may call `wait_threads`",
    "current-conversation execution may complete without verified",
    "Set `state: complete` merely when continuation begins",
)
CRITICAL_CONTRACT_HASHES = {
    "native-input": "791c0ca5d91bfced24adc536a8f9cc6c2f7288363bfcca61a807a31e6a6978dc",
    "approval": "9afab963c673cab472442c9dc10370cdd7a02563ff8003036316064e1c113b8b",
}


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


def has_canonical_native_retry_lifecycle(contract: str) -> bool:
    return NATIVE_RETRY_LIFECYCLE in " ".join(contract.split())


def native_input_text_errors(contract: str) -> list[str]:
    normalized = " ".join(contract.split())
    errors = [
        f"missing required native-input rule {rule!r}"
        for rule in NATIVE_INPUT_RULES
        if rule not in normalized
    ]
    errors.extend(
        f"contains former non-English native-control label {label!r}"
        for label in FORMER_NATIVE_LABELS
        if label in contract
    )
    errors.extend(critical_contract_errors("native-input", contract))
    return errors


def critical_contract_errors(name: str, text: str) -> list[str]:
    actual = hashlib.sha256(text.encode()).hexdigest()
    expected = CRITICAL_CONTRACT_HASHES[name]
    if actual == expected:
        return []
    return [f"{name} content differs from its reviewed contract pin"]


def approval_protocol_errors(protocol: str) -> list[str]:
    normalized = " ".join(protocol.split())
    errors = [
        f"missing required approval rule {rule!r}"
        for rule in APPROVAL_RULES
        if rule not in normalized
    ]
    errors.extend(critical_contract_errors("approval", protocol))
    return errors


def prompt_review_contract_errors(skill: str, protocol: str) -> list[str]:
    normalized_skill = " ".join(skill.split())
    normalized_protocol = " ".join(protocol.split())
    normalized_contract = f"{normalized_skill} {normalized_protocol}"
    errors = [
        f"missing required current-conversation rule {rule!r}"
        for rule in SKILL_INLINE_RULES
        if rule not in normalized_skill
    ]
    errors.extend(
        f"missing required inline-execution rule {rule!r}"
        for rule in INLINE_RULES
        if rule not in normalized_protocol
    )
    errors.extend(
        f"missing required background-dispatch rule {rule!r}"
        for rule in BACKGROUND_RULES
        if rule not in normalized_protocol
    )
    errors.extend(
        f"contains contradictory current-conversation rule {rule!r}"
        for rule in PROMPT_REVIEW_CONTRADICTIONS
        if rule in normalized_skill or rule in normalized_protocol
    )
    background_tools = (
        "list_threads",
        "read_thread",
        "wait_threads",
        "send_message_to_thread",
        "create_thread",
        "fork_thread",
        "handoff_thread",
    )
    for sentence in re.split(r"(?<=[.!?])\s+", normalized_contract):
        if (
            "current-conversation" in sentence
            and any(f"`{tool}`" in sentence for tool in background_tools)
            and not re.search(r"\b(?:do not|does not|never)\s+(?:call|use)\b", sentence)
        ):
            errors.append(
                "contains a current-conversation sentence that permits background thread operation"
            )
            break
    return errors


def check_native_input_contract() -> list[str]:
    contract_path = ROOT / "skills" / "grilling" / "NATIVE-INPUT.md"
    if not contract_path.is_file():
        return [f"missing required file: {contract_path.relative_to(ROOT)}"]
    contract = contract_path.read_text(encoding="utf-8")
    errors = [
        f"{contract_path.relative_to(ROOT)}: {error}"
        for error in native_input_text_errors(contract)
    ]
    if not has_canonical_native_retry_lifecycle(contract):
        errors.append(
            f"{contract_path.relative_to(ROOT)}: native retry lifecycle must match the canonical contract"
        )
    consumers = (
        "skills/domain-modeling/SKILL.md",
        "skills/grill-with-docs/SKILL.md",
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
    for path in markdown_files():
        if path == contract_path:
            continue
        text = path.read_text(encoding="utf-8")
        for label in FORMER_NATIVE_LABELS:
            if label in text:
                errors.append(
                    f"{path.relative_to(ROOT)}: contains former non-English "
                    f"native-control label {label!r}"
                )
    approval_path = ROOT / consumers[-1]
    if approval_path.is_file():
        approval = approval_path.read_text(encoding="utf-8")
        errors.extend(
            f"{consumers[-1]}: {error}"
            for error in approval_protocol_errors(approval)
        )
        normalized_approval = " ".join(approval.split())
        for rule in ("list_threads", "read_thread", "state: blocked", "Do not guess an identity"):
            if rule not in normalized_approval:
                errors.append(f"{consumers[-1]}: missing destination-identity rule {rule!r}")
        skill_path = ROOT / "skills" / "prompt-review-and-dispatch" / "SKILL.md"
        skill = skill_path.read_text(encoding="utf-8") if skill_path.is_file() else ""
        errors.extend(
            f"prompt-review-and-dispatch: {error}"
            for error in prompt_review_contract_errors(skill, approval)
        )
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
