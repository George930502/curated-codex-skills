# Approval and dispatch protocol

Read [`../../grilling/NATIVE-INPUT.md`](../../grilling/NATIVE-INPUT.md) first.
It exclusively defines native question shape and lifetime.

## State

```text
state: intake | audit | grilling | alignment | polish | awaiting-approval | dispatch | blocked | complete
source_prompt: [original input]
target_surface: [GPT-5.6 surface]
destination_thread_id: [verified Codex task ID]
destination_host_id: [host ID when present]
destination_title: [verified title]
purpose_brief: [goal, target state, audience, context, inputs, output contract, constraints, evidence behavior, authorization, validation, success criteria]
audit: [latest audit-only result]
draft: [exact polished prompt]
pending_question: [native stage and exact question]
approval: pending | approved | rejected
rejection_reason: [verbatim answer]
dispatch_evidence: [send result]
```

A change to source, target, destination, or purpose clears the audit, draft,
approval, and dispatch evidence.

After every grilling answer, update the applicable `purpose_brief` field before
re-auditing. Polishing receives this complete record, not a prose summary.

## Destination identity

Use `list_threads` to find the active Codex task and `read_thread` when needed
to match the current request. Store its thread ID, host ID, and title. If more
than one candidate remains, resolve the choice with native input. A title alone
is not identity.

## Approval

After displaying the full draft and destination, run the approval gate defined
in the native-input contract. Approval authorizes only the displayed bytes and
destination. On `不同意`, run the native rejection gate and store its selected
category or `Other` text verbatim in `rejection_reason`. Approval-gate `Other`
is already the verbatim reason. Then clear the rejected draft and return that
reason to grilling.

## Dispatch

After approval, call `send_message_to_thread` once with:

```text
threadId: destination_thread_id
hostId: destination_host_id (when present)
prompt: draft (unchanged)
```

Record the returned success as `dispatch_evidence`. Completion requires that
evidence. If the tool is unavailable, identity is ambiguous, or the send fails,
set `state: blocked`; retain the approved draft and retry the same dispatch when
the capability returns. Manual paste and a normal assistant reply are not
dispatch and cannot complete the workflow.
