"""Vendor Mira Core skill contracts into this repository under digest provenance.

This repository borrows method from Mira Core rather than forking its toolchain.
Borrowed contracts therefore carry a recorded digest of the exact upstream bytes
they came from, so divergence becomes a visible, classified fact instead of an
accident discovered later.

Subcommands
    sync    copy declared skills from the parent and record provenance
    check   compare each vendored skill against the parent's live source

`check` reports one of four states per skill:

    UNCHANGED        parent matches the recorded digest; local body matches too
    UPSTREAM_MOVED   the parent changed since vendoring; local body did not
    LOCALLY_DIVERGED the local body changed; the parent did not
    FORKED           both changed independently

The state covers the SKILL.md contract and every file under references/. A
contract's operative detail often lives in a reference -- mira-github's failure
fixtures, repo-audit's finding schema -- so comparing only SKILL.md would report
clean while a contract diverged substantively. The per-skill state is the
combination: any reference that diverged makes the skill diverged.

Divergence is not failure. Every LOCALLY_DIVERGED result must be classified in
lineage/advancement-ledger.json as intentional-scope, candidate-advance, or
unreviewed, so no divergence sits unexamined.

UNVERIFIED means a reference exists with no recorded digest to compare against.
It is not divergence, but it is a blind spot, so --strict rejects it too.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "vendor-manifest.json"

PROVENANCE_KEYS = (
    "vendored_from",
    "vendored_from_repo",
    "vendored_digest",
    "vendored_at",
    "vendor_divergence",
    "vendor_divergence_note",
)


def normalized_text(path: Path) -> str:
    """Decode and normalize newlines so digests are platform-stable.

    Mira Core carries no repository-wide `text=auto`, so identical content can
    differ by line ending across checkouts. Digests must not depend on that.
    """
    raw = path.read_bytes().decode("utf-8")
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_frontmatter(text: str) -> tuple[list[str], str]:
    """Return (frontmatter_lines, body) without reformatting either.

    Textual rather than YAML round-tripping: descriptions contain colons and
    quotes, and reserializing them would rewrite bytes we are trying to track.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return [], text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], "\n".join(lines[index + 1 :])
    return [], text


def strip_provenance(frontmatter: list[str]) -> list[str]:
    kept: list[str] = []
    for line in frontmatter:
        key = line.split(":", 1)[0].strip()
        if key in PROVENANCE_KEYS:
            continue
        kept.append(line)
    return kept


def upstream_equivalent(text: str) -> str:
    """The vendored file with provenance removed, for comparison to the parent."""
    frontmatter, body = split_frontmatter(text)
    if not frontmatter:
        return text
    kept = strip_provenance(frontmatter)
    return "---\n" + "\n".join(kept) + "\n---\n" + body


def render_with_provenance(source_text: str, provenance: dict[str, str]) -> str:
    frontmatter, body = split_frontmatter(source_text)
    if not frontmatter:
        raise SystemExit("vendored skill has no YAML frontmatter to annotate")
    kept = strip_provenance(frontmatter)
    added = [f"{key}: {provenance[key]}" for key in PROVENANCE_KEYS if key in provenance]
    return "---\n" + "\n".join(kept + added) + "\n---\n" + body


def reference_files(skill_dir: Path) -> list[Path]:
    references = skill_dir / "references"
    if not references.is_dir():
        return []
    return sorted(path for path in references.glob("*") if path.is_file())


def reference_digests(skill_dir: Path) -> dict[str, str]:
    return {path.name: digest(normalized_text(path)) for path in reference_files(skill_dir)}


def recorded_reference_digests(recorded: dict) -> tuple[dict[str, str], bool]:
    """Return (name -> digest, digests_available).

    Records written before references were digested carry a bare list of names.
    That shape is reported as UNVERIFIED rather than silently treated as clean,
    because an absent baseline is exactly the blind spot this comparison exists
    to remove.
    """
    references = recorded.get("references")
    if isinstance(references, dict):
        return references, True
    if isinstance(references, list):
        return {name: "" for name in references}, False
    return {}, True


