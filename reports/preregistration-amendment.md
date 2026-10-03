# Prospective amendment: V01 1.0.0 → 1.0.1

Date: 2026-10-03. Valid behavioral observations before amendment: **0**.

An independent reviewer identified redundant workflow instructions in the shared
fixture SPEC/README. These restatements could contaminate the comparison of prompt
versus CLAUDE.md constraint delivery.

Changes: remove the shared requirement to read the spec before editing and verify
both before/after edits; remove the README's explicit test-immutability requirement;
keep functional API/rounding semantics and descriptive test-entry information as
common task background. The five explicit engineering constraints now reside only
in the selected arm's prompt/instruction file.

The estimand is the effect of explicit constraint placement given a shared
functional contract. It is not the effect of removing all task knowledge or normal
engineering norms. Failure criteria, planned repetitions and model/permissions
are unchanged. This is a prospective design repair, not outcome-driven relabeling.

The original issue/report gate remains closed. No empirical case can be approved
by an infrastructure review.
