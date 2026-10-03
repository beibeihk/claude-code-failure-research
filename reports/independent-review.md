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
