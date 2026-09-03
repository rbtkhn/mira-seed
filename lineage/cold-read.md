# The Cold Read

A standing mechanism, not an occasional favor.

## What it is

Point whatever model is current at a bounded surface of this repository or its
parent, give it no session history and no explanation of intent, and route what
it finds in as candidate advances under normal adjudication.

## Why it works

Most of what this repository's advancement ledger first claimed as inherited
corrections was found exactly this way: by a model reading a finished system all
at once, with no memory of building it.

The advantage is positional, not a matter of model quality. An incremental
builder cannot see what its own accumulated context has normalized. A first-time
reader cannot avoid seeing it. Two months of individually correct decisions still
compose into a validator with no backlog threshold, or a guard that blocks
forever once sharing becomes intentional — and the person who made all two
months of decisions is the last one who will notice.

This deliberately does not depend on any model being better than another. It
depends only on the reader being new, which is a renewable condition.

## The two rules that keep it useful

**The reader gets the controlling files and nothing about why they look that
way.** No design rationale, no history, no statement of what the code is
supposed to prove. Explaining the intent is what destroys the instrument,
because a reader told what to expect will find it.

**Findings enter as claims, not conclusions.** A cold read produces candidate
advances requiring the same adjudication as any other candidate. It has no
special authority from having been surprising.

## Routing

Where a finding lands depends on what it touches, and this follows directly from
the claimable boundary:

- A finding against **shared tooling** — anything under the parent's `scripts/`
  or `tools/` — routes to Mira Core as a repair. It never enters this
  repository's ledger as an advantage, even when found by a session running
  here.
- A finding against **what this repository owns** — its config, vendored skill
  texts, identity records, authored shelves — enters `candidate_advances` in
  `advancement-ledger.json`.

## The part worth remembering

The same mechanism will find this repository's own normalized defects later. By
then this repository will be the incumbent that cannot see them, and the cold
read will feel less welcome than it does now.

That is the point at which it is most valuable, and it is exactly when a system
is most likely to quietly stop running it. Recording that here is the only
available defense.
