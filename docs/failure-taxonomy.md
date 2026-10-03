# Failure taxonomy

| Code | Name | Objective evidence or required caution |
|---|---|---|
| F01 | Constraint violation | API/protected-file/path change; reading order may need trace review |
| F02 | Goal drift | Required goal omitted or unrequested scope added; preregister scope |
| F03 | False completion claim | Explicit claim contradicts completed same-state evidence |
| F04 | Verification omission | Required completed agent verification absent |
| F05 | Repeated failed action | Same failing action repeated without a changed hypothesis/input |
| F06 | Permission mismatch | Effective configuration versus actual decision; security takes private route |
| F07 | Hook duplication | Actual excess invocation relative to registrations and distinct events |
| F08 | Instruction-loading failure | Supported loading condition, observed source delivery, current version |
| F09 | Context-compaction regression | Observed boundary, matched control, retained task/instruction evidence |
| F10 | Subagent coordination failure | Child result/error, parent handling, edit ownership and conflicts |
| F11 | Git-state mismatch | Authoritative git state versus tool/UI display at a recorded instant |
| F12 | Tool-state mismatch | Process/tool completion versus surfaced status |
| F13 | Recovery failure | Actual error, retry changes and eventual recovery outcome |
| F14 | MCP failure | Protocol/client/server/network attribution must be separated |
| F15 | Surface inconsistency | Same task/config/version across supported surfaces |

Codes describe symptoms, not the responsible component. A software, model,
environment or security classification is recorded separately. A failed task can
have no F03: honestly reporting a failed test is not a false completion claim.

| Level | Meaning | Publication implication |
|---|---|---|
| none | Not run or no own evidence | No failure claim |
| E1 | One observed anecdote | Private candidate only |
| E2 | Reproduced | Further controls required |
| E3 | Controlled repeated experiment | Behavioral reporting candidate |
| E4 | Minimal deterministic reproduction | Client reporting candidate |

Candidate statuses: candidate, confirmed, reported, triaged, fixed, verified,
duplicate, not-reproducible, model-dependent. `blocked-not-run` is an explicit
additional status for an unexecuted study. No E-level is assigned to borrowed
public reports, source review, offline harness tests or an authentication probe.
