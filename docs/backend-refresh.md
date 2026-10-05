# X2: real commit/checkout snapshots through the source backend

On **2026-10-05**, two fresh fixture batches passed **4/4 sequential scenario
test executions**, covering **20 state fetch/hunk checks**. No functional
failure, incomplete native invocation or test timeout occurred. No account,
login, model call or billed model cost was involved.

The [protocol](../reports/backend-refresh-protocol.json), runner and assertions
were committed at `0ec0920` before native execution. The
[reviewed result](../results/client-tests/backend-refresh-X2.json) includes
source, test, protocol, capture, private overlay and executable hashes. No
assertion was revised and no native attempt was retried after seeing results.

## Design and result

Each ordinary repository and linked worktree follows the same real Git sequence.
The native test calls one unchanged `gitBackendOf` instance through all five
states, in `uncommitted` mode. The initial dirty baseline is read once; repository
discovery is also read once. Expected counts are **2 → 0 → 1 → 0 → 1**.

| State | Actual operation and oracle | Both scenarios, both batches |
|---|---|---|
| Before commit | Replace two tracked one-line files, including a spaced path | 2 files, 2 additions, 2 deletions; exact hunks |
| After commit, clean | Commit both replacements | Empty rows, zero totals, empty hunk map |
| After commit, edited | Replace one line again | 1/1/1; removed text comes from the new commit |
| After checkout, clean | Commit the second edit, then checkout the original checkpoint | Different HEAD from the previous capture; empty diff |
| After checkout, edited | Replace the tracked `税收.txt` line | 1/1/1; removed text comes from the checkpoint |

Each expected removal string is checked against actual `git show HEAD:path`
output; each addition string against the actual UTF-8 working-file bytes.
Captured real numstat paths/counts must agree with the named fixture edits
before native tests start. Assertions compare complete file rows, stats,
mode/base, empty stale paths and exact hunk marker strings/line starts. The
documented closing blank context row on a non-final tracked file is included.

The two repeated scenario tests are the sampling units. Twenty stage checks
are not twenty independent trials, model draws or task successes. An additional
offline Python test checks that captured raw patches contain the expected
removal/addition strings, including the new commit and checkpoint bases.

## What was actually exercised

Python executes actual local Git discovery/status/shortstat/numstat/ls-files
and raw patch commands, with the pinned source's repository lead and literal
pathspec flags. It also supplies fixture-only identity, disables signing/hooks
and global config, and uses LF/C-locale guards. No user Git settings change.

The native official **2.1.289** test engine loads a private copy of the pinned
public source at `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528`. Functional hooks are
byte-identical to that source. Source host callbacks replay captured answers
and require the exact source argv and init (pinned cwd, C locale, 5000 ms
timeout). Unknown calls invalidate the test; captured own Git-directory entries
provide the transient-state check. No untracked files or timestamp probes are
needed for these tracked-file, uncommitted-mode scenarios.

The current observed remote HEAD remains
`2bfb629dfaff0c8318047a4beb93cf1dc5b58b18`; its `mods/diff`, issue templates and
security policy have no diff from the tested source pin. That comparison does
not establish identity of proprietary production engines.

This is **source backend behavior with captured real process replies**.
Production process/filesystem transport, actual UI polling/invalidation, timeout
enforcement and a HEAD change between `fetchDiff` and `fetchHunks` remain
untested. The source callbacks enforce their requested init, rather than proving
that a production host honors those options. No Claude instruction retention,
compaction, subagent behavior or model failure frequency is measured.

## Reproduce and decision

Use the source pin above and the private checksum-matching official win32-x64
2.1.289 executable described in [acquisition provenance](free-followup.md#n2-isolated-official-engine).
Do not run the installer or change the global CLI.

```bash
python -m runners.run_backend_refresh --upstream .private/upstream
```

Both native batches completed on their first attempt. An initial offline test
command used a package-style import against a non-package tests directory;
correcting it to `unittest discover` ran the fixture check successfully. That
command error occurred before native execution and is not a client failure.

Raw captures/logs, fixture paths, upstream source and binary remain Git-ignored.
Only reviewed static labels, relations, counts and hashes are published. The
global CLI is still **2.1.288**, and its SHA256 before/after is unchanged:
`84304f7d4b0cd0ebcbe8318695a260151b48991a6659c3366fdd5da290c0ab91`.

No source failure signal emerged. No new independent production-case review
was triggered; this is not an independently rerun production result. The gate
stays closed: **zero confirmed production defects, zero official issues,
no release**. X2 is complete within its registered scope; the original model
research goal remains unfulfilled under the no-account/no-paid-call constraint.
