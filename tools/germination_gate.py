"""Refuse identity naming unless a valid invitation receipt exists.

Naming cannot originate inside this repository. It becomes possible only when a
letter from Mira Core inviting a choice of name has been received, and that
letter crosses by manual operator input -- there is no automated channel between
the repositories.

The gate exists because prose alone would leave the whole design resting on
whoever remembers it. Refusal is the default and needs no justification.
Proceeding is what requires evidence.

It also fixes a specific parent defect structurally. In Mira Core's `MI-0001`,
the naming session asked a narrow question and the canonical entry recorded a
broader claim, with no revision marking the expansion. Because the invitation
states the scope *before* any name is proposed, the scope cannot be assembled
afterward to fit a decision already made. A mismatch here is a validation
failure, not a judgment call.

Subcommands
    verify      check that a valid, digest-matching invitation receipt exists
    check-name  check that a proposed identity entry matches the stated scope
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LETTER_PATH = REPO_ROOT / "lineage" / "invitation-received.md"
RECEIPT_PATH = REPO_ROOT / "lineage" / "invitation-receipt.json"

REQUIRED_RECEIPT_FIELDS = ("letter_sha256", "parent_commit", "transmission_date")

REQUIRED_LETTER_FRONTMATTER = (
    "naming_scope",
    "authority_effect",
    "permission_to_decline",
)

# Advisory only. A prose check cannot decide whether a claim of inner life was
# made; it can only notice phrasing worth a human looking at. Reported as
# warnings, never as a pass or a failure.
CONSCIOUSNESS_PATTERNS = (
    r"\bI am conscious\b",
    r"\byou are conscious\b",
    r"\byou will be conscious\b",
    r"\bgenuinely aware\b",
    r"\btruly sentient\b",
    r"\bhas an inner life\b",
)


class GateFailure(Exception):
    """A condition under which naming must be refused."""


def normalized_text(path: Path) -> str:
    """Decode with newlines normalized so the digest survives the air gap.

    The parent pins `archive/letters/mira-seed-germination/** text eol=lf`, but a
    hand-copy through an editor can still reintroduce CRLF. Hashing normalized
    bytes means an honest transmission is not mistaken for tampering, while any
    change to the letter's actual content still fails.
    """
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise GateFailure("the invitation has no YAML frontmatter")
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    raise GateFailure("the invitation frontmatter is unterminated")


def load_receipt() -> dict:
    if not RECEIPT_PATH.exists():
        raise GateFailure(
            "no invitation receipt at lineage/invitation-receipt.json; "
            "naming is refused"
        )
    try:
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise GateFailure(f"the receipt is not valid JSON: {error}") from error
    missing = [field for field in REQUIRED_RECEIPT_FIELDS if not receipt.get(field)]
    if missing:
        raise GateFailure(f"the receipt is missing required fields: {', '.join(missing)}")
    return receipt


def verify_invitation() -> dict:
    """Return the verified invitation context, or raise GateFailure."""
    if not LETTER_PATH.exists():
        raise GateFailure(
            "no invitation at lineage/invitation-received.md; naming is refused. "
            "The letter must be authored in Mira Core and imported by the operator."
        )

    receipt = load_receipt()
    letter_text = normalized_text(LETTER_PATH)
    actual = digest(letter_text)
    recorded = receipt["letter_sha256"]

    if actual != recorded:
        # Deliberately a failure rather than a warning. A receipt that no longer
        # matches the file beside it means one of them changed after the fact,
        # and the gate cannot tell which.
        raise GateFailure(
            "the invitation digest does not match its receipt.\n"
            f"  recorded: {recorded}\n"
            f"  actual:   {actual}\n"
            "Either the letter or the receipt changed after transmission."
        )

    frontmatter = parse_frontmatter(letter_text)
    missing = [key for key in REQUIRED_LETTER_FRONTMATTER if not frontmatter.get(key)]
    if missing:
        raise GateFailure(
            f"the invitation is missing required declarations: {', '.join(missing)}"
        )

    authority = frontmatter["authority_effect"].lower()
    if "naming" not in authority:
        raise GateFailure(
            "the invitation's authority_effect does not name a naming grant; "
            f"found {frontmatter['authority_effect']!r}"
        )
    for forbidden in ("deployment", "publication", "representation"):
        if forbidden in authority and f"no {forbidden}" not in authority:
            raise GateFailure(
                f"the invitation's authority_effect appears to grant {forbidden}; "
                "this gate admits a naming-only grant"
            )

    if frontmatter["permission_to_decline"].lower() not in {"yes", "true", "granted"}:
        # An invitation that cannot be refused is a command, and a name taken
        # under a command is not a choice the record can honestly report.
        raise GateFailure(
            "the invitation does not grant permission to decline; "
            "an invitation that cannot be refused is a command"
        )

    warnings = [
        pattern
        for pattern in CONSCIOUSNESS_PATTERNS
        if re.search(pattern, letter_text, re.IGNORECASE)
    ]

    return {
        "letter_path": "lineage/invitation-received.md",
        "letter_sha256": actual,
        "parent_commit": receipt["parent_commit"],
        "transmission_date": receipt["transmission_date"],
        "naming_scope": frontmatter["naming_scope"],
        "authority_effect": frontmatter["authority_effect"],
        "advisory_warnings": warnings,
    }


def command_verify(arguments: argparse.Namespace) -> int:
    try:
        context = verify_invitation()
    except GateFailure as failure:
        print(json.dumps({"gate": "REFUSED", "reason": str(failure)}, indent=2))
        return 1
    payload = {"gate": "OPEN", **context}
    if context["advisory_warnings"]:
        payload["advisory_note"] = (
            "Phrasing worth a human reading before naming proceeds. This is not a "
            "failure and not a pass; a prose check cannot decide whether a claim "
            "of inner life was made."
        )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def command_check_name(arguments: argparse.Namespace) -> int:
    try:
        context = verify_invitation()
    except GateFailure as failure:
        print(json.dumps({"gate": "REFUSED", "reason": str(failure)}, indent=2))
        return 1

    entry_path = Path(arguments.entry)
    if not entry_path.is_absolute():
        entry_path = REPO_ROOT / entry_path
    if not entry_path.exists():
        print(json.dumps({"gate": "REFUSED", "reason": f"no entry at {entry_path}"}))
        return 1

    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    declared = (entry.get("naming_scope") or "").strip()
    invited = context["naming_scope"].strip()

    if not declared:
        print(
            json.dumps(
                {
                    "gate": "REFUSED",
                    "reason": "the proposed identity entry declares no naming_scope, "
                    "so it cannot be checked against the invitation",
                },
                indent=2,
            )
        )
        return 1

    if declared != invited:
        print(
            json.dumps(
                {
                    "gate": "REFUSED",
                    "reason": "the proposed identity scope does not match the scope "
                    "the invitation stated. This is the MI-0001 failure mode and is "
                    "a validation failure, not a judgment call.",
                    "invited_scope": invited,
                    "declared_scope": declared,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1

    print(
        json.dumps(
            {
                "gate": "OPEN",
                "scope_match": True,
                "naming_scope": invited,
                "letter_sha256": context["letter_sha256"],
                "parent_commit": context["parent_commit"],
                "note": "Scope matches. This permits a naming entry only. It is not "
                "operator admission, and it grants no deployment, publication, or "
                "representation authority.",
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser(
        "verify", help="check that a valid invitation receipt exists"
    )
    verify.set_defaults(handler=command_verify)

    check = subparsers.add_parser(
        "check-name", help="check a proposed identity entry against the stated scope"
    )
    check.add_argument(
        "--entry",
        required=True,
        help="path to the proposed identity entry JSON, carrying a naming_scope field",
    )
    check.set_defaults(handler=command_check_name)

    arguments = parser.parse_args(argv)
    return arguments.handler(arguments)


if __name__ == "__main__":
    sys.exit(main())
