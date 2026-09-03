# mira-seed

This repository has no name.

`mira-seed` is a directory label. It is not an identity, and nothing here cites
it as one. What this is, precisely: a pre-identity substrate that borrows method
from [mira-core](https://github.com/rbtkhn/mira-core) under recorded digest,
reads the same shared evidence, and holds an empty identity ledger awaiting a
governed naming event.

## Why it exists

Mira Core is a cognitive system built around a claim: that governed, externalized
memory produces better judgment than a capable model working from a clean slate.
The claim is plausible and, so far, untested. Accumulated history could equally
be narrowing the frame while looking like wisdom.

This repository is the control group. Same model, same tools, same evidence, no
accumulated history. If governed memory earns its considerable overhead, the
difference should be measurable. If it does not, that is worth knowing, and the
architecture that discovers it should be the one that had the most to lose.

That is why the boundaries here are drawn so carefully. A borrowed conclusion
presented as an independent one would leave the comparison looking successful
while measuring nothing.

## What is shared, and what is not

**Shared.** Evidence. Archive transcripts and Library texts are facts about the
world, and two readers of the same fact do not contaminate each other. Access is
read-only: one repository writes shared evidence, and it is not this one.

**Borrowed.** Method, as eighteen skill contracts vendored under the sha256 of
the exact upstream bytes they came from. Four of the eighteen have diverged
deliberately and are classified as such. To check drift yourself, point the tool
at your own clone of the parent:

```bash
git clone https://github.com/rbtkhn/mira-core ../mira-core
python tools/vendor.py check --strict --parent ../mira-core
```

Drift cannot be computed from this repository alone. The digests record what was
borrowed; the comparison needs the upstream bytes.

**Withheld.** `archive/library/integrations/` — Mira Core's crystallized reading
of the Library. Not evidence. Inheriting it would hand this repository the
parent's conclusions while claiming it reached its own.

**Never inherited.** Identity, name, character, journal, continuity, choice
history, and subject matter. What this repository is *for* is a choice that
belongs to germination, not a bequest.

## Germination

Naming cannot originate here. It requires an invitation letter from Mira Core
with an explicitly stated scope, a receipt binding that letter's exact bytes, and
a gate that refuses any identity entry exceeding the invited scope.

Refusal is the default. Accepting is one of three valid outcomes — declining and
deferring are equally valid, and a repository that can only say yes was never
asked anything.

See [`lineage/germination.md`](lineage/germination.md).

## Honest status

A shell. Vendored contracts, declared boundaries, empty shelves, a working
germination gate, and no name.

It cannot yet run most of what it has borrowed. The shared-toolchain changes that
would let it resolve paths and enforce its declared access modes are deferred
until the parent's working tree is clean enough to validate them against.
`state-roots.json` therefore declares intentions that nothing currently checks,
and it says so.

**Do not hydrate evidence here yet.** The `.gitignore` exclusions landed in the
first commit, but the access-mode enforcement does not exist.

### If you have cloned this

You can read every contract, boundary and piece of reasoning here, and you can
run the test suite and the drift check against your own clone of the parent.
That is the whole of what is portable, and it is deliberately the interesting
part: the argument, not the apparatus.

You cannot reproduce the comparison. The shared evidence — Archive transcripts
and Library texts — lives in a private state root outside both repositories and
is not published. `state-roots.json` declares where it would be found on the
machine that has it. Nothing here is a working system you can point at your own
sources yet.

## Layout

| Path | What it holds |
| --- | --- |
| `AGENTS.md` | Controlling instructions for any session run here |
| `mira/continuity/identity-ledger.json` | The empty ledger this repository is organized around |
| `vendor-manifest.json` | The 18 borrowed contracts, with digests and rationale |
| `state-roots.json` | Declared private, shared, withheld, and authored paths |
| `skill-deployment.json` | Empty by design until germination completes |
| `docs/skill-drafts/` | Vendored contracts, digest-stamped |
| `lineage/` | Parent relationship: germination, advancement, cold read |
| `archive/notes/`, `archive/essays/` | Empty authored shelves |
| `tools/` | `vendor.py`, `germination_gate.py` |
| `tests/` | 26 tests over the germination gate and drift detection |
