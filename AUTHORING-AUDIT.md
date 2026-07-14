# Authoring audit

This checked-in record identifies the skill invocations that shaped the
artifact and the observable results.

- Date: 2026-07-14
- `$writing-great-skills`: `SKILL.md` SHA-256 `4d6ccbc3760b1bd4107c495a79872286ea69494003f3b0a719fc95b147457061`; its `GLOSSARY.md` SHA-256 is `cccd684c73fb7a06f523497b0121765f92d2b33d6ef9c51602294849233451d6`.
- `$ponytail`: `SKILL.md` SHA-256 `1316a2f3f95741d2300b116fe0c2d81ce4a9568656ed0a62643f54aaf09957f2`.

The authoring and repair runs explicitly invoked both skills before edits. The
transcript was inspected locally; machine-specific paths and task identifiers
are intentionally excluded from this public artifact. Resulting checks:

| Invoked rule | Observable result |
|---|---|
| Native before custom code | Deleted `approval_input_server.py`; use host-native input and thread send tools. |
| Single source of truth | Native question rules live only in `skills/grilling/NATIVE-INPUT.md`; GPT-5.6 facts live only in the official synthesis. |
| Progressive disclosure | SKILL files retain steps; schemas, sources, prompt shapes, and protocol details are referenced. |
| Checkable completion | Every composed workflow has an explicit completion criterion. |
| Pruning/YAGNI | Removed text fallbacks, private MCP transport, repeated GPT rules, and duplicated domain format policy. |

Validation evidence from the same task: all five source and installed skills
passed the repository validator, and source/install parity passed. Upstream
commits, source hashes, local hashes, and adaptation records were reviewed;
the multi-source Prompt Master distillation is intentionally not represented
as one mechanically applicable patch. The final `$code-review` runs use fresh
isolated Standards and Spec subagents.
