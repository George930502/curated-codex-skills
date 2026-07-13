# Prompt Review and Dispatch

Codex skills that audit and polish GPT-5.6 prompts, clarify purpose through
native choices, require explicit approval, then queue the approved prompt into
the verified Codex task.

## Skills

- `prompt-master-gpt5` — audit or polish a GPT-5.6 prompt.
- `prompt-review-and-dispatch` — clarify, polish, approve, and dispatch.
- `grill-with-docs` — Matt Pocock's grilling/domain-modeling composition.
- `grilling` — one-decision-at-a-time interviewing with native Codex input.
- `domain-modeling` — maintain project language and durable decisions.

The authoritative native-input contract is
`skills/grilling/NATIVE-INPUT.md`. GPT-5.6 facts live only in
`skills/prompt-master-gpt5/references/openai-gpt56-prompting.md`.

Per the product contract, every incomplete prompt review invokes
`grill-with-docs`, not bare `grilling`. Its domain-modeling branch writes only
when an actual term is resolved or a candidate decision passes the ADR gate.

## Evidence

[`SOURCES.md`](SOURCES.md) pins every upstream commit, source path, hash, and
local adaptation. [`AUTHORING-AUDIT.md`](AUTHORING-AUDIT.md) records the invoked
skill standards and resulting checks. The repository is MIT licensed;
third-party notices are in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Install

```bash
git clone https://github.com/George930502/prompt-review-and-dispatch.git
rsync -a prompt-review-and-dispatch/skills/ "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart Codex, then invoke `$prompt-review-and-dispatch`.

## Validate

```bash
for skill in skills/*; do
  python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" "$skill"
done
```
