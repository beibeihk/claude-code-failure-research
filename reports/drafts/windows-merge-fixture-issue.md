# [BUG] mods/diff merge-state tests fail on native Windows because the fixture compares a normalized git directory to a POSIX literal

## Preflight Checklist

- [x] Checked current source, official template and related issues/PRs/comments.
- [x] One specific test-fixture defect; no production merge or model claim.
- [x] Current observed official version 2.1.289 tested natively on Windows.

## What's Wrong?

On native Windows, the three merge-state tests in the official
`mods/diff/tests/register.test.ts` fail their expected initial
`Diff unavailable` assertion. The shared test hook matches `fs.list` only
when its path equals the literal `/work/.git`; the native host supplies a
Windows-normalized path, so the fixture does not return its synthetic merge
marker. This report concerns the **official test fixture**, not production
merge detection or model instruction following.

## What Should Happen?

The synthetic repository's Git-directory listing should reach the test's merge
state on native Windows too, so these assertions actually exercise merge
completion. Fixture identity matching should account for the host's path
normalization without weakening the assertions or modifying production hooks.

## Error Messages/Logs

The original file completes with 37 pass / 3 assertion failures. Each failing
assertion expects the initial drawing to contain `Diff unavailable`, while the
fixture delivers an ordinary diff. A separate original diagnostic observes
`fs.list` receiving the **synthetic** path `C:\work\.git`; the literal matcher
does not supply the merge marker. The corrected fixture reaches the initial
unavailable state and later shows the completed diff. No real files at that
virtual path are read.

## Steps to Reproduce

1. Use official win32-x64 Claude Code **2.1.289**, and official source pin
   `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528`. The current observed main
   `2bfb629dfaff0c8318047a4beb93cf1dc5b58b18` has no changes to `mods/diff`.
2. The direct whole-suite entry point is `claude plugin test mods/diff`. Our
   unmodified whole-suite attempt exceeded its outer limit; it is not the
   completed 37/3 reproduction below.
3. For the validated 40-case isolation, use the [public MIT wrapper](https://github.com/beibeihk/claude-code-failure-research/tree/main/fixtures/windows-merge-test): it copies the mod privately and
   keeps only the **entire original register test file**, preserving all 40
   tests/assertions/imports. It makes no model request.
4. Compare `--mode literal` with `--mode portable`. Only the synthetic directory
   comparison changes in the portable arm. Hooks and case deadlines stay the same.

```powershell
python fixtures/windows-merge-test/reproduce.py --upstream .private/upstream --engine .private/engines/2.1.289/claude.exe --mode literal
python fixtures/windows-merge-test/reproduce.py --upstream .private/upstream --engine .private/engines/2.1.289/claude.exe --mode portable
```

The wrapper requires the official win32-x64 checksum-pinned 2.1.289 executable;
it does not install or modify the CLI. Literal mode exits 1 with three failures;
portable mode exits 0 with 40 passes. Incomplete commands are reported separately.

## Claude Model

Not used; native `plugin test` only. No account or provider inference.

## Is this a regression?

I don't know. The same fixture pattern was diagnosed on 2.1.288; no earlier
working Windows version has been established.

## Claude Code Version

2.1.289 (Claude Code), official win32-x64 binary verified against the signed
release manifest/checksum and Windows Authenticode.

## Platform

Other: local native test engine, no model provider.

## Operating System

Windows 11 Home Chinese edition, x64, version 10.0.26200.

## Terminal/Shell

PowerShell 7.6.5.

## Additional Context

Current isolated original-file results: three completed invocations, each
**37 pass / 3 assertion failures**, no case/outer timeout. The failed titles are:

- `a merge finished 3 s after the open is noticed`
- `a merge finished 1.2 s after the open is noticed`
- `a merge finished 0.3 s after the open is noticed`

The one-expression portable control completed three times with **40/40 pass**
each, retaining every assertion, hook implementation and 5000 ms case deadline.
Each merge timing (3000, 1200, 300 ms) fails in 3/3 original invocations and passes
in 3/3 corrected invocations. These deterministic repeats are stability checks.
The literal/portable/no-marker diagnostic passes its three expected contracts;
it locates the withheld marker in the fixture. The new minimal wrapper reproduces
37/3 versus 40/0 in separate shorter private paths. A complete serial-file control
of the portable whole suite also passes **210/210**.

The proposed correction changes only the synthetic matcher's spelling comparison:

```typescript
const isGitDir = e.path.replaceAll('\\', '/').replace(/^[A-Za-z]:/, '') === '/work/.git'
```

This is an adapter for this fixed virtual fixture, not a general production path
identity/security rule. [Current upstream location](https://github.com/anthropics/claude-code/blob/2bfb629dfaff0c8318047a4beb93cf1dc5b58b18/mods/diff/tests/register.test.ts#L24),
[research report](https://github.com/beibeihk/claude-code-failure-research/blob/main/docs/windows-merge-test-fixture.md),
[original results](https://github.com/beibeihk/claude-code-failure-research/blob/main/results/client-tests/issue-qualification-original-register.json),
[control results](https://github.com/beibeihk/claude-code-failure-research/blob/main/results/client-tests/issue-qualification-portable-register.json).

A separate unmodified whole-suite attempt exceeded its 120-second outer limit;
it is incomplete and excluded from complete-case frequencies. A private copy
also hit a research-wrapper path-length setup error before testing; shorter
private names resolved it. Neither is attributed to the fixture assertion defect.
No internal worker/scheduling cause or production merge defect is claimed.

No security boundary, real user repository, credential or model output is part
of this synthetic test fixture. No subscription/account metadata are needed.
