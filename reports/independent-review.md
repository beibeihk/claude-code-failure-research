# Independent infrastructure review — 2026-10-03

A separate Codex agent that did not design the experiment reviewed only drafts,
data and fixture materials. It did not run Claude, contact maintainers, post an
issue/comment or write project files. This record paraphrases its findings.

## Initial findings

1. All 28 candidates have known existing-report risk; V01 overlaps #97155 at the
   broad symptom level. No novel report is established.
2. Shared SPEC/README repeated workflow constraints, contaminating the intended
   instruction-delivery comparison.
3. Drafts correctly distinguish zero Claude trials from access diagnosis and
   offline fixture/mocked-CLI tests; no unsupported root-cause claim appears.
4. Live reproduction, loaded instructions, resolved model, stream compatibility,
   repeated trials, controls and ablations remain unvalidated.
5. Reviewed public data/fixtures contained no credentials or raw user transcript.
   Hashed identifiers remain linkable pseudonymous data.
6. Publishing clearly labeled infrastructure is acceptable; Anthropic submission
   is not permitted by the evidence gate.

## Repair and second review

Before any behavioral run, V01 was amended to 1.0.1. Shared procedural constraints
were removed, the conditional estimand was stated, and the original design was
[archived](design-archive/README.md). The reviewer re-read the updated fixture,
scenario, amendment and final offline record of 42 passing checks.

The second review found the common-workflow confound repaired and no blocker to
publishing the reviewed infrastructure. It did not rerun the offline checks.
This is an evidence/readability/privacy review of the stated materials, not a
certification of every runner implementation path or a live compatibility test.

**Decision: publish infrastructure; do not submit an Anthropic issue.**
`independent_case_review` remains false because no observed case exists.

## No-account client-study review, 2026-10-03

The independent reviewer read the new no-spend policy, model-entry guards,
client-test runner, original TypeScript tests, protocol, reviewed result metadata,
README files and no-cost report. No client, model or paid API was run by the
reviewer; private raw logs and packet traffic were not independently inspected.

The reviewer required one publication correction: the parser counts `(pass)`
test cases, not individual `expect` assertions. The final authored batches are
**11 distinct test cases each executed 10 times, giving 110 passing case
executions**. The report, technical report, protocol and result annotations were
corrected to use that unit.

The review accepted the model/client distinction, scoped Windows virtual-fixture
diagnosis, invalid-batch exclusion, both full-suite timeout records, fail-closed
model-entry guards and public source/license/privacy boundaries. Remaining
timeouts are unresolved. The static review does not certify network behavior or
substitute for the main researcher's measured runs and 50 offline checks.

**Decision after the count-unit correction: publish the scoped client-contract
study and original infrastructure. No production bug, official issue or release
is approved.** `independent_case_review` remains false for production reporting.
