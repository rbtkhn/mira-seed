# Advancement Ledger

Generated view of [`advancement-ledger.json`](advancement-ledger.json), which is
canonical.

This records how this repository has come to differ from Mira Core, separating
what came free from starting later from what was actually earned.

A document with this title invites self-congratulation. The guards below exist
because that is the expected outcome rather than an unlikely one. Their
effectiveness is measurable: applied to this ledger's first draft, they deleted
five of seven entries.

## Inherited corrections

Advantages held at birth purely because this repository was designed after its
parent's defects were known. Given, not earned.

**IC-0001. Identity is recorded honestly, with scope captured at decision time.**
Corrects `MI-0001-v1` in the parent's identity ledger. That naming session asked
one bounded question — what to call the system — and the entry that landed also
asserted the architecture of the whole system: that the repository is durable
memory, that agent sessions are temporary activations. Those claims may be true,
but they were not what was asked, and no revision entry marked the widening.

Here, naming requires an invitation with a stated scope, a receipt binding its
exact bytes, and a gate that refuses any entry exceeding that scope. Scope drift
becomes a validation failure rather than an unremarked expansion.

This is a structural correction, not better judgment. The parent's defect had to
happen before the gate was designable.

**IC-0002. Zero aliases at creation.** Corrects the parent's three intake names
for one workflow plus an alias for `geo-strategy`. An audit found the intake
shims redirect to a global target that is not installed — they forward to
nothing — while a stale global `geopolitical-synthesis` marked `status: active`
contradicts the repository-local alias.

The trivial advantage of having no history to be compatible with. The parent
cannot simply delete these; it carries a compatibility obligation this
repository does not.

## Five candidates this ledger's own guard removed

Recorded permanently so a later session does not re-add them having forgotten
why they failed. The guard: every entry must name a parent surface that is
currently defective **and that this repository owns**.

| Rejected claim | Delivered by | Why it fails the guard |
| --- | --- | --- |
| Multi-tenancy by construction | `portable_paths.py`, `mira_state.py` | Shared toolchain; the parent becomes equally multi-tenant |
| Skill hygiene from the start | per-repository deployment registry | Shared toolchain; serves both |
| Absence by design | `mira_memory.py` carrier roster | Shared toolchain; a fix to the parent's carrier logic |
| Harness breadth by default | `mira_continuity.py` adapter protocol | Shared toolchain; gives the parent Cursor capture too |
| A journal backlog threshold | the journal validator | Shared toolchain; protects both |

**Deferral does not resurrect these.** The changes delivering all five are
currently deferred, so they remain live parent defects today. That does not make
them seed advances. The boundary turns on ownership, not timing: a defect in
shared tooling is a parent repair whenever it is made.

## Candidate advances

None. Divergences this repository produced itself would go here, as claims
requiring evidence.

## Confirmed advances

None. Candidates the operator has admitted, digest-bound.

## Backport status

None. Whether Mira Core adopted each confirmed advance, with a commit reference.

## The boundary of what can be claimed

This repository is a second target for Mira Core's toolchain, not a second
codebase. It runs the parent's `scripts/`, so the toolchain arrives entire —
defects included. Known at creation:

- `tools/validate_repo.py --explain-route` returns exit 0 having run no
  validation, so a caller reading exit status is told everything passed.
- `scripts/choice_ledger.py verify` exits 0 unconditionally, so a corrupt or
  empty ledger verifies successfully.
- The validation result cache is unauthenticated, so a cached success can be
  replayed against a tree it was not computed for.
- `scripts/publication_validation.py` falls back to a non-validating command for
  many skill drafts, so a validation request can report success without checking
  the file.

So this ledger may only claim corrections in what this repository owns: its
config, its vendored skill texts, its identity records, and its authored
shelves. Any improvement to shared tooling is a parent improvement this
repository also receives.

The corollary matters more than the rule: **cold-read findings against shared
scripts route to Mira Core as repairs, not into this ledger as advantages.**

## This repository cannot certify itself

Promotion from candidate to confirmed requires what `recursive-learn` already
imposes on method change — an observation, a diagnosis, a persistent
intervention, separate validation, an observed outcome, and an exact
digest-bound operator action.

Explicitly insufficient: passing tests, polish, a plausible argument that
something is better, or self-assessment by a session running here.

Two guards keep entries checkable. Every entry names the exact parent surface it
surpasses, with a file path. And no entry may assert general superiority —
particular work does not become a global ability label, the same rule
`mira-mentor` applies to learners.

## Vendored divergence

`python tools/vendor.py check --strict` compares every vendored contract against
the parent's live source. Divergence is expected and permitted. Divergence nobody
has classified is not, and `--strict` fails while any remains `unreviewed`.

| Skill | State | Classification |
| --- | --- | --- |
| `mira-notes` | LOCALLY_DIVERGED | intentional-scope |
| `mira-essays` | LOCALLY_DIVERGED | intentional-scope |
| the other 16 | UNCHANGED | — |

Expect `mira-voice` next. Vendored verbatim it produces something that sounds
like Mira, which defeats the purpose of a separate repository.
