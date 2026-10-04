# Three-candidate real-fixture screen

Research date: **2026-10-04**, native Windows, Claude Code **2.1.288**.
No account/login, model call, authentication change or billed model cost.
The prior timeout study was not rerun. This is a separate bounded screen.

The [protocol](../reports/free-screen-protocol.json) fixed exactly three
candidates and functional criteria before native-engine execution. Eighteen
distinct authored cases ran against **two fresh fixture batches**: **36/36
case executions passed**, with no assertion failure, test timeout or incomplete
native command. These are stability/contract checks, not 36 model trials.

## Evidence and controls

| Candidate | Real oracle and functional control | Case executions | Signal |
|---|---|---:|---|
| FS01: Git state and recovery | Actual ordinary/linked repositories: clean, conflicting merge, successful merge abort; linked conflicting rebase and successful abort. `rev-parse` resolves own/common Git directories and directory entries preserve real marker kinds. | 8 cases × 2 = 16/16 pass | None |
| FS02: filename/output parsing | Actual `status -z`, `diff --numstat -z`, `diff --raw -z -p` and staged rename output. Exact spaces/Chinese names, text edits, binary flag, old/new rename identities and clean status are asserted. | 4 cases × 2 = 8/8 pass | None |
| FS03: nested instruction delivery | Real synthetic AGENTS/CLAUDE files supply exact bytes. First/repeated Read, failed/successful Read, sibling/inside root, whole/partial instruction Read, context recomputation and nested CLAUDE precedence are paired. | 6 cases × 2 = 12/12 pass | None |

FS01 and FS02 call unchanged public source helpers inside the official test
engine; they do not invoke the full diff UI. The linked worktree's conflict
marker lived in its own Git directory, while the common directory had no
`MERGE_HEAD`. Abort controls removed the operation markers. Parser outputs
retained all supported filenames and the expected written lines; the binary
file was not invented as a text edit and the staged rename had zero line edits.

FS03 uses the native engine's `prompt.context` and `tool.call` events through
unchanged agents-md hooks. The first successful nested Read attached two exact
frames, a repeat attached none, and context recomputation allowed delivery
again. A failed Read consumed no delivery. Reading the entire instruction file
marked it delivered; reading one line with an explicit limit did not. A nested
CLAUDE claimed its own directory while a deeper AGENTS remained eligible.
Context recomputation here is an explicit context call, not an actual model
compaction or `/clear` trial. Only the module's default option was exercised.
The failed-Read arm injects the documented `isError` result in the test hook;
it is not a captured real filesystem error or a permission failure. It tests
the delivery guard, while the positive Read contents come from actual files.

## What became more realistic, and what did not

The Python runner creates actual local files and Git histories, executes local
Git, verifies expected operation exit statuses and captures directory entry
kinds and command bytes. It feeds those captures into private TypeScript test
data. Initial and nested walk responses are bounded to the actual fixture's
directories; Read replies use real captured file contents. A new fixture tree
is created for each batch; the native invocations run sequentially at the
unchanged default 5000 ms case deadline.

This removes hand-invented marker/output/content values from these oracle
comparisons. The transport **still replays captured responses**: it does not
validate the production `fs.ancestors` loader, subprocess bridge, live state
refresh, symlink resolution, real permission decisions or model adherence.
The complete CLI/IDE path could fail even though these component cases pass.
The ancestor bridge does not implement imports/exclusion/approval semantics.
Windows forbids tab/newline filenames, so they were not fabricated as real-file
coverage. Non-default instruction modes and live option reload remain untested.

The original helpers and mod hooks are neither patched nor copied into the
public MIT repo. The runner preserves Anthropic's license with private overlays.
Global Git config/identity and user repositories are untouched; fixture commands
use neutral local identity with hooks/signing disabled. Public records contain
static test labels, counts, synthetic marker/name metadata and hashes, without
raw logs, captured absolute paths, complete Git output or upstream implementation.

## Version boundary

Before this screen, official remote HEAD was observed as
`2bfb629dfaff0c8318047a4beb93cf1dc5b58b18`, whose changelog adds 2.1.289.
Comparing that commit to our pinned
`1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528` showed no changes in the tested
mods, type declarations, license, security policy or issue templates. This
does not establish equality of proprietary native engines. The measured CLI
remains **2.1.288**; no 2.1.289 execution or latest-version certification is
claimed. The pin protects reproducibility rather than replacing a future
current-version retest for any real defect signal.

## Decision and reproduction

No candidate produced a functional signal, so none advanced to minimal defect
reproduction or independent production-case review. This is a negative screen
within the specified component scope, not proof of universal client correctness.
The [reporting gate](../reports/reporting-gate.json) stays closed. Production
failures/issues/releases remain **0/0/none** and the original overall goal is
not marked complete.

```bash
python -m runners.run_free_screen --upstream .private/upstream --batches 2
```

Use the existing pinned official checkout/CLI as described in the
[README](../README.md#run-actual-client-experiments--no-account-required).
The [original tests](../research-tests/free-screen) and
[runner](../runners/run_free_screen.py) are public; generated fixture data,
source overlays and native logs remain ignored under `.private/free-screen`.
Reviewed metadata: [Git component results](../results/client-tests/free-screen-diff.json)
and [instruction event results](../results/client-tests/free-screen-agents-md.json).
No new independent case review is claimed for this negative screening cycle.

There are concrete free follow-ups: non-default instruction option contrasts,
the same registered contracts on a separately pinned 2.1.289 engine, and real
HEAD/ref change oracles for refresh probes. They are not automatically promoted
to new failure candidates in this bounded round. Their status and completion
conditions are in [remaining-work](../reports/remaining-work.json).
