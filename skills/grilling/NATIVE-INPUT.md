# Native input contract

This is the single source of truth for every clickable grilling, alignment,
rejection, and approval question in this repository.

## Request shape

Call `request_user_input` with exactly one question and omit
`autoResolutionMs`. The question must have:

- a header of at most 12 characters;
- a stable snake-case `id`;
- one sentence asking for one decision;
- two or three mutually exclusive options;
- the recommended option first, with `(Recommended)` appended to its label;
- one sentence per option explaining the trade-off.

The Codex client adds the free-form `Other` choice. Preserve an `Other` answer
verbatim. Do not add a custom field or simulate controls with Markdown.

## Lifecycle

Every question is blocking. With `autoResolutionMs` omitted, inactivity has no
agent-authored expiry. Keep the exact pending question and workflow state until
a valid answer arrives. If `request_user_input` returns without a selected
option while the task is still active, immediately call it again with the same
question and options. Repeat without a retry limit; do not finish the turn in
an awaiting state that requires a prose reply. Only the host stopping the task
or session may clear the control. When that task resumes, reissue the same
native stage before any other user-facing response. Silence, cleanup, and an
empty answer change no state.

If `request_user_input` is unavailable, set the workflow to `blocked` and name
the missing capability. A prose question is not a substitute.

## Required gates

- Grilling: ask the highest-impact unresolved decision, then recompute.
- Alignment: offer `目的已對齊 (Recommended)` and `仍需釐清`; `Other` is custom feedback.
- Approval: offer `同意 (Recommended)` and `不同意`; only the first authorizes dispatch.
- Rejection: offer two or three reason categories; `Other` carries the user's exact reason.

Completion requires an explicit native selection; inference from prose or
inactivity is invalid.
