# Source lock and adaptation audit

Reviewed 2026-07-14. GitHub repository contents, not mirrors or derivative
articles, are the source of truth.

## Matt Pocock skills

- Repository: https://github.com/mattpocock/skills
- Commit: `66898f60e8c744e269f8ce06c2b2b99ce7660d5f`
- License: upstream `LICENSE`, SHA-256 `0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5`; MIT notice preserved in `THIRD_PARTY_NOTICES.md`.
- Exact unified diff: [`provenance/matt-adaptations.patch`](provenance/matt-adaptations.patch).

| Local file | Upstream file | Upstream SHA-256 | Local SHA-256 | Adaptation |
|---|---|---|---|---|
| `skills/grill-with-docs/SKILL.md` | `skills/engineering/grill-with-docs/SKILL.md` | `610d091047bcfb9db0f75c057d15538481a721111579fc5ec7f83ad9131a2165` | `454528d25fcc31d3e912e0bab24d22bb9f0c4439c73e63992b97a6a3427439f2` | Core description/body preserved; Codex invocation syntax and completion gate added. |
| `skills/grilling/SKILL.md` | `skills/productivity/grilling/SKILL.md` | `44331dda57f461db4fec3f2efb6ddabe7aaaa0a57ae0f88a883bc61aed8a0587` | `8ba1c3cfc3d75a7f385daa2903abbf173c53b807a6129b16a8beebd73bf6c5fc` | Native decision-tree and fact ownership preserved; question cadence moved to the sole native-input contract. |
| `skills/domain-modeling/SKILL.md` | `skills/engineering/domain-modeling/SKILL.md` | `152e2c97239affb12a60c5f4a7e74ab546a49ae169688c81f4e2ccc42dafa579` | `4d91ae37bde9cb589be6f81f4fc2bc91002f64ab354994321b83caa607e23bad` | Native behavior preserved; duplicated file-layout and ADR gate text replaced by conditional pointers; every standalone decision uses the shared native-input contract. |
| `skills/domain-modeling/ADR-FORMAT.md` | same relative upstream path | `f1f36cd3f8d3b6474ddd5855da4e233bfc4ae1a1c5024909ccf11871819a41b2` | same | Unchanged. |
| `skills/domain-modeling/CONTEXT-FORMAT.md` | same relative upstream path | `b8cc318f2a4285b530e908b6bc43901c3c5cd11100362636bbc4216639bef597` | `ccd51ef654a9db6b9599eb5c4ec2936537783871c724c0799606177baf09b588` | Ambiguous context routing points to the shared native-input contract. |

## Prompt Master

- Repository: https://github.com/nidhinjs/prompt-master
- Commit: `d15eabbe5d2122eedc060bae8a771381e9873d1b`
- License: upstream `LICENSE`, SHA-256 `29e8ba0b54274eaa92b7cb074fe1765ba7b83993e0d2605e5308c6972a47daa7`; MIT notice preserved in `THIRD_PARTY_NOTICES.md`.
- Exact unified diff: [`provenance/nidhin-adaptations.patch`](provenance/nidhin-adaptations.patch).

| Upstream file | SHA-256 | Distilled locally |
|---|---|---|
| `SKILL.md` | `b85718374d27bbada453791af92b7ae0b3256e5552d2f3f9d940ca4183131e4b` | intent extraction, bounded clarification, silent routing, output lock, token audit |
| `references/patterns.md` | `2d2eb623396ce5edade402cfcafbd457af093cf85fa5966c34c210e58ce1f9d1` | coding-agent scope, state, success, evidence, and approval patterns |
| `references/templates.md` | `0850a3871058077bfc6a16372fa3beb28d81f02baab8d42d3607ddc3a681ae67` | minimal one-shot and agentic prompt shapes |

Local distilled outputs are `skills/prompt-master-gpt5/SKILL.md` at SHA-256
`76e923d381e2927ccf9be9442d8e8cf8f5e8e7ae66ea9f6d1c4a3cc7b43f59d8`
and `references/gpt56-routing.md` at SHA-256
`cda7e237fa80d63226c06bd12252cb7a5a18dc1e7caf143c858b75d333eca3dc`.

OpenAI guidance overrides upstream model-specific advice. In particular, the
local skill omits visible chain-of-thought requests and generic role padding.

## Skill-writing audit

[`AUTHORING-AUDIT.md`](AUTHORING-AUDIT.md) records the explicit
`$writing-great-skills` and `$ponytail` invocations during the 2026-07-14
authoring and repair sessions. They are authoring standards, not
runtime prompt-refinement dependencies: `writing-great-skills` is user-only
(`disable-model-invocation: true`) and therefore cannot be invoked by another
skill. Applied checks:

- every step has a checkable completion criterion;
- shared policy has one source of truth;
- branch-specific detail is behind a context pointer;
- duplicated rules, no-ops, speculative dependencies, and prose fallbacks are removed;
- native host capabilities and the standard library precede custom code.
