# Windows portability of the official merge-state test fixture

On **2026-10-05**, official win32-x64 **2.1.289** reproduced three deterministic
assertion failures in the entire unchanged official `register.test.ts` file.
They are an **upstream test-fixture defect**, not evidence that actual production
merges fail to refresh. This scope supports an accurately classified test report
without a Claude account or inference; no model/core failure is counted.

| Current native arm | Complete case executions | Result |
|---|---:|---|
| Entire original register file, three invocations | 120 | Each 37 pass / 3 assertion failures; 111 pass, 9 fail total |
| Only its virtual path matcher normalized, three invocations | 120 | Each 40/40; 120 pass total |
| Portable whole suite, one file per native invocation | 210 | 210/210, private overlay restored byte-exactly |
| Existing literal/portable/no-marker diagnostic, unchanged | 3 | 3/3 expected contracts, actual synthetic path observed |
| New minimal wrapper validation, separate shorter paths | 80 | Literal 37/3, portable 40/0; excluded from primary three-repeat frequency |

The three upstream cases vary merge completion time: 3000, 1200 and 300 ms.
Each fails in 3/3 original-file invocations and passes in 3/3 corrected-file
invocations. Those timing contrasts, file isolation and no-marker control help
separate the deterministic fixture mismatch from scheduling and real merge
logic. No randomized causal estimate or independent model sampling is claimed.

## Mechanism and component boundary

The shared test helper hands a synthetic merge directory listing to `fs.list`
only if its requested path equals the POSIX literal `/work/.git`. The current
native diagnostic receives **`C:\work\.git`**, an engine-normalized path for
that same fictional directory. Thus the literal fixture supplies an empty
listing, the initial pane shows an ordinary diff, and the assertion expecting
an unavailable merge state fails. Normalizing only this fixture comparison
delivers its marker and makes all 40 original assertions pass. Hooks remain
byte-identical; the marker and diff replies are scripted test-world responses.

This is a fixture matching error in the public official test file. Production
filesystem/process transport, real merge completion, model retention and
long-horizon agent behavior are not validated by these UI test-world controls.
Real ordinary/linked Git markers were checked separately in the
[earlier source screen](free-candidate-screen.md); that also was captured-response
evidence, rather than a live production-UI test.

The tested source is pinned at `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528`;
current observed main is `2bfb629dfaff0c8318047a4beb93cf1dc5b58b18`, with no diff
to `mods/diff`. The official source, assertions and private copies retain their
license. The global CLI stays 2.1.288 with the unchanged binary SHA256 recorded
in [the prior report](backend-refresh.md). OS: Windows 11 Home Chinese edition,
x64, 10.0.26200; PowerShell 7.6.5. Model calls and billed model cost remain zero.

## Preserved limitations and protocol changes

The [initial protocol](../reports/issue-qualification-protocol.json) was committed
at `bc1ba94` before execution. An unmodified whole-suite attempt stopped at the
120-second outer limit: 115 pass labels, two native case-timeout labels, no footer.
It is incomplete, excluded from complete-suite rates, and does not establish a
test-worker root cause. The planned two portable full-dispatch repeats were
not executed. The continuation at `8084cbb` moved the already registered
single-file and serial controls ahead of further full dispatch; no failed native
attempt was overwritten or secretly retried.

A continuation setup failed during private `copytree` before invoking any
plugin test. The longer destination crossed the Windows path-length limit.
Short private arm names were registered at `c66e6a3`; partial files remain private
and no OS settings were changed. This is a research harness error. Because the
initial full dispatch has environmental confounds, it is not promoted to a
native runner defect.

The unchanged authored path diagnostic and minimal-wrapper validation were
registered at `4194437` after the original-file signal and before their execution.
These are prospective mechanism/replication extensions, not a claim that every
follow-up was designed before observing any failure.

## Reproduce, review and report

The [minimal MIT wrapper](../fixtures/windows-merge-test/README.md) copies official
dependencies privately and isolates the **entire 40-case original register file**.
It redistributes no upstream implementation. Literal and portable modes both
completed in shorter fresh private paths; expected failure exit 1 is distinct
from incomplete exit 2. Native logs, source and complete captures stay private.

Reviewed metadata:
[original register](../results/client-tests/issue-qualification-original-register.json),
[portable register](../results/client-tests/issue-qualification-portable-register.json),
[portable serial suite](../results/client-tests/issue-qualification-portable-serial.json),
[path diagnostic](../results/client-tests/issue-qualification-path-diagnostic.json),
[incomplete full suite](../results/client-tests/issue-qualification-incomplete-full.json).

The [issue body](../reports/drafts/windows-merge-fixture-issue.md) uses the official
bug-report field headings. The [duplicate search](../reports/windows-merge-duplicate-search.json)
identified no exact existing report within its recorded scope; this is not a
proof of novelty. [Independent case review](../reports/windows-merge-independent-review.md)
approved submission as a test-fixture defect, with no blocking modification.
Two non-blocking wording clarifications were applied. No new issue is counted
until GitHub confirms creation; current status is recorded in
`reports/reporting-gate.json`.
