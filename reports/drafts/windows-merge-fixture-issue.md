# [BUG] mods/diff merge-state tests fail on native Windows because the fixture compares a normalized git directory to a POSIX literal

Draft only. Not submitted; current control results and independent case review
must be completed before publication to Anthropic.

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

Only the required assertion summary and sanitized virtual paths will be included.
Full source and native logs remain private; reviewed per-case metadata are linked.

## Steps to Reproduce

1. Use official win32-x64 Claude Code **2.1.289**, and official source pin
   `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528`. The current observed main
   `2bfb629dfaff0c8318047a4beb93cf1dc5b58b18` has no changes to `mods/diff`.
2. Run the original mod tests with `claude plugin test mods/diff`.
3. To isolate the relevant fixture, use the public MIT wrapper in
   `fixtures/windows-merge-test/reproduce.py`: it copies the mod privately and
   keeps only the **entire original register test file**, preserving all 40
   tests/assertions/imports. It makes no model request.
4. Compare `--mode literal` with `--mode portable`. Only the synthetic directory
   comparison changes in the portable arm. Hooks and case deadlines stay the same.

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

Windows; exact public OS/version metadata to be recorded before submission.

## Terminal/Shell

PowerShell; exact version to be recorded before submission.

## Additional Context

Current isolated original-file results: three completed invocations, each
**37 pass / 3 assertion failures**, no case/outer timeout. The failed titles are:

- `a merge finished 3 s after the open is noticed`
- `a merge finished 1.2 s after the open is noticed`
- `a merge finished 0.3 s after the open is noticed`

Control results, minimal-wrapper verification, duplicate search and independent
review are pending. A separate whole-suite attempt exceeded its 120-second outer
limit; it is incomplete and excluded from complete-case frequencies. This draft
does not claim an internal worker/scheduling cause or a production merge defect.

No security boundary, real user repository, credential or model output is part
of this synthetic test fixture. No subscription/account metadata are needed.
