# No-account client reliability study

Date: 2026-10-03. Claude Code 2.1.288, native Windows. The researcher's current
choice is **no account, no login and no paid model access**. This is an executed
client-component study, with **zero Claude model coding trials**.

The official [mod documentation](https://github.com/anthropics/claude-code/blob/1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528/mods/README.md)
publishes four built-in mods and describes `claude plugin test`. The real binary
runs tests in child processes; test hooks answer the world beneath each mod.
Calls not answered by these hooks throw. No model is involved in this command.
The interface is early access and does not expose all proprietary client code.

## What ran

| Experiment | Actual result | Interpretation |
|---|---|---|
| Unmodified upstream agents-md suite, exploratory | 5/5 pass | Public module's existing contracts execute without login |
| Unmodified upstream diff suite, exploratory | 207/210 pass; 3 merge cases fail | Candidate test mismatch requiring diagnosis |
| Eight authored instruction test cases, 10 sequential repetitions | 80/80 test-case executions pass | Three cases use real engine hooks; five use public source helpers |
| Three authored Windows diff test cases, 10 sequential repetitions | 30/30 test-case executions pass after documented harness amendment | Literal-path negative control, portable-path control and no-merge control |

The two authored batches produce **110 passing test-case executions: 11 distinct
authored cases each run 10 times**. This counts test cases, not individual `expect`
assertions or coding tasks. Repetition checks deterministic stability, not independent model draws.
The instruction tests cover fallback, CLAUDE precedence, unreadable walks,
path/content deduplication, directory boundaries and managed filtering. They
do not cover every loading mode or demonstrate that a model follows instructions.

## Why the three merge assertions failed

The upstream integration fixture supplies an `fs.list` response only when the
request equals the literal `/work/.git`. The Windows engine canonicalizes this
virtual path into `C:\work\.git`. Consequently, the stub returns an empty list,
withholding `MERGE_HEAD`. The pane then displays an ordinary diff, which disagrees
with the fixture's expected `Diff unavailable` state.

This explanation came from recorded synthetic `fs.list` paths. Changing only
slashes still failed because the drive prefix remained. An authored control
normalizes slashes and the drive prefix **only for this virtual `/work` fixture**.
With client hooks, scripted Git responses, mock clock and UI flow held fixed:

| Arm, 10 sequential repetitions | While merge marker is present | After marker removal |
|---|---|---|
| Original literal POSIX stub | Normal diff; marker was never delivered, 10/10 | Normal diff, 10/10 |
| Portable virtual-fixture stub | `Diff unavailable`, 10/10 | Normal diff, 10/10 |
| No-marker control | Normal diff, 10/10 | Not a transition experiment |

This identifies a **test-fixture platform mismatch**, not a demonstrated
production Git-pane defect. Stripping drive letters is not proposed as a fix
for real filesystem identity or product path handling.

## Invalid and load-sensitive observations

Before the final authored batch, the diagnostic assertion referred to a `process`
global unavailable in the official test environment. That was our harness error.
The 10-repeat batch had one `ReferenceError` and two passing checks per repetition;
its observations are exploratory and excluded from the 110 passing case executions.
[Protocol 1.0.1](../reports/no-cost-protocol.json) records the prospective repair:
remove that assumption and explicitly restrict the diagnostic to native Windows.
The invalid batch is retained privately; its run ID and reason remain public.

A full-suite portable control initially overlapped another native test run and
produced **204 pass / 6 per-test timeouts**. Its three merge assertions passed.
A sequential retest produced **208 pass / 2 per-test timeouts**, also with all
three merge assertions passing. These two timeouts were investigated on
**2026-10-04**: focused default-deadline and expanded-deadline batches each
passed 20/20, while a full default-dispatch retest had 205 pass / 5 timeouts.
A separate worker sampler observed a peak of 27 descendants of the native CLI.
The corrected serial-file full-suite run passed **210/210 at the original 5-second
case deadline**. This is a scoped harness workaround; no production bug or fix
is confirmed, and the internal latency cause remains unresolved. See the
[timeout investigation](timeout-investigation.md) for original assertions,
preserved invalid parser attempt, phase timing and the scheduling controls.
The upstream engine has a 5-second per-test
timeout, so execution load must be controlled. A complete suite footer does
not establish that every failed test is a client defect.

## Reproduction and evidence handling

Commands are in the [README](../README.md#run-actual-client-experiments--no-account-required).
Run them sequentially with the pinned upstream checkout and CLI. No upstream
checkout, user settings or authentication store is modified. Authored tests are
in [research-tests](../research-tests); source overlays and full logs remain
private, preserving Anthropic's license outside this repository's MIT coverage.

The child environment removes provider credentials/overrides, disables optional
traffic and directs accidental provider requests to a closed loopback endpoint.
We did not capture packets and do not claim all possible runtime network traffic
was measured. The commands do not invoke model inference, and model cost is zero.

Reviewed metadata under [results/client-tests](../results/client-tests) contain
counts, versions, source/executed-tree hashes, log hashes and synthetic `/work`
observations only. No raw transcript or source implementation is exported.
The historical [model study](../scenarios/verification-retention.json) is preserved,
but [research-policy.json](../research-policy.json) blocks its execution and the
old API probe before model invocation.

## What this enables next

The subsequent [bounded three-candidate screen](free-candidate-screen.md) ran
18 distinct authored cases against two fresh actual file/Git fixture batches:
36/36 passing executions. Merge/rebase recovery, supported filename parsing
and default nested instruction delivery had no functional signal. This is a
captured-response component comparison, not production transport verification.
The 2.1.289 changelog was observed but the native engine tested was 2.1.288.
The [2026-10-05 follow-up](free-followup.md) subsequently completed N1/N3/N2:
18/18 initial non-default option executions, 14/14 actual HEAD/ref source-probe
executions, and 36/36 unchanged screen cases on a verified private 2.1.289
engine. All are scoped component contracts; production transport, live reload
and model evidence remain unvalidated.

Further free experiments can test nested instruction attachment, option selection,
Git state transitions, diff parsing/rendering, hook order and recovery against
real component contracts. A real filesystem/Git fixture should validate any
candidate production failure before reporting. A local scripted API endpoint or
substitute model could later exercise more CLI plumbing, but neither has been
implemented or executed here; neither would establish Claude model reliability.

Confirmed production failures: **0**. Official issues/comments: **0/0**.
The [reporting gate](../reports/reporting-gate.json) remains closed and there is
no v0.1.0 release. The original goal of a high-quality official report remains
conditional on a novel, independently reviewed E3/E4 production case.
