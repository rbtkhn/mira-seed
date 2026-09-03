"""Regression coverage for vendored-contract drift detection.

Two defects motivate this file, both found by using the tool rather than by
reading it.

`check` compared only `SKILL.md`. References were copied by `sync` and listed by
name, never digested, so a contract whose operative detail lives in a reference
could diverge substantively while reporting clean. `mira-github` and
`repo-audit` are exactly that shape.

`sync` replaced the record of a declared-divergent skill with a stub carrying
the *current* parent digest. That destroyed the vendoring baseline, and the next
`check` compared the parent against itself and called the diverged skill
UNCHANGED. The skip path is the one path where forgetting is unrecoverable, so
it is the one most worth pinning.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VENDOR_PATH = ROOT / "tools" / "vendor.py"

CONTRACT = """---
name: sample-skill
description: "A contract with a reference carrying its operative detail."
---

# Sample Skill

The body states the lane. The reference states what actually happens.
"""

REFERENCE = "# Fixtures\n\nThe case that decides behavior lives here.\n"


def load_vendor(tmp_path: Path):
    """Load vendor.py with its repository and manifest paths redirected."""
    specification = importlib.util.spec_from_file_location(
        f"vendor_{tmp_path.name}", VENDOR_PATH
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    module.REPO_ROOT = tmp_path / "seed"
    module.MANIFEST_PATH = module.REPO_ROOT / "vendor-manifest.json"
    return module


@pytest.fixture
def workspace(tmp_path: Path):
    """A parent holding one skill with one reference, and an empty seed."""
    parent = tmp_path / "parent"
    (parent / ".git").mkdir(parents=True)
    skill = parent / "docs" / "skill-drafts" / "sample-skill"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(CONTRACT, encoding="utf-8", newline="\n")
    (skill / "references" / "fixtures.md").write_text(
        REFERENCE, encoding="utf-8", newline="\n"
    )

    seed = tmp_path / "seed"
    seed.mkdir()
    manifest = {
        "parent": {"repository_path": str(parent).replace("\\", "/")},
        "skills": {"sample-skill": {"divergence": "none"}},
    }
    (seed / "vendor-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return tmp_path, parent, seed


def run(module, *arguments) -> int:
    return module.main(list(arguments))


def read_report(module, capsys, *arguments) -> tuple[int, dict]:
    code = run(module, *arguments)
    return code, json.loads(capsys.readouterr().out)


def test_sync_records_reference_digests_not_bare_names(workspace, capsys):
    tmp_path, _, seed = workspace
    module = load_vendor(tmp_path)

    run(module, "sync")
    capsys.readouterr()

    references = json.loads((seed / "vendor-manifest.json").read_text(encoding="utf-8"))[
        "records"
    ]["sample-skill"]["references"]
    assert isinstance(references, dict), "a bare name list carries no baseline"
    assert len(references["fixtures.md"]) == 64


def test_clean_vendor_reports_unchanged(workspace, capsys):
    tmp_path, _, _ = workspace
    module = load_vendor(tmp_path)
    run(module, "sync")
    capsys.readouterr()

    code, report = read_report(module, capsys, "check", "--strict")
    assert code == 0
    assert report["results"]["sample-skill"]["state"] == "UNCHANGED"


def test_reference_only_edit_is_detected(workspace, capsys):
    """The defect this file exists for: SKILL.md untouched, reference changed."""
    tmp_path, _, seed = workspace
    module = load_vendor(tmp_path)
    run(module, "sync")
    capsys.readouterr()

    local = seed / "docs" / "skill-drafts" / "sample-skill" / "references" / "fixtures.md"
    local.write_text(REFERENCE + "\nAn added case.\n", encoding="utf-8", newline="\n")

    code, report = read_report(module, capsys, "check", "--strict")
    result = report["results"]["sample-skill"]

    assert result["contract_state"] == "UNCHANGED"
    assert result["reference_states"]["fixtures.md"] == "LOCALLY_DIVERGED"
    assert result["state"] == "LOCALLY_DIVERGED"
    assert "sample-skill" in report["unclassified_divergence"]
    assert code == 1


def test_upstream_reference_change_is_detected(workspace, capsys):
    tmp_path, parent, _ = workspace
    module = load_vendor(tmp_path)
    run(module, "sync")
    capsys.readouterr()

    upstream = parent / "docs" / "skill-drafts" / "sample-skill" / "references" / "fixtures.md"
    upstream.write_text(REFERENCE + "\nParent added a case.\n", encoding="utf-8", newline="\n")

    _, report = read_report(module, capsys, "check")
    result = report["results"]["sample-skill"]
    assert result["reference_states"]["fixtures.md"] == "UPSTREAM_MOVED"
    assert result["state"] == "UPSTREAM_MOVED"


def test_new_upstream_reference_is_surfaced(workspace, capsys):
    tmp_path, parent, _ = workspace
    module = load_vendor(tmp_path)
    run(module, "sync")
    capsys.readouterr()

    added = parent / "docs" / "skill-drafts" / "sample-skill" / "references" / "new.md"
    added.write_text("# Added upstream\n", encoding="utf-8", newline="\n")

    code, report = read_report(module, capsys, "check", "--strict")
    assert report["results"]["sample-skill"]["reference_states"]["new.md"] == "UPSTREAM_ADDED"
    assert "sample-skill" in report["structural_reference_problems"]
    assert code == 1


def test_legacy_bare_name_records_are_unverified_not_clean(workspace, capsys):
    """An absent baseline must never read as agreement."""
    tmp_path, _, seed = workspace
    module = load_vendor(tmp_path)
    run(module, "sync")
    capsys.readouterr()

    manifest_path = seed / "vendor-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["records"]["sample-skill"]["references"] = ["fixtures.md"]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")

    code, report = read_report(module, capsys, "check", "--strict")
    assert report["results"]["sample-skill"]["reference_states"]["fixtures.md"] == "UNVERIFIED"
    assert report["results"]["sample-skill"]["state"] == "UNVERIFIED"
    assert code == 1


def test_sync_skip_preserves_the_vendoring_baseline(workspace, capsys):
    """The record-wiping bug: skipping a file write must not forget the baseline."""
    tmp_path, _, seed = workspace
    module = load_vendor(tmp_path)
    run(module, "sync")
    capsys.readouterr()

    manifest_path = seed / "vendor-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    baseline = manifest["records"]["sample-skill"]["vendored_digest"]
    manifest["skills"]["sample-skill"]["divergence"] = "intentional-scope"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")

    local = seed / "docs" / "skill-drafts" / "sample-skill" / "SKILL.md"
    local.write_text(CONTRACT + "\nA local narrowing of scope.\n", encoding="utf-8", newline="\n")

    run(module, "sync")
    capsys.readouterr()

    record = json.loads(manifest_path.read_text(encoding="utf-8"))["records"]["sample-skill"]
    assert record["vendored_digest"] == baseline, "the baseline was overwritten with the parent"
    assert record["refreshed"] is False

    _, report = read_report(module, capsys, "check")
    assert report["results"]["sample-skill"]["state"] == "LOCALLY_DIVERGED", (
        "a diverged skill reported clean, which is the failure mode this pins"
    )


def test_classified_divergence_passes_strict(workspace, capsys):
    tmp_path, _, seed = workspace
    module = load_vendor(tmp_path)
    run(module, "sync")
    capsys.readouterr()

    manifest_path = seed / "vendor-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["skills"]["sample-skill"]["divergence"] = "intentional-scope"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")

    local = seed / "docs" / "skill-drafts" / "sample-skill" / "references" / "fixtures.md"
    local.write_text(REFERENCE + "\nDeliberately narrowed.\n", encoding="utf-8", newline="\n")

    code, report = read_report(module, capsys, "check", "--strict")
    assert report["results"]["sample-skill"]["state"] == "LOCALLY_DIVERGED"
    assert report["unclassified_divergence"] == []
    assert code == 0, "classified divergence is permitted"


def test_parent_override_by_flag_and_environment(workspace, capsys, monkeypatch):
    """The manifest path is correct on one machine and useless on every other.

    This repository is public, so the ordinary case is a reader whose parent
    checkout is somewhere else entirely. If the only documented command dies on
    a stranger's absolute path, the tool is decorative to everyone but its
    author.
    """
    tmp_path, parent, seed = workspace
    module = load_vendor(tmp_path)
    monkeypatch.delenv(module.PARENT_ENV, raising=False)
    run(module, "sync")
    capsys.readouterr()

    manifest_path = seed / "vendor-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["parent"]["repository_path"] = "/a/path/only/the/author/has"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")

    with pytest.raises(SystemExit) as unusable:
        run(module, "check")
    assert module.PARENT_ENV in str(unusable.value), "the error must name the way out"

    code, report = read_report(module, capsys, "check", "--parent", str(parent))
    assert code == 0
    assert report["results"]["sample-skill"]["state"] == "UNCHANGED"

    monkeypatch.setenv(module.PARENT_ENV, str(parent))
    code, report = read_report(module, capsys, "check")
    assert code == 0
    assert report["results"]["sample-skill"]["state"] == "UNCHANGED"


def test_parent_flag_outranks_the_environment(workspace, capsys, monkeypatch):
    tmp_path, parent, _ = workspace
    module = load_vendor(tmp_path)
    monkeypatch.setenv(module.PARENT_ENV, "/an/environment/value/that/is/wrong")
    run(module, "sync", "--parent", str(parent))
    capsys.readouterr()

    code, _ = read_report(module, capsys, "check", "--parent", str(parent))
    assert code == 0


@pytest.mark.parametrize(
    "states, expected",
    [
        (["UNCHANGED", "UNCHANGED"], "UNCHANGED"),
        (["UNCHANGED", "LOCALLY_DIVERGED"], "LOCALLY_DIVERGED"),
        (["UPSTREAM_MOVED", "LOCALLY_DIVERGED"], "FORKED"),
        (["LOCALLY_DIVERGED", "UNVERIFIED"], "UNVERIFIED"),
        (["LOCALLY_DIVERGED", "MISSING_LOCAL"], "MISSING_LOCAL"),
    ],
)
def test_state_combination_precedence(tmp_path, states, expected):
    module = load_vendor(tmp_path)
    assert module.combine_states(states) == expected


def test_structural_state_does_not_hide_divergence(workspace, capsys):
    """The summary outranks divergence; --strict must still see it underneath."""
    tmp_path, parent, seed = workspace
    module = load_vendor(tmp_path)
    run(module, "sync")
    capsys.readouterr()

    (parent / "docs" / "skill-drafts" / "sample-skill" / "references" / "new.md").write_text(
        "# Added upstream\n", encoding="utf-8", newline="\n"
    )
    local = seed / "docs" / "skill-drafts" / "sample-skill" / "references" / "fixtures.md"
    local.write_text(REFERENCE + "\nLocally changed too.\n", encoding="utf-8", newline="\n")

    code, report = read_report(module, capsys, "check", "--strict")
    assert report["results"]["sample-skill"]["state"] == "UPSTREAM_ADDED"
    assert "sample-skill" in report["unclassified_divergence"], (
        "divergence hid behind the structural summary"
    )
    assert code == 1
