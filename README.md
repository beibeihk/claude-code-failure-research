# Claude Code Failure Research

> Reproducible reliability experiments for long-horizon coding agents.

[中文](README.zh-CN.md) · [Methodology](docs/methodology.md) · [Issue routing](docs/issue-routing.md) · [Technical report](docs/technical-report.md)

Community research project, unaffiliated with Anthropic. This repository studies
reproducible failure patterns, controls, and evaluation methods. It does not
assume that a reported symptom is a Claude Code defect.

**Status — 2026-10-03:** active **no-account, no-paid-model** client research.
Claude Code 2.1.288's official `plugin test` engine runs locally without login.
We have executed instruction-loading contracts and controlled Git-pane fixture
diagnostics. **Zero valid Claude model coding trials, zero confirmed production
failures, zero submitted Anthropic issues.** 28 existing reports were screened.
See the [no-cost study](docs/no-cost-research.md) for actual counts and scope.
No model failure rate or long-horizon performance estimate is claimed.

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
- A pinned official client-test runner, original instruction contracts, and a
  Windows virtual-Git-fixture path control. No Anthropic source is redistributed.
- A [no-spend execution policy](research-policy.json) that blocks both the old
  access probe and the live coding runner, including direct `run_one` calls.

[Offline checks](results/offline-validation.json) passed locally, including
mocked CLI integration. [Independent review](reports/independent-review.md) approved
the explicitly unexecuted infrastructure after a prospective design amendment.

The long-horizon, compaction, subagent, MCP, IDE and Remote Control studies are
**protocols or candidate directions**, not completed experiments. The CLI runner
has offline validation; model execution is disabled under the researcher's policy.

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

## Run actual client experiments — no account required

Use the installed **2.1.288** official CLI and a separate pinned official source
checkout. The test engine is an early-access API; other versions need a protocol
revision. These commands make no model request:

```bash
git clone https://github.com/anthropics/claude-code.git .private/upstream
git -C .private/upstream checkout --detach 1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528
python -m runners.run_client_tests --upstream .private/upstream --suite agents-md --selection research --repetitions 10
python -m runners.run_client_tests --upstream .private/upstream --suite diff --selection upstream
python -m runners.run_client_tests --upstream .private/upstream --suite diff --selection research --repetitions 10
python -m runners.run_client_tests --upstream .private/upstream --suite diff --selection upstream-portable-control
```

Run the commands sequentially: the engine's per-test timeout is sensitive to
concurrent load. The authored diff diagnostic is registered for native Windows;
the upstream suites and authored instruction tests also have other-platform
entry points, not yet validated here. The runner clears inherited provider
credentials/overrides in child memory, points accidental provider requests to a
closed loopback endpoint, and disables nonessential traffic. It never alters the
user's credentials or settings. Private source overlays preserve the upstream
license; the authored tests remain MIT. Raw output stays under `.private/`.

`plugin test` exercises real client hooks/UI and public helper functions against
scripted world interactions. It does not sample a Claude model or measure coding
task behavior. Repeated deterministic tests are stability checks, not independent
model draws. Test failures require environment and fixture diagnosis first.

The old model-study protocol is preserved for audit, but `--execute` and
`runners.probe_access` now fail before any CLI model invocation. No login is a
prerequisite for the current research path. A future policy change requires a
new explicit researcher instruction; CLI flags cannot override it.

Client-test summaries are written to `.private/client-tests/RUN_UUID/summary.json`.
Review their labels and authored observation payloads before manually copying
metadata to `results/client-tests` with the schema's `public_review` marker.
No raw log is exported. The following preserved exporter is for the historical
model-study schema; it does not accept client-test summaries:

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
| [No-cost client study](docs/no-cost-research.md) | Executed component contracts and fixture diagnosis; no model use |
| [No-cost protocol](reports/no-cost-protocol.json) | Versioned repetitions, controls, limitations and amendment |
| [V01 scenario](scenarios/verification-retention.json) | Preserved model protocol; execution disabled by no-spend policy |
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
