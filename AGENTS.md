# Repository guidance

Curated Codex Skills is a distribution repository. Preserve each skill's
runtime identity, approval gates, provenance, and upstream notices.

## Required checks

Run before proposing a change:

```bash
python3 scripts/validate.py --skills-dir skills
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
```

Use `py -3` instead of `python3` on Windows. Installer tests must pass an
isolated destination and must never write to a real user home.

## Change rules

- Keep repository-wide identity separate from individual skill names.
- Keep `SOURCES.md`, `THIRD_PARTY_NOTICES.md`, and provenance patches auditable.
- Do not weaken native-input, explicit-approval, or verified-dispatch gates.
- Add automation only when it enforces a documented contract.
- Update `CHANGELOG.md` for user-visible behavior.

## Agent skills

### Issue tracker

Work is tracked in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the canonical Matt Pocock triage roles. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository. See `docs/agents/domain.md`.

## Review guidelines

Review from the requested fixed baseline. Standards review checks documented
repository rules; Spec review checks the stated task only. Treat unsupported
compatibility claims, installer writes outside an isolated destination, broken
provenance, and weakened approval/dispatch behavior as release blockers.
