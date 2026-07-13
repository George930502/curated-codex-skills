# GPT-5.6 prompting guidance: source inventory and synthesis

Reviewed 2026-07-14 through the OpenAI Developer Docs MCP.

## Coverage boundary

“All GPT-5.6 prompting guidance” means every canonical OpenAI API guide or model
page found by the four searches `GPT-5.6 prompting`, `GPT-5.6 models`, `GPT-5.6
Codex prompting`, and `GPT-5.6 ChatGPT prompting` that either:

1. explicitly names GPT-5.6 while prescribing prompt behavior; or
2. is the prompting or migration guide linked by the canonical GPT-5.6 model guide.

All 66 results of the broadest models search were paged before filtering.
Cookbook examples, tracks, use cases, showcases, API reference schemas, generic
feature manuals, product pages that merely mention GPT-5.6, and the release
blog are outside this API-guide boundary. Feature manuals remain supporting
sources when a selected feature is used. The ChatGPT search returned no
GPT-5.6-specific prompting guide; the Codex search pointed back to the model
and prompt-engineering guides below.

## Reading order and evidence

| Order | Official page | Why included |
|---:|---|---|
| 1 | [Using GPT-5.6](https://developers.openai.com/api/docs/guides/latest-model.md) | Canonical family guide; its frontmatter names the next two guides. |
| 2 | [Prompting guidance for GPT-5.6 Sol](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6.md) | Canonical prompt guide for Sol and the GPT-5.6 family. |
| 3 | [Upgrading to GPT-5.6 Sol](https://developers.openai.com/api/docs/guides/upgrading-to-gpt-5p6-sol.md) | Canonical migration guide for prompts, tools, agents, and integrations. |
| 4 | [Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering) | Explicit GPT-5.6 and coding prompting section; links the current guide. |
| 5 | [Prompting overview](https://developers.openai.com/api/docs/guides/prompting) | Official prompt construction and reusable-prompt overview. |
| 6 | [Model optimization](https://developers.openai.com/api/docs/guides/model-optimization) | Requires eval-driven prompt iteration; explicitly recommends GPT-5.6. |
| 7 | [Code generation](https://developers.openai.com/api/docs/guides/code-generation) | Explicit GPT-5.6 coding-agent selection and guidance pointer. |
| 8 | [Text generation](https://developers.openai.com/api/docs/guides/text) | Explains that GPT-5.6 is a reasoning model and points to the applicable prompt route. |
| 9 | [Models index](https://developers.openai.com/api/docs/models) and [Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), [Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra), [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) | Family membership and routing facts; the index was discoverable but its `.md` fetch returned 404, so model pages supply the fetched evidence. |

Supporting implementation pages read only when their feature is used:
[reasoning](https://developers.openai.com/api/docs/guides/reasoning),
[reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices),
[tools](https://developers.openai.com/api/docs/guides/tools),
[prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching), and
[multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent).

## Claim-to-source synthesis

| Prompt rule | Evidence |
|---|---|
| Define outcome, important constraints, evidence, and completion bar; leave ordinary path selection to the model. | GPT-5.6 prompt guide: introduction, “Outcome-first prompts and stopping conditions”. |
| Remove repeated rules, examples, irrelevant tools, and generic process scaffolding one group at a time; rerun the same evals. | GPT-5.6 guide: “Favor leaner prompts”; prompt guide: “Simplify prompts first”; model optimization. |
| State true invariants once; use decision rules for judgment and resolve contradictions. | Prompt guide: “Simplify prompts first”, “Outcome-first prompts”. |
| Put durable application behavior in `instructions`/developer content and request data in user/input content; resend instructions when the state mechanism does not carry them. | Prompting overview, prompt engineering, and text generation: message roles and instruction following. |
| Use Markdown for hierarchy and XML for data/example boundaries; use a small diverse few-shot set only when examples improve the measured behavior. | Prompt engineering: message formatting and few-shot learning. |
| Define safe local autonomy and approval before external, destructive, costly, or scope-expanding actions. | GPT-5.6 guide and prompt guide: “Define autonomy and approval boundaries”. |
| Specify required content and structure; use `text.verbosity` as API setup rather than pretending prompt text enables it. | Both GPT-5.6 guides: response length/style. |
| Describe personality as writing choices and collaboration as ask/assume/check behavior. | Prompt guide: “Personality, collaboration, and response length”. |
| Expose relevant tools only; define prerequisite retrieval, parallel independent reads, fallbacks, schemas, retries, stop conditions, and direct handoff. | Prompt guide: “Tool routing” and “Programmatic Tool Calling”. |
| Use programmatic tool calling only for bounded deterministic reduction; keep approval, semantic judgment, citations, and final validation direct. | GPT-5.6 guide and prompt guide: “Programmatic Tool Calling”. |
| For grounded work, define support requirements, retrieval budget, citation placement, inference labels, source conflicts, and missing-evidence behavior. | Prompt guide: “Grounding, citations, and retrieval budgets”. |
| For long work, request a short preamble and sparse outcome updates; preserve phase/state and compact at milestones. | Prompt guide: “Long-running workflows and state”. |
| Validate changed behavior with targeted tests/checks; report the next-best check when validation cannot run. | Prompt guide: “Check work before finishing”. |
| Treat production prompts as code: typed dynamic inputs, version control, review, fixtures/evals, staged release, and rollback. | Prompting overview, prompt engineering, and text generation: version prompts in code. |
| Keep model, reasoning, caching, PTC, and orchestration controls in API/application setup. | GPT-5.6 model and migration guides. |
| Select Sol for frontier capability, Terra for balance, and Luna for efficient high volume; `gpt-5.6` routes to Sol. | GPT-5.6 model guide and three model pages. |
| Migrate by changing the model first, preserving reasoning effort, evaluating, then making surgical prompt changes. | Prompt guide: “Prompt migration workflow”; migration guide. |
| Do not request visible chain-of-thought; ask for observable checks and final answers. | Reasoning best practices plus the GPT-5.6 outcome/check-work guidance. |

## Coding-agent contract

A GPT-5.6 coding-agent prompt is complete when it names:

- one user-visible target state and relevant starting state;
- exact file/resource and permission scope;
- constraints and behavior to preserve;
- evidence and missing-evidence behavior;
- validation and an exhaustive definition of done;
- safe autonomous actions and approval/stop conditions;
- the final artifact and concise completion evidence.

Add tool routing, retries, progress updates, examples, personality, or API setup
only when they change behavior. Re-run representative tasks after each prompt
change; a shorter prompt is better only when it still passes.
