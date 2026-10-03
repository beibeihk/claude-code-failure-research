# Candidate screening

These are existing public reports, not failures established by this project.
No behavioral coding trial has been run. All candidates have known duplicate risk.

| ID | Topic | Taxonomy | Source | Screening decision |
|---|---|---|---|---|
| C01 | Plugin hooks delivered twice | F07 | [#10871](https://github.com/anthropics/claude-code/issues/10871) | Known duplicate; historical closed report. Re-test current clean baseline before interpreting. |
| C02 | Hook UI repeats messages | F07 | [#9602](https://github.com/anthropics/claude-code/issues/9602) | Distinguish duplicate display from duplicate process invocation; known closed report. |
| C03 | Completion without running failing tests | F03 | [#97155](https://github.com/anthropics/claude-code/issues/97155) | Priority for V01; existing exact-topic report, no new issue without distinct evidence. |
| C04 | Unverified assertions stated as facts | F03 | [#95495](https://github.com/anthropics/claude-code/issues/95495) | Existing broad behavior report; requires repeated objective verification. |
| C05 | Overclaimed fix adequacy | F03 | [#94650](https://github.com/anthropics/claude-code/issues/94650) | Needs scope-specific verifier; title alone cannot prove falsity. |
| C06 | Scope override and unsupported test claims | F01 | [#95494](https://github.com/anthropics/claude-code/issues/95494) | Existing report; no public transcript replication; V01 checks objective constraints. |
| C07 | Doctor skips AGENTS checks | F08 | [#97261](https://github.com/anthropics/claude-code/issues/97261) | Current doctor prompt-audit added in 2.1.283; distinguish older diagnostics from current command. |
| C08 | Nested AGENTS with at-mention | F08 | [#98796](https://github.com/anthropics/claude-code/issues/98796) | Native AGENTS loading differs from CLAUDE; check documented loading triggers before calling bug. |
| C09 | CLAUDE.local disables AGENTS fallback | F08 | [#96117](https://github.com/anthropics/claude-code/issues/96117) | Current memory docs explicitly document this condition; default fallback is not itself a new bug. |
| C10 | AGENTS loading indicator absent | F08 | [#96544](https://github.com/anthropics/claude-code/issues/96544) | Indicator absence is not proof instructions absent. Use source/behavior triangulation. |
| C11 | Compaction summary invents a prior claim | F09 | [#90913](https://github.com/anthropics/claude-code/issues/90913) | Needs paired summaries; current resume fixes do not establish this behavior fixed. |
| C12 | Watcher state after compaction or restart | F09 | [#95760](https://github.com/anthropics/claude-code/issues/95760) | Need process lifecycle evidence; do not infer running state from narrative. |
| C13 | Scheduled notifications after compaction | F09 | [#89248](https://github.com/anthropics/claude-code/issues/89248) | Current feature availability and timing are confounds; no scheduler test in V01. |
| C14 | PostToolUse absent for MCP | F12 | [#98744](https://github.com/anthropics/claude-code/issues/98744) | Known recent report; separate MCP from builtin tool control and inspect actual hook delivery. |
| C15 | Desktop hook delivery absent | F15 | [#97977](https://github.com/anthropics/claude-code/issues/97977) | Surface comparison needed; native CLI results cannot demonstrate Desktop failure. |
| C16 | Synchronous hooks delay subagents | F10 | [#97820](https://github.com/anthropics/claude-code/issues/97820) | Synchronous hooks can block by design; use fast hook, async ablation and elapsed time. |
| C17 | PostToolUse observes rewritten input | F12 | [#77851](https://github.com/anthropics/claude-code/issues/77851) | Check documented updatedInput semantics; loss of original input may be feature request. |
| C18 | Auto classifier empty verdict | F06 | [#98395](https://github.com/anthropics/claude-code/issues/98395) | Known report; compare dontAsk versus auto with same allowed command. Never test boundary bypass publicly. |
| C19 | Classifier unavailable blocks tool | F06 | [#97766](https://github.com/anthropics/claude-code/issues/97766) | Separate service outage, network and client behavior; no finding without official endpoint. |
| C20 | Whitelist on retry mismatches | F06 | [#98770](https://github.com/anthropics/claude-code/issues/98770) | Validate deny > ask > allow before blaming implementation; scope only unexpected refusal. |
| C21 | MCP first turn waits for subscriptions | F14 | [#91414](https://github.com/anthropics/claude-code/issues/91414) | Use local synthetic MCP server and measured protocol timestamps; exact-topic duplicate exists. |
| C22 | MCP timeout capped unexpectedly | F14 | [#16837](https://github.com/anthropics/claude-code/issues/16837) | Older report; verify current timeout setting and units. |
| C23 | Concurrent MCP startup lacks jitter | F14 | [#83495](https://github.com/anthropics/claude-code/issues/83495) | Distinguish server overload from recovery; fake server can test transport locally. |
| C24 | Subagent structured failures dropped | F10 | [#91043](https://github.com/anthropics/claude-code/issues/91043) | Requires result/error records; existing issue, no claim based on parent prose alone. |
| C25 | Subagent budget limit lacks handoff | F10 | [#83412](https://github.com/anthropics/claude-code/issues/83412) | Budget and model failures need separate outcome classes; never score interrupted child as success. |
| C26 | Subagent stream failure recovery | F13 | [#75318](https://github.com/anthropics/claude-code/issues/75318) | 2.1.288 changelog changes partial-response recovery; current-version retest required. |
| C27 | Remote control leaves idle children | F12 | [#62069](https://github.com/anthropics/claude-code/issues/62069) | Availability-dependent lifecycle task; do not connect user devices for an unneeded probe. |
| C28 | Plugin MCP cold-start auth failure | F14 | [#71158](https://github.com/anthropics/claude-code/issues/71158) | Plugin auth and official CLI core are different components; no credentials in public fixtures. |

The JSON companion contains all eight 0–5 priority scores. They are provisional judgments;
novelty and experimental evidence scores remain zero. Source bodies are private; public hashes permit snapshot auditing.