def compare_digests(expected: str, source: str, local: str) -> str:
    upstream_same = source == expected
    local_same = local == expected
    if upstream_same and local_same:
        return "UNCHANGED"
    if not upstream_same and local_same:
        return "UPSTREAM_MOVED"
    if upstream_same and not local_same:
        return "LOCALLY_DIVERGED"
    return "FORKED"


DIVERGENT_STATES = {"LOCALLY_DIVERGED", "FORKED"}
STRUCTURAL_STATES = ("MISSING_LOCAL", "UPSTREAM_REMOVED", "UPSTREAM_ADDED", "UNVERIFIED")


def combine_states(states: list[str]) -> str:
    """Roll component states up into one summary state for the skill.

    A skill is only UNCHANGED when every part of it is. Structural problems
    outrank content divergence in the summary because they describe a set that
    no longer lines up rather than bytes that moved. The summary is for a
    reader; --strict evaluates the component states directly, so nothing hides
    behind the label chosen here.
    """
    distinct = {state for state in states if state != "UNCHANGED"}
    if not distinct:
        return "UNCHANGED"
    for state in STRUCTURAL_STATES:
        if state in distinct:
            return state
    if "FORKED" in distinct or {"UPSTREAM_MOVED", "LOCALLY_DIVERGED"} <= distinct:
        return "FORKED"
    return distinct.pop()


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"missing {MANIFEST_PATH.name}; nothing is declared vendored")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def parent_root(manifest: dict) -> Path:
    root = Path(manifest["parent"]["repository_path"])
    if not (root / ".git").exists():
        raise SystemExit(f"parent repository not found at {root}")
    return root


def command_sync(arguments: argparse.Namespace) -> int:
    manifest = load_manifest()
    parent = parent_root(manifest)
    today = date.today().isoformat()
    records: dict[str, dict] = {}

    for name, declared in sorted(manifest["skills"].items()):
        source_dir = parent / "docs" / "skill-drafts" / name
        source_skill = source_dir / "SKILL.md"
        if not source_skill.exists():
            raise SystemExit(f"declared skill {name} not present in parent")

        source_text = normalized_text(source_skill)
        source_digest = digest(source_text)
        target_dir = REPO_ROOT / "docs" / "skill-drafts" / name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_skill = target_dir / "SKILL.md"

        divergence = declared.get("divergence", "none")
        provenance = {
            "vendored_from": f"docs/skill-drafts/{name}/SKILL.md",
            "vendored_from_repo": "mira-core",
            "vendored_digest": source_digest,
            "vendored_at": today,
            "vendor_divergence": divergence,
        }
        note = declared.get("divergence_note")
        if note:
            provenance["vendor_divergence_note"] = json.dumps(note, ensure_ascii=False)

        wants_references = declared.get("references", True)
        upstream_references = reference_digests(source_dir) if wants_references else {}
        previous = manifest.get("records", {}).get(name, {})

        if divergence != "none" and target_skill.exists() and not arguments.overwrite:
            # A skill carrying intended local divergence must not be silently
            # overwritten by an upstream refresh. Refreshing it is a deliberate
            # act that discards the divergence, so it requires --overwrite.
            #
            # Recording still happens. An earlier version replaced the record
            # with a bare stub carrying the *current* parent digest, which
            # destroyed the vendoring baseline: the next check compared the
            # parent against itself and reported the diverged skill UNCHANGED.
            # Skipping the file write must not mean forgetting what was borrowed.
            records[name] = {
                "vendored_digest": previous.get("vendored_digest", source_digest),
                "vendored_at": previous.get("vendored_at", today),
                "divergence": divergence,
                # A legacy bare-name list carries no baseline, so upgrade it to
                # the parent's current digests. Sound only because the contract
                # is diverged locally rather than upstream: the parent's bytes
                # are still the bytes this was vendored from. A skill whose
                # parent had also moved would need re-vendoring, not a rewrite.
                "references": (
                    previous["references"]
                    if isinstance(previous.get("references"), dict)
                    else upstream_references
                ),
                "refreshed": False,
                "skip_reason": "declared divergent and already present; use --overwrite to refresh",
            }
            continue

        target_skill.write_text(
            render_with_provenance(source_text, provenance),
            encoding="utf-8",
            newline="\n",
        )

        if upstream_references:
            target_references = target_dir / "references"
            target_references.mkdir(exist_ok=True)
            for reference in reference_files(source_dir):
                (target_references / reference.name).write_text(
                    normalized_text(reference), encoding="utf-8", newline="\n"
                )

        records[name] = {
            "vendored_digest": source_digest,
            "vendored_at": today,
            "divergence": divergence,
            "references": upstream_references,
            "refreshed": True,
        }

    manifest["last_sync"] = today
    manifest["records"] = records
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"synced": len(records), "records": records}, indent=2))
    return 0


