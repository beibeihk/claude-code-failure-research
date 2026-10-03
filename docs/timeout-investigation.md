# Two default-deadline timeouts: scoped investigation

Research update: **2026-10-04**, native Windows, Claude Code 2.1.288, pinned
upstream commit `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528`.
No account, model request, authentication change or paid model call was needed.
The official remote HEAD was checked and still matched the pinned commit.

## Question and preserved evidence

The earlier [full-suite record](../results/client-tests/full-suite-sequential-control.json)
had 208 passing cases and two failures reported as **5000 ms test timeouts**:

- `register > the start asks nothing of git and registers /diff`: 5693.11 ms.
- `detail-view > each hunk draws as a diff Code named by the path`: 6035.58 ms.

Neither log reported a failed functional assertion for these cases. The timeout
reason is test-runtime evidence, not proof of a lost tool result, stale Git state
or production client hang. The earlier six-timeout overlapping run also remains
public. Historical observations are not overwritten by a later passing run.

The official [test contract](https://github.com/anthropics/claude-code/blob/1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528/mods/types/claude-code.d.ts)
defines a default 5000 ms test deadline and an optional `timeoutMs`; plugins load
on the first engine call. We registered the
[investigation protocol](../reports/timeout-investigation-protocol.json) before
new runs. A wider deadline is a diagnostic parameter, not a product fix.

## Minimal cases and controls

The runner extracts the two named cases and their imports into a private copy,
at their original relative paths. It removes unrelated test cases but keeps the
original assertions, fixtures and hooks implementation. Extraction fails if the
pinned case marker changes. The upstream checkout and user configuration remain
untouched; the upstream license accompanies each private overlay.

All native CLI calls were sequential. The default and expanded-deadline batches
were blocked by arm rather than randomized; they are diagnostic comparisons,
not an identified causal effect of deadline length. Raw logs remain private.

| Arm | Case executions | Failures | Per-case elapsed range |
|---|---:|---:|---|
| Exploratory focused smoke, default 5000 ms | 2 | 0 | 1219.84–1277.91 ms |
| Two original cases, default 5000 ms, 10 repetitions | 20 | 0 | 1061.55–1422.00 ms |
| Same cases, explicit 15000 ms, 10 repetitions | 20 | 0 | 994.22–1593.47 ms |
| Separate phase-timing arm, 15000 ms, 2 repetitions | 4 | 0 | 1388.63–1910.92 ms |

These are **two distinct upstream cases repeatedly executed**, not 40 new
test cases, individual assertion counts or independent model trials. The
previous 110 passing authored-case executions remain a separate study record.
The timing arm changes instrumentation and is not mixed into the original-case
pass total. The expanded deadline did not rescue a failure in this batch: both
deadline arms already passed.

The full default-dispatch retest produced **205 pass / 5 test timeouts**, including
both targets again (7454.66 and 7500.00 ms). Its executed-tree hash matches the
older full-suite control exactly. Therefore the timeout symptom did reproduce
in full-suite context, while failing to reproduce in the two-case isolation.
We distinguish those scopes rather than calling the overall symptom unreproduced.

The timed registration body reached its first engine call after 1 ms, returned
from session start at 1358 and 1843 ms, and completed assertions at 1381 and
1886 ms. The rendering body returned from its first UI render at 1400 and
1890 ms and completed assertions at 1402 and 1901 ms. These observations locate
most of the currently observed latency inside the first engine call. They do
not determine what caused the earlier 5.7–6.0 second runs. Timings use `Date.now`
wall time in a separate instrumented arm, not a packet trace or OS profiler.

## Worker-dispatch extension

The full-suite result motivated a prospectively registered extension. A separate
Windows process-tree sampler saw **27 simultaneous descendants of the native
test CLI** at its sampled peak, across 28 frames. It captured counts only, with
no command lines, usernames, executable paths or credentials. The official
contract describes one binary child per test file; this observed concurrency is
consistent with simultaneous file workers. The sampler's overhead means its
**206 pass / 4 timeout** outcome is not an uninstrumented performance comparison.

The new serial arm dispatches all 30 original test files individually through the
same official engine at the default **5000 ms per-case deadline**. It temporarily
renames inactive test files only inside this run's private overlay, restores
their exact bytes and verifies the executed-tree hash afterward. Hooks and
functional assertions are unchanged. This changes scheduling and fresh-parent
process frequency, so it is not a pure single-parameter causal estimate of
internal worker count.

The first serial attempt stopped after 21/30 files because our metadata parser
recognized `Ran N tests` but rejected the engine's valid `Ran 1 test` footer.
The native CLI's single case passed. This is a harness parser bug, not a Claude
test failure. [Protocol 1.1.1](../reports/timeout-investigation-protocol.json)
records the invalid partial attempt, singular/plural parser repair and full rerun.
The partial attempt is excluded from the full-suite comparison.

The corrected serial-file rerun completed **210/210 cases across 30 files, with
zero test timeouts and zero functional assertion failures**. It retained the
default 5000 ms deadline. The private overlay was restored and its executed-tree
hash was the same `c7efdb0b…` hash as the full default-dispatch controls. No client
hooks or production code patch was applied. This is a verified harness execution
workaround, not a verified production fix.

| Full-suite dispatch comparison | Pass / fail | Scope of conclusion |
|---|---|---|
| Default engine dispatch, no sampler | 205 / 5 | All failures were test timeouts; both target symptoms reproduced |
| Default engine dispatch, separate worker sampler | 206 / 4 | Sampled peak 27 descendants; instrumented timing not directly comparable |
| One original test file per native CLI invocation | 210 / 0 | Same default deadline and restored source tree; this serial execution passed |

## Interpretation

The minimal cases **did not reproduce the two old timeouts**, even under the
original deadline; the full-suite retest reproduced timeout symptoms. Current
observations, including the passing serial-file run, support sensitivity to
dispatch and full-suite execution context. Both focused deadline arms already
passed; no rescue effect of expanding the deadline was identified. Runtime
initialization, worker scheduling or resource
contention remain possible mechanisms; this study does not isolate one internal
cause or promise serial dispatch never times out on another machine.
There is no basis to say a production defect was fixed, that the older runs were
invalid, or that changing the deadline corrects Claude Code.

The three earlier merge-state assertion failures are a different diagnosis:
the literal POSIX virtual-path stub failed to deliver a merge marker to the
Windows engine. The focused startup/rendering cases do not use that merge stub;
we have not conflated path mismatch with their timeout cause.

Production bug confirmation: **none**. Evidence is insufficient for a new
official issue. No E3/E4 production case, model reliability estimate or release
is claimed. A further timeout must be preserved and classified before retesting,
with its configured deadline, full/focused scope and assertion outcome separate.

## Reproduce without model access

With the pinned official checkout and CLI already available, run sequentially:

```bash
python -m runners.run_client_tests --upstream .private/upstream --suite diff --selection upstream-focused --repetitions 10
python -m runners.run_client_tests --upstream .private/upstream --suite diff --selection upstream-focused --test-timeout-ms 15000 --repetitions 10
python -m runners.run_client_tests --upstream .private/upstream --suite diff --selection upstream-focused --test-timeout-ms 15000 --instrument --repetitions 2
python -m runners.run_client_tests --upstream .private/upstream --suite diff --selection upstream-portable-control
python -m runners.observe_test_workers --upstream .private/upstream
python -m runners.run_client_tests --upstream .private/upstream --suite diff --selection upstream-serial-files
```

Reviewed counts, source/executed-tree hashes, error kinds, elapsed times and
synthetic timing marks are in [results/client-tests](../results/client-tests).
The runner distinguishes test timeouts, assertions, test-runtime exceptions and
unknown failures. It never publishes exception bodies or raw transcripts.
The no-spend [policy](../research-policy.json) remains enforced.
