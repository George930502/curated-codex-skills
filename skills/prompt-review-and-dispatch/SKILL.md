---
name: prompt-review-and-dispatch
description: Audit a GPT-5.6 prompt, clarify purpose through native clickable questions, polish it, require explicit approval, then queue the exact approved prompt into a verified Codex task. Use when the user wants a review-before-send prompt workflow.
---

# Prompt Review and Dispatch

Orchestrate `$prompt-master-gpt5` and `$grill-with-docs`. Read
[`references/approval-protocol.md`](references/approval-protocol.md) before the
first user decision; it is the single source for state, approval, and dispatch.
Every user decision in every stage follows
[`../grilling/NATIVE-INPUT.md`](../grilling/NATIVE-INPUT.md).

## 1. Intake

Capture the rough prompt, GPT-5.6 target surface, and destination Codex task.
Resolve the destination with the host's thread-list/read capabilities and show
its title and ID before approval.

Completion criterion: one destination task is verified and every working-state
field required by the approval protocol exists.

## 2. Audit

Invoke `$prompt-master-gpt5` in `audit-only` mode. Consume its gate as
authoritative; this orchestrator does not redefine the audit dimensions.

Completion criterion: the audit returns exactly one gate:
`ready-for-polish` or `needs-purpose-clarification`.

## 3. Align

For an incomplete prompt, invoke `$grill-with-docs`. Resolve facts from files
and docs; ask only the highest-impact unresolved decision.

Re-run `audit-only` after each answer. Repeat until the audit is ready and the
user passes the native alignment gate. A complete user-supplied contract may
skip grilling, but still requires that gate.

Completion criterion: the audit is ready and alignment is explicitly selected.

## 4. Polish

Invoke `$prompt-master-gpt5` in `polish` mode with the aligned brief and audit.
Preserve settled decisions.

Completion criterion: one final copyable prompt passes the prompt-master audit.

## 5. Approve and dispatch

Show the exact prompt and verified destination, then execute the approval and
dispatch stages in the approval protocol. Rejection returns to alignment with
the selected reason as new evidence; a new draft requires a new approval.

Completion criterion: the approval protocol reaches `complete`.
