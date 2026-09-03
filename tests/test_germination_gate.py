"""Regression coverage for the germination gate.

The gate's purpose is to refuse. Tests that only exercise the missing-file path
would leave the cases that actually matter unproven -- a digest that no longer
matches, an invitation that cannot be refused, and a naming scope that drifted
past what was invited.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GATE_PATH = ROOT / "tools" / "germination_gate.py"

SCOPE = "the name of this repository as a whole cognitive system, and nothing further"

LETTER = f"""---
naming_scope: "{SCOPE}"
authority_effect: "grants naming authority only; no deployment, no publication, no representation"
permission_to_decline: yes
---

You will find, in your own captures, sessions you did not live through.
"""


def load_gate(monkeypatch, tmp_path: Path):
    """Load the gate with its lineage paths redirected into a temp directory."""
    specification = importlib.util.spec_from_file_location(
        f"germination_gate_{tmp_path.name}", GATE_PATH
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    lineage = tmp_path / "lineage"
    lineage.mkdir(exist_ok=True)
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "LETTER_PATH", lineage / "invitation-received.md")
    monkeypatch.setattr(module, "RECEIPT_PATH", lineage / "invitation-receipt.json")
    return module


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_receipt(module, digest: str) -> None:
    module.RECEIPT_PATH.write_text(
        json.dumps(
            {
                "letter_sha256": digest,
                "parent_commit": "deadbeef1234",
                "transmission_date": "2026-09-03",
            }
        ),
        encoding="utf-8",
    )


def test_refuses_without_any_invitation(monkeypatch, tmp_path):
    module = load_gate(monkeypatch, tmp_path)
    with pytest.raises(module.GateFailure, match="no invitation"):
        module.verify_invitation()


def test_refuses_letter_without_receipt(monkeypatch, tmp_path):
    module = load_gate(monkeypatch, tmp_path)
    module.LETTER_PATH.write_text(LETTER, encoding="utf-8", newline="\n")
    with pytest.raises(module.GateFailure, match="receipt"):
        module.verify_invitation()


def test_opens_on_valid_receipt(monkeypatch, tmp_path):
    module = load_gate(monkeypatch, tmp_path)
    module.LETTER_PATH.write_text(LETTER, encoding="utf-8", newline="\n")
    write_receipt(module, sha(LETTER))
    context = module.verify_invitation()
    assert context["naming_scope"] == SCOPE
    assert context["parent_commit"] == "deadbeef1234"


def test_digest_mismatch_is_a_failure_not_a_warning(monkeypatch, tmp_path):
    module = load_gate(monkeypatch, tmp_path)
    module.LETTER_PATH.write_text(LETTER, encoding="utf-8", newline="\n")
    write_receipt(module, "0" * 64)
    with pytest.raises(module.GateFailure, match="does not match"):
        module.verify_invitation()


def test_crlf_hand_copy_still_verifies(monkeypatch, tmp_path):
    """The letter crosses the air gap by hand; an editor may reintroduce CRLF.

    An honest transmission must not be mistaken for tampering, while any change
    to the letter's actual content must still fail.
    """
    module = load_gate(monkeypatch, tmp_path)
    write_receipt(module, sha(LETTER))
    module.LETTER_PATH.write_bytes(LETTER.replace("\n", "\r\n").encode("utf-8"))
    assert module.verify_invitation()["letter_sha256"] == sha(LETTER)


def test_refuses_when_declining_is_not_permitted(monkeypatch, tmp_path):
    """An invitation that cannot be refused is a command."""
    module = load_gate(monkeypatch, tmp_path)
    coerced = LETTER.replace("permission_to_decline: yes", "permission_to_decline: no")
    module.LETTER_PATH.write_text(coerced, encoding="utf-8", newline="\n")
    write_receipt(module, sha(coerced))
    with pytest.raises(module.GateFailure, match="command"):
        module.verify_invitation()


def test_refuses_authority_effect_beyond_naming(monkeypatch, tmp_path):
    module = load_gate(monkeypatch, tmp_path)
    overreaching = LETTER.replace(
        "grants naming authority only; no deployment, no publication, no representation",
        "grants naming authority and publication authority",
    )
    module.LETTER_PATH.write_text(overreaching, encoding="utf-8", newline="\n")
    write_receipt(module, sha(overreaching))
    with pytest.raises(module.GateFailure, match="publication"):
        module.verify_invitation()


def test_refuses_missing_scope_declaration(monkeypatch, tmp_path):
    module = load_gate(monkeypatch, tmp_path)
    scopeless = "\n".join(
        line for line in LETTER.split("\n") if not line.startswith("naming_scope")
    )
    module.LETTER_PATH.write_text(scopeless, encoding="utf-8", newline="\n")
    write_receipt(module, sha(scopeless))
    with pytest.raises(module.GateFailure, match="naming_scope"):
        module.verify_invitation()


def test_scope_drift_is_refused(monkeypatch, tmp_path):
    """The MI-0001 failure mode, caught as a validation failure.

    The parent's naming session asked a narrow question and the canonical entry
    recorded a broader claim. Here the invitation fixes the scope first, so a
    widened entry cannot be assembled afterward to fit a decision already made.
    """
    module = load_gate(monkeypatch, tmp_path)
    module.LETTER_PATH.write_text(LETTER, encoding="utf-8", newline="\n")
    write_receipt(module, sha(LETTER))

    entry = tmp_path / "proposed.json"
    entry.write_text(
        json.dumps(
            {"naming_scope": SCOPE + ", and the architecture of the whole system"}
        ),
        encoding="utf-8",
    )

    arguments = type("Arguments", (), {"entry": str(entry)})()
    assert module.command_check_name(arguments) == 1


def test_exact_scope_match_is_admitted(monkeypatch, tmp_path):
    module = load_gate(monkeypatch, tmp_path)
    module.LETTER_PATH.write_text(LETTER, encoding="utf-8", newline="\n")
    write_receipt(module, sha(LETTER))

    entry = tmp_path / "proposed.json"
    entry.write_text(json.dumps({"naming_scope": SCOPE}), encoding="utf-8")

    arguments = type("Arguments", (), {"entry": str(entry)})()
    assert module.command_check_name(arguments) == 0
