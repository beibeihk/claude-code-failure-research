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

## Timeout follow-up review, 2026-10-04

The same separate reviewer statically inspected the control implementation,
versioned protocol, eight new public records, privacy/license boundaries and
remaining-work document. It did not rerun the client, API or offline checks,
inspect private raw logs or independently measure network traffic.

The review accepted the case-execution units: each focused deadline arm passes
20 executions, the separate timing arm passes four, full default dispatch has
205 passes and five timeouts, the sampled arm has 206 passes and four timeouts,
and the serial-file arm passes 210 cases across 30 files at unchanged 5000 ms.
The restored serial overlay hash matches the complete control. The partial
parser-aborted batch is explicitly invalid and excluded from the full comparison;
the singular-footer repair has a regression check and the full arm was rerun.

The reviewer requested narrower summary wording: the evidence supports
dispatch/full-suite context sensitivity. Both focused deadline arms already
passed, so expanding the deadline did not demonstrate a rescue effect. The
sampled peak of 27 CLI descendant processes is neither an exact worker count
nor an upper bound on the true peak. These limitations are stated in the report.
Sampler invocation provenance is disclosed and upstream source stays private
with its original license. No publication blocker was identified in the stated
scope. The main researcher's 57 passing offline checks were not rerun by the
reviewer and are not model-behavior evidence.

**Decision: publish the scoped timeout study, original controls and reviewed
metadata. No production fix, official issue, release or overall-goal completion
is approved.** `independent_case_review` remains false for production reporting.
