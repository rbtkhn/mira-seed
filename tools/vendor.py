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

Divergence is not failure. Every LOCALLY_DIVERGED result must be classified in
lineage/advancement-ledger.json as intentional-scope, candidate-advance, or
unreviewed, so no divergence sits unexamined.
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

        if divergence != "none" and target_skill.exists() and not arguments.overwrite:
            # A skill carrying intended local divergence must not be silently
            # overwritten by an upstream refresh. Refreshing it is a deliberate
            # act that discards the divergence, so it requires --overwrite.
            records[name] = {
                "skipped": "declared divergent and already present; use --overwrite to refresh",
                "vendored_digest": source_digest,
            }
            continue

        target_skill.write_text(
            render_with_provenance(source_text, provenance),
            encoding="utf-8",
            newline="\n",
        )

        reference_names: list[str] = []
        source_references = source_dir / "references"
        if source_references.is_dir() and declared.get("references", True):
            target_references = target_dir / "references"
            target_references.mkdir(exist_ok=True)
            for reference in sorted(source_references.glob("*")):
                if reference.is_file():
                    text = normalized_text(reference)
                    (target_references / reference.name).write_text(
                        text, encoding="utf-8", newline="\n"
                    )
                    reference_names.append(reference.name)

        records[name] = {
            "vendored_digest": source_digest,
            "vendored_at": today,
            "divergence": divergence,
            "references": reference_names,
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

        if not local_skill.exists():
            state = "MISSING_LOCAL"
        elif not source_skill.exists():
            state = "UPSTREAM_REMOVED"
        else:
            source_digest = digest(normalized_text(source_skill))
            local_digest = digest(upstream_equivalent(normalized_text(local_skill)))
            upstream_same = source_digest == expected
            local_same = local_digest == expected
            if upstream_same and local_same:
                state = "UNCHANGED"
            elif not upstream_same and local_same:
                state = "UPSTREAM_MOVED"
            elif upstream_same and not local_same:
                state = "LOCALLY_DIVERGED"
            else:
                state = "FORKED"

        results[name] = {
            "state": state,
            "declared_divergence": declared.get("divergence", "none"),
        }
        counts[state] = counts.get(state, 0) + 1

    unclassified = [
        name
        for name, result in results.items()
        if result["state"] in {"LOCALLY_DIVERGED", "FORKED"}
        and result["declared_divergence"] == "none"
    ]

    report = {
        "counts": counts,
        "results": results,
        "unclassified_divergence": unclassified,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if arguments.strict and unclassified:
        # Divergence itself is permitted. Divergence nobody has classified is not.
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