def command_check(arguments: argparse.Namespace) -> int:
    manifest = load_manifest()
    parent = parent_root(manifest)
    results: dict[str, dict] = {}
    counts: dict[str, int] = {}

    for name, declared in sorted(manifest["skills"].items()):
        recorded = manifest.get("records", {}).get(name, {})
        expected = recorded.get("vendored_digest")
        source_skill = parent / "docs" / "skill-drafts" / name / "SKILL.md"
        local_skill = REPO_ROOT / "docs" / "skill-drafts" / name / "SKILL.md"

        reference_states: dict[str, str] = {}

        if not local_skill.exists():
            contract_state = "MISSING_LOCAL"
        elif not source_skill.exists():
            contract_state = "UPSTREAM_REMOVED"
        else:
            contract_state = compare_digests(
                expected,
                digest(normalized_text(source_skill)),
                digest(upstream_equivalent(normalized_text(local_skill))),
            )
            recorded_references, have_digests = recorded_reference_digests(recorded)
            upstream_references = reference_digests(parent / "docs" / "skill-drafts" / name)
            local_references = reference_digests(REPO_ROOT / "docs" / "skill-drafts" / name)

            for reference in sorted(set(recorded_references) | set(upstream_references) | set(local_references)):
                if reference not in recorded_references:
                    reference_states[reference] = "UPSTREAM_ADDED"
                elif not have_digests:
                    reference_states[reference] = "UNVERIFIED"
                elif reference not in local_references:
                    reference_states[reference] = "MISSING_LOCAL"
                elif reference not in upstream_references:
                    reference_states[reference] = "UPSTREAM_REMOVED"
                else:
                    reference_states[reference] = compare_digests(
                        recorded_references[reference],
                        upstream_references[reference],
                        local_references[reference],
                    )

        component_states = [contract_state, *reference_states.values()]
        state = combine_states(component_states)

        results[name] = {
            "state": state,
            "contract_state": contract_state,
            "reference_states": reference_states,
            "declared_divergence": declared.get("divergence", "none"),
        }
        counts[state] = counts.get(state, 0) + 1

    # Evaluated over component states rather than the rolled-up summary, so a
    # divergence cannot hide behind a structural label that outranks it.
    unclassified = [
        name
        for name, result in results.items()
        if result["declared_divergence"] == "none"
        and DIVERGENT_STATES & ({result["contract_state"], *result["reference_states"].values()})
    ]
    structural = {
        name: [
            component
            for component, component_state in result["reference_states"].items()
            if component_state in STRUCTURAL_STATES
        ]
        for name, result in results.items()
    }
    structural = {name: components for name, components in structural.items() if components}

    report = {
        "counts": counts,
        "results": results,
        "unclassified_divergence": unclassified,
        "structural_reference_problems": structural,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if arguments.strict and (unclassified or structural):
        # Divergence itself is permitted. Divergence nobody has classified is
        # not, and neither is a reference with no baseline to compare against.
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync = subparsers.add_parser("sync", help="vendor declared skills from the parent")
    sync.add_argument(
        "--overwrite",
        action="store_true",
        help="refresh skills carrying declared divergence, discarding local edits",
    )
    sync.set_defaults(handler=command_sync)

    check = subparsers.add_parser("check", help="compare vendored skills to the parent")
    check.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero when a divergence has no recorded classification",
    )
    check.set_defaults(handler=command_check)

    arguments = parser.parse_args(argv)
    return arguments.handler(arguments)


if __name__ == "__main__":
    sys.exit(main())
