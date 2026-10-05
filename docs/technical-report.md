# Reproducible Failure Analysis for Claude Code

Infrastructure and no-cost client-contract report, updated 2026-10-05.
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

**Selected case: F002, an official upstream Windows test-fixture defect.**
[Reported as #99565](https://github.com/anthropics/claude-code/issues/99565)
after current-version controls and independent case review. V01 remains a
prepared model study; no production or model failure is confirmed.

| Observation | Actual status |
|---|---|
| Public reports screened | 28; all have known existing-report/duplicate risk |
| Official docs reviewed | 20 pages plus nine pinned repository files |
| CLI versions inspected | 2.1.169; native component tests on 2.1.288 and isolated official 2.1.289; global CLI remains 2.1.288 |
| Official access diagnostics | One isolated 2.1.288 probe; authentication required; no model use |
| Valid Claude coding trials | 0 |
| No-cost authored client test-case executions | 110 pass: 11 distinct cases repeated 10 times; separate from model trials |
| Full-suite portable fixture controls | 204/210 then 208/210; remaining failures are test timeouts, unresolved |
| Timeout investigation, focused original cases | Default 5000 ms: 20/20; expanded 15000 ms: 20/20; no functional failures |
| New full-suite execution controls | Default dispatch: 205/210; sampled dispatch: 206/210, peak 27 descendants; serial files: 210/210 at default 5000 ms |
| Bounded real-fixture screen | 3 candidates, 18 distinct authored cases, 2 fresh batches: 36/36 passing component-case executions; no functional signal |
| N1 option contracts | 3 tests × 3 non-default modes × 2 batches: 18/18 pass; initial private-manifest selection only |
| N3 HEAD/ref probe | 7 actual Git state-pair cases × 2 batches: 14/14 pass; captured source-helper replies, no production polling |
| N2 native engine comparison | The same 18 authored screen cases × 2 fresh batches on private 2.1.289: 36/36 pass; no rescue effect since historical 2.1.288 also passes |
| Confirmed production / model failures | 0 / 0 |
| Confirmed upstream test-fixture defects | 1: F002; original register file 37/3 in each of three invocations; single-matcher control 40/40 in each of three |
| Behavioral reproduction rate | N/A |
| New Anthropic issues / comments | 1 / 0; official #99565, test-fixture scope |
| Release | [v0.1.0 published](https://github.com/beibeihk/claude-code-failure-research/releases/tag/v0.1.0), validated harness and first fixture case; Windows/Ubuntu CI passed for the exact release target |

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
live refresh and model adherence remain unvalidated. The subsequent
[free follow-up](free-followup.md) tests initial non-default mode selection,
actual HEAD/ref source probes and the same contracts on a private official
2.1.289 engine. Option reload and proprietary production transport remain untested.

The [F002 report](windows-merge-test-fixture.md) preserves incomplete full-suite
attempts separately. Its three original repetitions and three matcher controls
are complete; the no-marker diagnostic and shorter-path wrapper validate the
fixture mechanism. The 210/210 serial-file control is not a default parallel
full-suite success. [Independent case review](../reports/windows-merge-independent-review.md)
approved the narrow test-fixture report. An active daily heartbeat checks official
feedback and notifies only on a meaningful change; no response is yet recorded.

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
The [reporting gate](../reports/reporting-gate.json) passed for F002; one official
issue has been submitted. Production and model reporting gates remain closed.
Official feedback monitoring is active; a fixture correction is not counted as
a verified Anthropic fix until an upstream change is tested on the original case.
