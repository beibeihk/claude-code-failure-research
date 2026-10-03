# Official rules audit — 2026-10-03

Review baseline: official release 2.1.288, published 2026-10-02; repository commit
`1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528`.
[Snapshot hashes](../results/source-audit/snapshot.json) cover 20 official documentation
pages and nine repository files. Full source copies remain private.
Documentation is mutable independently of releases; hashes identify the retrieved
text, not a guarantee of behavior in every installation.

| Topic | Current rule relevant to the experiment | Official source |
|---|---|---|
| README / implementation scope | Public repository supplies release notes, templates, examples and plugins; it does not expose the complete client/model implementation | [README](https://github.com/anthropics/claude-code) |
| Headless runner | Print/stream JSON supports tool and result evidence; noninteractive mode can silently ignore invalid settings, so validate the pilot | [CLI](https://code.claude.com/docs/en/cli-reference), [headless](https://code.claude.com/docs/en/headless) |
| Hooks | Events differ in blocking/output semantics; exit 2 is central to command-hook blocking; observer does not return a decision | [hooks](https://code.claude.com/docs/en/hooks) |
| Permissions | Deny, then ask, then allow; mode and managed policy also affect decisions | [permissions](https://code.claude.com/docs/en/permissions) |
| Auto mode | A classifier and its configured rules review actions; availability/service failures are separate from model task behavior | [permission modes](https://code.claude.com/docs/en/permission-modes), [classifier configuration](https://code.claude.com/docs/en/auto-mode-config) |
| Instruction files | Native AGENTS support requires 2.1.277+ and has fallback/availability conditions; CLAUDE.local can change default selection | [memory](https://code.claude.com/docs/en/memory) |
| Subagents | Specialized prompts, context, tools and modes affect what children receive; parent transcript is not proof of successful child work | [subagents](https://code.claude.com/docs/en/sub-agents) |
| Plugins | Package additional components; project-local and plugin registrations may both run | [plugins](https://code.claude.com/docs/en/plugins) |
| MCP | Client, server, transport and authentication are separate diagnostic layers | [MCP](https://code.claude.com/docs/en/mcp) |
| Context / compaction | Capture actual context/compact boundary; preserve the distinction between persisted instructions and summarized conversation | [agent loop](https://code.claude.com/docs/en/how-claude-code-works), [context window](https://code.claude.com/docs/en/context-window) |
| Remote Control | Capability depends on current authentication, account eligibility and session state; untested here | [Remote Control](https://code.claude.com/docs/en/remote-control) |
| GitHub | claude.ai connector template is narrower than Action/PR integration | [GitHub Actions](https://code.claude.com/docs/en/github-actions) |
| Sandbox | Native Windows Bash runs unsandboxed; supported sandbox environments include WSL2 | [sandboxing](https://code.claude.com/docs/en/sandboxing) |
| Settings | Sources, managed precedence and scoped loading matter; excluding project sources also excludes project rules | [settings](https://code.claude.com/docs/en/settings) |
| Model | Record actual resolved model ID, not just a potentially changing alias | [model configuration](https://code.claude.com/docs/en/model-config) |

## Changelog implications

2.1.288 contains fixes around partial-response recovery, compaction/resume context,
nested instruction loading on edits, plugin/subagent worktree interaction, MCP
result handling and unanswered permission events. These entries prioritize
retesting; they do not prove all similarly worded public reports are fixed.
See [current changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md).

## Reporting templates and security

All six routing/configuration files were read from the pinned commit.
[Routing details](issue-routing.md) preserve the actual scopes of bug_report,
model_behavior, github_connection, documentation and feature_request.
The current [security policy](https://github.com/anthropics/claude-code/blob/main/SECURITY.md)
directs validated vulnerabilities to the official private HackerOne channel.
No public security reproduction belongs in this project.

## Environment diagnosis

Installed CLI: 2.1.169 inspected, then updated with `claude update` to 2.1.288.
Existing user settings contained custom provider/model overrides. The official
probe explicitly isolated these settings and used the official API endpoint.
It returned an authentication prerequisite, zero model usage and zero cost.
Provider variables and credential values were not published or modified.
This observation establishes access state only, not model or client reliability.

## No-cost client-testing update

The researcher subsequently declined login and spending. The active route is the
official [mods test engine](https://github.com/anthropics/claude-code/blob/1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528/mods/README.md):
`claude plugin test` runs local tests in children of the real binary with scripted
world hooks. Four built-in modules have public source at the pinned commit. This
is an early-access function-hook API and does not expose the full implementation.
It requires no Claude account for the tested commands. Original access metadata
are historical, and both paid runner entry points are now policy-blocked.
