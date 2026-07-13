# Coding-agent prompt patterns

Distilled from `nidhinjs/prompt-master` commit
`d15eabbe5d2122eedc060bae8a771381e9873d1b`. OpenAI's current GPT-5.6 guidance
overrides upstream model advice; the repository `SOURCES.md` holds provenance.

## Audit dimensions

1. Precise task verb and one deliverable.
2. Target model/tool and receiving surface.
3. Starting state, relevant prior decisions, and supplied inputs.
4. Target state, output shape, audience, and length.
5. Scope, stack, files/resources, and must-preserve behavior.
6. Evidence boundary and missing-evidence behavior.
7. Checkable success and validation.
8. Authorized actions, approval triggers, and stop conditions.
9. Examples only when they lock a difficult format or edge case.

## Shapes

### Bounded task

```text
Goal: [one outcome]
Context: [facts that change the answer]
Requirements: [must-have behavior and constraints]
Output: [format, audience, length, required fields]
Done when: [observable checks]
```

### Coding agent

```text
Goal: [one deliverable]
Starting state: [existing code and facts]
Target state: [required artifact and behavior]
Scope and authorization: [files/resources/actions]
Requirements: [non-negotiable behavior]
Validation: [tests or inspections]
Stop conditions: [approval or missing-evidence gates]
Output: [artifact and concise completion evidence]
```

### Grounded task

```text
Question: [decision needed]
Context: [domain and audience]
Evidence: [allowed sources or retrieval boundary]
Rules: [citation, inference, conflict, and missing-evidence behavior]
Output: [required artifact]
Done when: [coverage and support checks]
```

### Structured output

```text
Task: [operation]
Return exactly: [schema or fields]
Field rules: [types, required values, constraints]
Missing or invalid input: [behavior]
```

For multiple unrelated deliverables, create ordered prompts and state the exact
handoff artifact. For decompilation, extract this contract before rewriting.
