# Existing free work items N1, N3 and N2

Research date: **2026-10-05**, native Windows. These are exactly the three
previously listed free follow-ups. The old timeout experiments and old-engine
default screen were not rerun. No login, model call, billed model cost or
authentication change was made.

The [protocol](../reports/free-followup-protocol.json) registered option-specific
contexts, fixed Git operations, unchanged timestamps and source/test hashes
before native test execution. All **68 new case executions passed**, without
functional failures, test timeouts or incomplete commands. They are component
contract executions, not independent model trials or production task successes.

| Item | Design and actual result | Evidence boundary |
|---|---|---|
| N1, 2.1.288 | Three authored tests × three non-default modes × two fresh fixture batches: **18/18 pass** | Initial private-manifest option selection; no persisted settings or live reload |
| N3, 2.1.288 | Seven real Git state-pair tests × two fresh repositories: **14/14 pass** | Unchanged source `headKeyOf` with captured file kinds/bytes/timestamps, not live refresh transport |
| N2, private 2.1.289 | Existing 18 free-screen cases, assertions unchanged, two fresh batches: **36/36 pass** | Fixed public source overlay on a different native test engine; not all bundled production mods |

## N1: initial option contracts

Only `userConfig.instructionFiles.default` changes in each private manifest;
the options list and functional hooks remain byte-identical to pinned upstream.
Actual synthetic files supply the instruction bytes. The test hook explicitly
hands managed/user/project/local/memory entries to `prompt.context`; it does not
prove the production loader classifies or finds those files correctly.

| Mode | Initial context | Nested Read | Case executions |
|---|---|---|---:|
| `claude-md` | Handed instruction list remains intact | No AGENTS attachment and no instruction walk | 6/6 |
| `claude-md-and-agents-md` | Root AGENTS joins handed CLAUDE; an already imported AGENTS path is not duplicated | Both nested AGENTS attach, including the directory with a CLAUDE | 6/6 |
| `managed-only` | Only managed and memory kinds remain | No AGENTS attachment and no instruction walk | 6/6 |

Every mode preserves a test-supplied existing tool-context entry. That sentinel
is not a real engine CLAUDE attachment. The first test checks exact membership
and bytes after sorting paths; initial insertion order is not its estimand.
The imported-path test compares the complete resulting list directly. This
round does not exercise `/config`, option hot reload or user settings precedence.

## N3: real HEAD/ref changes

The fixture executes ordinary commits, branch checkout, detached checkout,
`pack-refs`, a linked-worktree commit and a non-ASCII branch commit. It captures
actual file entry kinds, relevant HEAD/ref/log/packed-ref bytes and `stat`
nanoseconds. The helper receives those timestamps converted to milliseconds.
No timestamp is set, preserved artificially or synthesized; no delay is used
to force a distinct stamp.

| State pair | Actual Git object identity | Source key |
|---|---|---|
| Same state captured twice | Same | Equal |
| Commit on the ordinary branch | Changed | Changed |
| Checkout the diverged branch | Changed | Changed |
| Detach at current commit | Same | Changed |
| Pack refs | Same | Changed |
| Linked-worktree commit | Changed | Changed |
| Non-ASCII branch commit | Changed | Changed |

Both linked-worktree batches kept the own HEAD bytes **and own HEAD mtime**
unchanged while the shared ref mtime changed; the key changed as expected.
Detach/pack controls show that the key is a conservative invalidation signal,
not a Git object-ID estimator. The separate unchanged-state control stayed equal.

The probe consumes Python-captured stat values. This does not validate the
production host's timestamp conversion, polling cadence, filesystem/process
bridge or actual UI refresh. These sequential operations with intervening
captures do not rule out timestamp collisions in faster or concurrent updates.
The non-ASCII case confirms the returned key relation, not an instrumented
assertion about which internal fallback branch ran.

## N2: isolated official engine

The official [setup documentation](https://code.claude.com/docs/en/setup#binary-integrity-and-code-signing)
provides a signed release manifest and platform checksum procedure. Version
2.1.289 was downloaded directly from the official archive into `.private`,
without running the installer. Checks passed:

- Binary size **249522848 bytes** and SHA256
  `bcc6d9117aec30ad9414490302a25414359c871f5647e32e49b055c92bf84e0b` match the manifest.
- Windows Authenticode status is `Valid`, signer `Anthropic, PBC`.
- Detached manifest verification reports `VALIDSIG` for documented fingerprint
  `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`, using a private public-key ring.
- The global CLI remains **2.1.288**, with identical before/after binary SHA256.

The first GPG attempt rejected Windows path spelling; relative paths succeeded.
The public-key import emitted an agent-start diagnostic, while detached
verification exited zero with the matching fingerprint. No user keyring or
authentication store was changed. See [acquisition provenance](../reports/engine-289-provenance.json).

The new engine is invoked by explicit executable path with child-only update
and provider/traffic guards. The old assertions' SHA256 values match the
historical private 2.1.288 overlays. Git cases pass 24/24 and instruction cases
12/12, as did the historical two-batch 2.1.288 control. There is **no identified
rescue/fix effect**, since both versions pass. The control is historical rather
than randomized/contemporaneous, and both versions load the same source pin;
this is native test-interface compatibility, not a complete version regression
study of proprietary production implementations.

## Reproduction and decision

With the existing source pin and global 2.1.288 test engine:

```bash
python -m runners.run_free_followup --upstream .private/upstream --item N1
python -m runners.run_free_followup --upstream .private/upstream --item N3
```

For N2, place the official checksum-matching win32-x64 2.1.289 executable at
`.private/engines/2.1.289/claude.exe`, without installing it globally, then run:

```bash
python -m runners.run_free_screen --upstream .private/upstream --batches 2 --engine-289
```

The runner verifies the registered binary checksum and reported version before
tests. Raw captures, native logs, binary, manifest/key files and upstream source
stay private/ignored. Public results contain inspected static labels, mode choices,
state relations, counts and hashes:
[N1](../results/client-tests/followup-N1.json),
[N3](../results/client-tests/followup-N3.json),
[N2 Git](../results/client-tests/followup-N2-diff.json),
[N2 instructions](../results/client-tests/followup-N2-agents-md.json).

No functional signal emerged, so no minimal production defect reproduction or
independent production-case review was triggered. The reporting gate remains
closed: **zero confirmed production defects, zero official issues, no release**.
N1/N3/N2 are completed within their registered scopes. Concrete optional free
extensions and original-goal limitations are in
[remaining-work](../reports/remaining-work.json); the overall goal is not
marked complete and unavailable model evidence is not replaced by these counts.
