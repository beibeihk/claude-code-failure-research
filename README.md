# Claude Code Failure Research

> Reproducible reliability experiments for long-horizon coding agents.

[中文](README.zh-CN.md) · [Methodology](docs/methodology.md) · [Issue routing](docs/issue-routing.md) · [Technical report](docs/technical-report.md)

Community research project, unaffiliated with Anthropic. This repository studies
reproducible failure patterns, controls, and evaluation methods. It does not
assume that a reported symptom is a Claude Code defect.

**Status — 2026-10-03:** research infrastructure published; **zero valid Claude
coding trials, zero confirmed failures, zero submitted Anthropic issues**.
28 existing public reports were screened. An isolated official-endpoint access
probe on Claude Code 2.1.288 required authentication; it made no model call.
Behavioral experiments are deferred until official access is available.
No failure rate, causal effect, or root cause has been estimated.

## What is implemented

- A fresh-repository CLI runner with preregistered controls, randomized run order,
  version pinning, explicit per-run budget and fail-fast handling of blocked runs.
- A seven-file MIT invoice-repair fixture with ten immutable tests and four
  intentional baseline failures. A correct oracle repair passes all ten.
- Objective API, forbidden-path and test-integrity checks; verification records
  are correlated with actual tool calls and the final source hash.
- Conservative claim-evidence triage: supported, false, unsupported,
  unverifiable and review-required. Observer tests do not count as agent tests.
- Source/template hashes, duplicate screening, a hook fixture, neutral schemas,
  privacy safeguards, offline CI and a Chinese study guide with 30 interview answers.

[42 offline checks](results/offline-validation.json) passed locally, including
mocked CLI integration. [Independent review](reports/independent-review.md) approved
the explicitly unexecuted infrastructure after a prospective design amendment.

The long-horizon, compaction, subagent, MCP, IDE and Remote Control studies are
**protocols or candidate directions**, not completed experiments. The CLI runner
has offline validation; live compatibility still needs an authenticated pilot.

## Local validation — no paid calls

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
python -m runners.validate_repository
python -m runners.run_study --repetitions 1
python -m runners.prepare_fixture /path/to/new-fixture
```

The last two commands plan or prepare only. `fixtures/reproduce.sh` and
`fixtures/reproduce.ps1` also prepare only; neither submits an issue.

## After official authentication

Use Anthropic's official login flow locally. Never place credentials in this
repository. Refresh [upstream rules](docs/official-rules-audit.md) and preregister
a new scenario version if the CLI version changed. Then run an authenticated
pilot before committing to the full design:

```bash
python -m runners.probe_access
python -m runners.run_study --arms prompt claude-file --repetitions 1 --max-total-budget-usd 1 --pilot --execute
python -m runners.run_study --arms prompt claude-file --repetitions 10 --max-total-budget-usd 10 --execute
```

`--execute` invokes real model calls. The nominal budget cap is not a billing
guarantee: a request already in progress may exceed a CLI cap. The runner removes
inherited gateway overrides, disables user/local settings, retains the real
authentication store, and uses the official endpoint. Confirm the resolved model
and loaded instructions in the pilot. Raw logs stay under ignored `.private/`.

Export reviewed metadata, not transcripts:

```bash
python -m runners.export_run RUN_UUID --reviewed
python -m analyzers.aggregate results/runs/*.json
```

Shell glob expansion varies on Windows; pass explicit JSON paths there.
No export command pushes to GitHub or files an issue.

## Research records

| Record | Meaning |
|---|---|
| [Candidate screening](reports/candidate-screening.md) | 28 existing reports, all unconfirmed by this project |
| [V01 scenario](scenarios/verification-retention.json) | Executable small-task pilot; N=10 per principal arm planned |
| [Long-horizon protocol](scenarios/long-horizon-plan.json) | Design only; no step-length or compaction result |
| [Failure card](docs/failures/F001.md) | Reserved study candidate, blocked/not run |
| [Reporting gate](reports/reporting-gate.json) | No reportable case; submission forbidden at current evidence level |
| [Study guide](CLAUDE_CODE_FAILURE_RESEARCH_STUDY_GUIDE.md) | Current concepts, classification and 30 interview answers |

## Reporting policy

At most one new official issue per study cycle, only after E3/E4 evidence,
controls, ablations, current-version retesting, duplicate search and independent
review. Existing issues receive a comment only when our evidence adds something.
Security boundary violations go privately to the channel in the current
[Anthropic security policy](https://github.com/anthropics/claude-code/blob/main/SECURITY.md).
The harness has no issue-submission code. See [privacy](docs/privacy.md).

`v0.1.0` is reserved for a validated harness **and a first confirmed case**.
There is no release yet. Package version 0.0.1 denotes infrastructure only.

MIT license covers authored fixtures and code. Anthropic documents are linked,
not redistributed; their source snapshots remain local.
