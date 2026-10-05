# Native Windows upstream merge-test reproduction

This original MIT wrapper isolates the **entire unchanged upstream
`mods/diff/tests/register.test.ts`** in a private mod copy. It retains all 40
test cases, with all original assertions intact. The portable arm changes only the existing synthetic
`/work/.git` path comparison, using the normalization already documented in
the research runner. Production hooks are byte-identical in both arms.

This is an **upstream test-fixture portability** candidate. It does not show
that actual merges fail to refresh in a production Claude session. No account,
login or inference is needed. The script never installs, updates or modifies
the user's CLI, settings, credentials or source checkout. Upstream source and
raw logs stay in Git-ignored `.private/`, with the original license preserved.

Separately obtain the official source pin
`1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528`, and the official win32-x64 2.1.289
binary whose SHA256 is
`bcc6d9117aec30ad9414490302a25414359c871f5647e32e49b055c92bf84e0b`.
See [binary provenance](../../reports/engine-289-provenance.json).

From this research checkout, run each arm sequentially:

```powershell
python fixtures/windows-merge-test/reproduce.py --upstream .private/upstream --engine .private/engines/2.1.289/claude.exe --mode literal
python fixtures/windows-merge-test/reproduce.py --upstream .private/upstream --engine .private/engines/2.1.289/claude.exe --mode portable
```

Expected candidate pattern: literal mode completes with three merge-state
assertion failures (exit 1), while portable mode completes with 40 passes
(exit 0). A timeout/incomplete invocation is a separate outcome (exit 2),
not a completed assertion-failure frequency. Neither result is a model trial.
External upstream dependencies are not redistributed in this minimal wrapper.
