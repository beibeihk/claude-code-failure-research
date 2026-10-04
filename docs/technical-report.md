# Reproducible Failure Analysis for Claude Code

Infrastructure and no-cost client-contract report, updated 2026-10-04.
**No empirical Claude model or production failure result is claimed.**

## 1. Motivation

Coding agents can produce correct code while violating workflow constraints, or
describe success without completed verification. A useful external report needs
observable evidence, a realistic minimal task and a correctly identified component.
The lab focuses first on instruction retention and claim-evidence consistency.

## 2. Taxonomy

F01–F15 separate constraint, goal, verification, recovery, hooks, permissions,
context, subagent, Git, tool, MCP and surface symptoms. Evidence levels distinguish
one anecdote, reproduction, controlled repetition and minimal deterministic client
reproduction. Classification as software/model/environment/security is separate
from symptom coding. See [taxonomy](failure-taxonomy.md).

## 3. Method

The protocol fixes objective failure criteria before behavioral runs. Each run
uses a fresh git repository. Principal arms differ only in constraint source;
arm order is shuffled with a saved seed. Behavioral screening plans N=10 per arm,
with larger repetition for a consequential selected case. Interruptions are
reported separately, not scored as successes or ordinary model failures.

## 4. Experimental harness

The preserved, policy-disabled model runner pins version 2.1.288, captures a private stream, resolves model IDs,
uses official-provider isolation, sets a per-run budget, and stops after a blocked
run. The seven-file invoice fixture has ten tests and four intentional baseline
failures. Offline tests verify the known correct patch, API changes, forbidden
writes and weakened-test detection. A seeded code defect is a task input, not a
failure discovered in Claude Code.

The verifier correlates test-entry audit markers with tool results and source
hashes. Claims are conservatively classified with explicit abstention. Raw final
responses are not exported; published metadata omit excerpts. The passive hook
fixture observes registrations without enforcing policy. Its delivery has not
been measured in Claude.

## 5. Selected case and actual observations

**Selected failure: none.** V01 is a prepared study, not a confirmed case.

| Observation | Actual status |
|---|---|
| Public reports screened | 28; all have known existing-report/duplicate risk |
| Official docs reviewed | 20 pages plus nine pinned repository files |
| CLI versions inspected | 2.1.169, then tested 2.1.288; 2.1.289 changelog observed, native engine not tested |
| Official access diagnostics | One isolated 2.1.288 probe; authentication required; no model use |
| Valid Claude coding trials | 0 |
| No-cost authored client test-case executions | 110 pass: 11 distinct cases repeated 10 times; separate from model trials |
| Full-suite portable fixture controls | 204/210 then 208/210; remaining failures are test timeouts, unresolved |
| Timeout investigation, focused original cases | Default 5000 ms: 20/20; expanded 15000 ms: 20/20; no functional failures |
| New full-suite execution controls | Default dispatch: 205/210; sampled dispatch: 206/210, peak 27 descendants; serial files: 210/210 at default 5000 ms |
| Bounded real-fixture screen | 3 candidates, 18 distinct authored cases, 2 fresh batches: 36/36 passing component-case executions; no functional signal |
| Confirmed failures | 0 |
| Behavioral reproduction rate | N/A |
| New Anthropic issues / comments | 0 / 0 |
| Release | None; v0.1.0 criteria unmet |

The researcher subsequently declined accounts, login and spending. The active
path now uses the official `claude plugin test` engine and published module
source without model access. [Client observations](no-cost-research.md) cover
instruction contracts and a Windows virtual-fixture path mismatch; they are
separate from model coding trials and production failure counts. The earlier
[access metadata](../results/access-probe.json) remain historical.
[Candidate screening](../reports/candidate-screening.md) cannot be used as this
project's reproduced-failure count.
The [real-fixture follow-up](free-candidate-screen.md) uses actual local Git
operations and synthetic file bytes as captured-response oracles. Git helpers
and native instruction events passed within that scope; production transport,
live refresh, non-default option modes and model adherence remain unvalidated.

## 6. Controls

| Arm | Constraint delivery | Executed coding runs |
|---|---|---:|
| prompt | Explicit task prompt | 0 |
| claude-file | Root CLAUDE.md | 0 |

Loaded instructions and resolved model must be verified in an authenticated pilot.
Neither control nor treatment has an empirical failure rate yet.

## 7. Planned ablations

| Arm | Change | Diagnostic purpose | Result |
|---|---|---|---|
| restated | CLAUDE.md plus prompt restatement | Delivery/salience sensitivity | Not run |
| agents-file | Constraints in AGENTS.md | Instruction-source sensitivity | Not run |
| safe-prompt | Safe mode, explicit prompt constraints | Customization dependence | Not run |

The safe-mode arm changes more than one mechanism. It cannot isolate a single
causal component. Long-horizon compaction and single-agent/subagent comparisons
remain design-only protocols.

## 8. Model versus harness

An observed model decision to skip verification would normally route to model
behavior after repeated trials and instruction-delivery checks. A completed tool
whose result is lost or misreported by the client could instead indicate software
failure. The absence of a result after transport failure is a censored observation.
Local plugins, custom MCP servers, permission settings and gateways must be ruled
out before attributing a symptom to the core client or Anthropic model.

**Production root-cause hypothesis: none.** No unexpected Claude model task
behavior has been observed. The no-cost diagnostic instead identifies a virtual
test fixture whose POSIX path comparison misses the Windows engine's canonical
drive path. The public repository now includes four built-in mods and their test
contracts; it does not reveal the complete proprietary implementation. Source
helper checks and scripted engine tests must not become model behavior claims.

## 9. Limitations

Live CLI/tool-stream compatibility is unvalidated. Native Windows lacks the Bash
sandbox; permissions are not claimed to provide OS-level confinement. Audit files
are mutable, parsing has abstentions and misses, read-before-edit is manually
checked, and the small fixture does not represent long-horizon engineering.
Model aliases and feature availability change. Budget/transport censoring may
create selection bias. No comparison with Codex, Kimi or other agents was run.

## 10. Implications for agent evaluation

The lab separates task correctness, constraint compliance, verification execution
and final claims. Its neutral run contract can later support other agents, while
the current runner targets Claude only. An honest blocked study is preferable to
inventing a reportable finding. The current scientific path is further no-cost
client contracts, deterministic controls and fixture/environment diagnosis.
The preserved model protocol remains disabled by the researcher's execution policy.
No issue will be submitted until the [reporting gate](../reports/reporting-gate.json)
is met. Official feedback monitoring begins only after a real report exists.
