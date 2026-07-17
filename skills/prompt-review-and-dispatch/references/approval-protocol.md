# Approval and dispatch protocol

Read [`../../grilling/NATIVE-INPUT.md`](../../grilling/NATIVE-INPUT.md) first.
It exclusively defines native question shape and lifetime.

## State

```text
state: intake | audit | grilling | alignment | polish | awaiting-approval | executing-inline | dispatch | blocked | complete
source_prompt: [original input]
target_surface: [GPT-5.6 surface]
execution_mode: current-conversation | background-task
destination_thread_id: [required only for background-task]
destination_host_id: [host ID when present for background-task]
destination_title: [current conversation or verified background-task title]
purpose_brief: [goal, target state, audience, context, inputs, output contract, constraints, evidence behavior, authorization, validation, success criteria]
audit: [latest audit-only result]
draft: [exact polished prompt]
draft_sha256: [SHA-256 of the exact UTF-8 draft bytes]
executed_draft_sha256: [SHA-256 of the exact UTF-8 bytes executed or sent]
pending_question: [native stage and exact question]
approval: pending | approved | rejected
rejection_reason: [verbatim answer]
verified_inline_execution_evidence: [draft_sha256 equals executed_draft_sha256; same-task continuation; approved prompt success-criteria evidence]
dispatch_evidence: [send result; draft_sha256 equals executed_draft_sha256]
```

A change to source, target, execution mode, destination, or purpose clears the
audit, draft, `draft_sha256`, `executed_draft_sha256`, approval, verified inline
execution evidence, and dispatch evidence.

Compute `draft_sha256` as SHA-256 of `draft.encode("utf-8")` without
normalization. Before execution or send, compute `executed_draft_sha256` from
the exact UTF-8 bytes about to be executed or sent. If either hash cannot be
computed from exact bytes or the hashes differ, set `state: blocked`; never
self-report equality.
Use `scripts/hash_prompt.py` from this skill directory with the exact bytes on
stdin; it reads `stdin.buffer` without normalization. If the helper or an
equivalent byte-hash capability is unavailable, set `state: blocked` rather
than self-reporting a hash.

Whenever the draft is replaced or invalidated for any reason, clear `draft`,
`draft_sha256`, `executed_draft_sha256`, approval, and all execution evidence
before creating or approving a new draft.

After every grilling answer, update the applicable `purpose_brief` field before
re-auditing. Polishing receives this complete record, not a prose summary.

## Destination identity

For `current-conversation`, use the current task as the destination, label it
`current conversation`, and do not call `list_threads`, `read_thread`, or
`wait_threads`. No destination ID is required because no second task is being
selected.

For `background-task`, use `list_threads` to find the active Codex task and
`read_thread` when needed to match the current request. Store its thread ID,
host ID, and title. If more than one candidate remains, resolve the choice with
native input. A title alone is not identity. If `list_threads`, or `read_thread`
when needed, is unavailable, set `state: blocked` and retain the draft. Do not
guess an identity or substitute a manually supplied title or ID.

## Approval

After displaying the full draft and selected execution mode, run the approval
gate defined in the native-input contract. Approval authorizes only the
displayed bytes and selected mode; background mode also includes its verified
destination. `awaiting-approval` remains a tool-backed native stage until an
option is selected; it has no attempt counter and cannot return control to a
prose-input prompt. Only `Approve (Recommended)` authorizes current-conversation
execution or background dispatch. On `Reject`, run the native rejection gate
and store its selected category or `Other` text verbatim in `rejection_reason`.
Approval-gate `Other` is already the verbatim reason and does not authorize
execution or dispatch. Then clear the rejected draft, `draft_sha256`,
`executed_draft_sha256`, and all execution evidence; reset approval to pending
before returning that reason to grilling.

## Current-conversation execution

After approval with `execution_mode: current-conversation`, set
`state: executing-inline` and treat `draft` as the next instruction for this
same running Codex task. Execute it as a direct continuation and report
progress in the current conversation. This is not a second synthetic user
message; do not call `list_threads`, `read_thread`, `wait_threads`,
`send_message_to_thread`, `create_thread`, `fork_thread`, or `handoff_thread`;
those are background or thread-management operations. Do not fabricate a send
result. Current-conversation execution is not dispatch and does not replace or
weaken the verified background-dispatch gate. Record the
verified same-task continuation in `verified_inline_execution_evidence`, then set
`state: complete` only when `executed_draft_sha256` equals `draft_sha256` and
the approved prompt's success criteria have actual result, artifact, or test
evidence. Do not set `state: complete` merely when continuation begins; if the
approved work is incomplete, retain `state: executing-inline` or set
`state: blocked`.

## Background dispatch

Use this section only after the user explicitly requested and approved
`execution_mode: background-task`. Call `send_message_to_thread` once with:

```text
threadId: destination_thread_id
hostId: destination_host_id (when present)
prompt: draft (unchanged)
```

Record the returned success as `dispatch_evidence`; verify that
`executed_draft_sha256` equals `draft_sha256`. Both execution modes require this
exact-byte comparison; background dispatch cannot complete without both the
verified send evidence and the comparison.
If the tool is unavailable,
identity is ambiguous, or the send fails, set `state: blocked`; retain the
approved draft and retry the same dispatch when the capability returns. Manual
paste and a normal assistant reply are not background dispatch and cannot
complete the background workflow.
