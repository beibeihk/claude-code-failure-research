# Passive hook ledger fixture

Authored MIT observer; no plugin dependency and no blocking decision. Each hook
invocation creates one UUID metadata file to avoid shared-log append races.
It records event/tool names, hashed correlation IDs and a monotonic timestamp.
Raw hook input, prompts, commands, paths and account fields are not logged.

Prepared fixture only: actual Claude hook delivery has not been tested. The
observer's offline unit test is not a hook reliability result. Review the current
exec-form `command`/`args` support before an authenticated pilot.

Use this fixture with one local registration per event and compare no-hook versus
hook runs on the same harmless task. Match native CLI stream tool IDs against
hashed IDs in the ledger. Do not treat two different tool calls, two registrations,
session resume, or a Stop/StopFailure distinction as duplicate delivery.

`python -m analyzers.hooks PATH_TO_LEDGER_FOLDER` produces counts and tentative
ordering diagnostics. Those diagnostics require stream correlation before a bug
claim. Task preparation does not submit an issue.
