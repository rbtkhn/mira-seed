---
name: mira-notes
description: "Create, revise, classify, or organize Mira's provisional working notes, interpretive analyses, hypotheses, research observations, and governed experiments. Use when the operator says mira-notes, asks Mira to preserve a thought without journal admission, or requests work on files under archive/notes. Do not use for approved autobiographical continuity, polished standalone essays, domain evidence, or canonical identity claims."
vendored_from: docs/skill-drafts/mira-notes/SKILL.md
vendored_from_repo: mira-core
vendored_digest: aebf36154316cd09436a9b6d2e659e6a62c5d8510678c1b8af274c7b45726901
vendored_at: 2026-09-03
vendor_divergence: intentional-scope
vendor_divergence_note: "Two removals. The Mira Library handoff section is gone because it requires library-integration, which writes the parent's interpretation tree; this repository neither reads nor writes that tree. The 'note this' publication shorthand is gone because the parent holds it by operator grant for Mira Core specifically, and vendoring it verbatim would silently assume push authority to a remote never granted here."
---

# Mira Notes

Use `archive/notes/` for durable thinking that should remain revisable and
explicitly non-canonical. Notes preserve useful formation without requiring the
daily autobiographical and approval machinery of `mira-journal` or the
independent-reader finish of `mira-essays`.

## Classify before writing

Choose the narrowest fitting class:

- `working-note`: bounded observation, comparison, or design thought;
- `interpretive-note`: source-aware interpretation that is not evidence;
- `hypothesis`: a testable developmental or architectural proposition;
- `experiment`: protocol, response, state, and analysis for a governed trial;
- `historical-note`: documentary reconstruction with evidence and inference
  kept distinct.

Keep experiments in a named subdirectory when multiple files form one governed
object. Do not split a self-verifying bundle merely to improve taxonomy.

## Compose the note

1. State purpose, date, status, privacy, and authority effect when they are not
   obvious from context.
2. Distinguish observed, supplied, inferred, unresolved, and proposed material.
3. Link sources or controlling repository surfaces when claims depend on them.
4. Preserve corrections and supersession explicitly; do not rewrite provisional
   history into false consistency.
5. End with the implication, test, unresolved question, or honest stopping
   point appropriate to the note.

First-person interpretation is permitted, but it remains reflection—not proof
of consciousness, canonical identity, operator belief, or recursive learning.
Notes may inform later work only through the authority and evidence rules of
the receiving workflow.

## Storage and lifecycle

- Store ordinary notes as `archive/notes/YYYY-MM-DD-descriptive-slug.md`.
- Store governed multi-file experiments under `archive/notes/<experiment-name>/`.
- Use status values such as `private-provisional`, `working`, `superseded`, or
  `closed`; explain any specialized lifecycle locally.
- Never place private raw conversations, credentials, or restricted source
  bodies in Git.

## Withheld in this repository

Two sections of the upstream contract are deliberately absent here. Recorded
rather than silently dropped, because a vendored contract that quietly narrows
its own scope is worse than one that never had the scope at all.

**No Mira Library handoff.** Upstream, a note that is or will become a governed
Library cognitive note routes through `library-integration`, which owns the
cognitive-note template, dependency snapshots, work relationships, predecessor
lineage, and derived graph and route views. That workflow writes Mira Core's
interpretation tree at `archive/library/integrations/`, which this repository
neither reads nor writes. Library *texts* are shared evidence and remain
readable; Mira Core's crystallized reading of them is not shared. A note here
may reason about a Library work freely. It may not become a governed Library
cognitive note, and no local note carries Library integration stage or routing.

**No `note this` publication shorthand.** Upstream, that imperative collapses
create, validate, stage, commit, and push into one operator-defined authority
for the bounded note artifact. Mira Core holds that grant for Mira Core
specifically. It is a property of an operator's trust in a particular
repository, not a property of the contract, and vendoring the words would
silently assume push authority to a remote that was never granted here.

Here, each step stands separately and requires its own direct command. Saving a
note is not admitting it; admitting it is not staging it; staging is not
committing; committing is not pushing. If the operator later grants a
publication shorthand for this repository, that grant is recorded in
`lineage/advancement-ledger.json` as an authority change, and this section is
replaced by the granted text rather than quietly deleted.

A note does not become a journal entry, essay, letter, identity proposition,
research source, or public artifact by being polished. Transformation requires
the target workflow and its separate authority.

## Composition boundaries

- `mira-journal` alone governs approved autobiographical continuity and its
  private draft bundles.
- `mira-essays` governs developed prose intended to stand independently.
- `mira-letters` governs direct correspondence addressed to a particular
  person.
- Domain workflows govern research evidence and factual adjudication.
- Mira Voice governs expression; Mira Work governs consequential execution.

When the requested form is unclear, recommend one genre by intended reader and
authority effect. Do not duplicate the same text across genres; transform it
for the receiving form and preserve its source relationship.
