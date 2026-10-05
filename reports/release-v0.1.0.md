# v0.1.0 — Controlled Windows test-fixture reproduction

This community research release packages the validated offline harness,
methodology, failure taxonomy and first confirmed **upstream test-fixture** case,
reported as [Anthropic #99565](https://github.com/anthropics/claude-code/issues/99565).
It contains **zero Claude model coding trials and zero confirmed production
failures**. It is not an Anthropic product release or a verified upstream fix.

- Official native 2.1.289: three complete original 40-case file invocations each
  yield 37 pass / 3 assertion failures. The same three merge-state tests fail.
- A single synthetic path-matcher correction retains all assertions and production
  hooks; three complete controls each pass 40/40. An authored path/no-marker
  diagnostic, serial-file 210/210 control and separate isolated wrapper validation
  support the narrow fixture mechanism.
- Public reproduction instructions, checksum provenance, reviewed metadata,
  independent case review and duplicate-search audit are included. Raw logs,
  credentials and upstream source copies remain private.
- The incomplete whole-suite attempt, pre-test private copy error and unexecuted
  planned repeats are disclosed, with no unsupported scheduling/root-cause claim.
- Offline CI validates the harness on Windows and Ubuntu without installing
  Claude, authenticating or making paid Claude calls. Model execution is blocked
  by the no-account/no-spend research policy.

See [the full report](../docs/windows-merge-test-fixture.md),
[minimum wrapper](../fixtures/windows-merge-test/README.md),
[case card](../docs/failures/F002.md) and
[remaining work](remaining-work.json). Long-horizon, constraint-retention and
false-completion model studies remain unexecuted. Official feedback follow-up
is active; no maintainer response or verified fix is included.
