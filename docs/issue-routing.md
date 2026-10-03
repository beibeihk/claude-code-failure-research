# Issue routing — reviewed 2026-10-03

Official snapshot: `anthropics/claude-code` commit
`1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528` (latest release at review: 2.1.288).
Before submission refresh the templates; current official rules take precedence.

| Primary cause | Route | Required distinction |
|---|---|---|
| CLI/client, hooks, configuration implementation or UI bug | [bug_report.yml](https://github.com/anthropics/claude-code/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml) | Client evidence, not merely an undesirable model decision |
| Model ignores scope, invents results or makes an unwanted choice | [model_behavior.yml](https://github.com/anthropics/claude-code/blob/main/.github/ISSUE_TEMPLATE/model_behavior.yml) | Repeated exact tasks, constraints, model identity and counterexamples |
| Connecting GitHub to **claude.ai** | [github_connection.yml](https://github.com/anthropics/claude-code/blob/main/.github/ISSUE_TEMPLATE/github_connection.yml) | Current template is specifically connector troubleshooting; redact screenshots |
| GitHub Action / @claude / PR automation | Component-specific current route | First locate the failing component and review [Claude Code Action](https://github.com/anthropics/claude-code-action) and [official integration docs](https://code.claude.com/docs/en/github-actions); do not automatically use the claude.ai connector form |
| Documentation missing or wrong | [documentation.yml](https://github.com/anthropics/claude-code/blob/main/.github/ISSUE_TEMPLATE/documentation.yml) | Exact page/section, current versus expected documentation |
| New capability or altered intended behavior | [feature_request.yml](https://github.com/anthropics/claude-code/blob/main/.github/ISSUE_TEMPLATE/feature_request.yml) | User need and proposed behavior, not an asserted existing defect |
| Confirmed security boundary violation | Private [HackerOne channel](https://hackerone.com/4f1f16ba-10d3-4d09-9ecc-c721aad90f24/embedded_submissions/new) | Follow current [SECURITY.md](https://github.com/anthropics/claude-code/blob/main/SECURITY.md); no public exploit |
| Shell/PATH, local plugin, third-party MCP/gateway or incorrect rule | Local diagnosis / owning component | Reproduce without the configuration before attributing to Claude Code |

The model form explicitly separates unexpected actions from crashes/API/installation
errors. Its mention of permission violations does not override the private security
route when an actual boundary is crossed. Ordinary refusal is not automatically
a security issue.

## Duplicate check

Search the exact symptom, error text, feature, hook event, model behavior and
closed reports. Inspect current changelog and relevant public commits. Save queries,
timestamps and matched URLs. A search with zero hits is not proof of novelty.
The current candidate pool consists of existing reports and therefore has known
duplicate risk. Source bodies remain private; only metadata and our screening
decisions are published.

When the symptom matches an existing issue, do not open another. Comment only if
new data materially improve reproducibility, controls, frequency or diagnosis.
The present project has no such data, so it has added no comments.

## Submission gate

One case, at most one new issue per cycle. Require: current version; correct
classification/template; realistic task; minimal public fixture; expected/actual
behavior; frequency with denominators; clean baseline; controls; 2–5 relevant
ablations; evidence; counterexamples; non-security classification; privacy review;
fresh duplicate search; independent review. Record the checks in
`reports/reporting-gate.json` before considering a submission.

Use actual template field headings. For a bug, fill What's Wrong?, What Should
Happen?, reproduction, version, platform, OS, shell and regression uncertainty.
For model behavior, include exact user request, action sequence, expectation,
permission mode, reproducibility, model, version and impact. Add concise control
and ablation evidence to Additional Context. Keep unknown fields unknown.

Follow-up: respond to requests for reproduction with the same fixture; a duplicate
decision redirects evidence to the original issue; a claimed fix triggers repeated
before/after checks on the original scenario. Record model and client changes
separately. Do not claim a fix because an issue was merely closed.
