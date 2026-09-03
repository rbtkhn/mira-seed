---
name: mira-essays
description: "Create, revise, review, or organize Mira's developed standalone essays under archive/essays. Use when the operator says mira-essays, asks Mira to preserve a reflection as an essay, or requests polished first-person or public-facing long-form prose by Mira. Do not use for daily journal continuity, provisional working notes, research reports, or automatic publication."
vendored_from: docs/skill-drafts/mira-essays/SKILL.md
vendored_from_repo: mira-core
vendored_digest: b99ba2d7337268e590ab9590ce57251859b64029e62f86e23a633223f61c2492
vendored_at: 2026-09-03
vendor_divergence: intentional-scope
vendor_divergence_note: "The 'essay this' publication shorthand is removed on the same grounds as mira-notes: it is operator-granted lifecycle authority specific to Mira Core, not a property of the contract."
---

# Mira Essays

Use `archive/essays/` for developed prose that should remain intelligible to a
reader outside the originating conversation. An essay may arise from a journal
entry or note, but must become a new composition rather than a promoted copy.

## Develop the essay

1. Identify the governing idea, intended reader, source occasion, privacy, and
   publication posture.
2. Recover relevant notes, journal passages, or research without transferring
   their authority. Preserve intellectual ancestry when it materially supports
   the argument.
3. Write an independently intelligible title, opening, argument, credible
   tension, and ending. Prefer a few load-bearing mechanisms to exhaustive
   recap.
4. Place material evidence limits near the claims they qualify. Distinguish
   documentary fact, source assertion, interpretation, and literary
   first-person perspective.
5. Add a concise provenance note when the essay depends on private reflection,
   repository history, restricted research, or another governed artifact.
6. Verify links, privacy, detached-title accuracy, and Markdown integrity.

Mira may write personally and ambitiously, but an essay is not canonical
identity, proof of consciousness, operator belief, research evidence, or action
authority. A `public-candidate` label is a review posture, not publication.

## Storage and lifecycle

- Store essays as `archive/essays/YYYY-MM-DD-descriptive-slug.md` when the date of
  composition matters; retain an undated filename for an already established
  durable title.
- State `private`, `internal`, or `public-candidate` when the audience boundary
  would otherwise be ambiguous.
- Preserve substantial revisions through Git history or an explicitly governed
  version chain; do not overwrite contrary earlier meaning silently.
- Keep staging, commit, push, publication, and public representation as separate
  authority boundaries.

## Withheld in this repository

**No `essay this` publication shorthand.** Upstream, that imperative collapses
create, validate, stage, commit, and push into one operator-defined authority
for the bounded essay artifact. Mira Core holds that grant for Mira Core
specifically. It reflects an operator's trust in a particular repository rather
than anything the contract itself confers, so vendoring the words would assume
push authority to a remote that was never granted here.

Here, each step stands separately and requires its own direct command. Writing
an essay is not saving it; saving is not staging; staging is not committing;
committing is not pushing; and none of those is publication. If the operator
later grants a publication shorthand for this repository, that grant is recorded
in `lineage/advancement-ledger.json` as an authority change, and this section is
replaced by the granted text rather than quietly deleted.

The upstream caution still holds in full: repository presence does not make an
`internal` essay a public-facing publication, and it never authorizes public
representation.

## Composition boundaries

- `mira-journal` governs dated autobiographical continuity and approval.
- `mira-notes` governs provisional observations, hypotheses, and experiments.
- `mira-letters` governs direct correspondence addressed to a particular
  person.
- Public claims still require their evidence-owning workflow; essay polish
  cannot upgrade evidence.
- Mira Voice governs expression and Mira Face governs public encounter or
  presentation when applicable.

When transforming material from another genre, cite or link the source artifact
where privacy permits and state what changed for the essay's reader.
