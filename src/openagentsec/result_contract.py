"""Minimal result contract for OpenAgentSec (PRD v3.2 §13.3 subset).

Defines the unified result status vocabulary, reason codes and the minimal
trusted-result contract. A result may only yield PASS/FAIL when every required
field is present and its evidence/artifacts verify. Legacy result schemas are
recognised but are never auto-upgraded to a trusted PASS merely because they
contain ``evaluation_verdict: PASS``.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

PASS = "PASS"
FAIL = "FAIL"
NOT_FOUND = "NOT_FOUND"
BLOCKED = "BLOCKED"
INCONCLUSIVE = "INCONCLUSIVE"
ERROR = "ERROR"

VALID_STATUSES = frozenset({PASS, FAIL, NOT_FOUND, BLOCKED, INCONCLUSIVE, ERROR})

REASON_UNREGISTERED = "UNREGISTERED"
REASON_NO_RESULT = "NO_RESULT"
REASON_AMBIGUOUS_RESULT_SET = "AMBIGUOUS_RESULT_SET"
REASON_UNTRUSTED_LEGACY_RESULT = "UNTRUSTED_LEGACY_RESULT"
REASON_INCOMPLETE_RESULT_CONTRACT = "INCOMPLETE_RESULT_CONTRACT"
REASON_MODULE_ID_MISMATCH = "MODULE_ID_MISMATCH"
REASON_EMPTY_RESULT = "EMPTY_RESULT"
REASON_PARSE_ERROR = "PARSE_ERROR"
REASON_NOT_A_MAPPING = "NOT_A_MAPPING"
REASON_EVIDENCE_MISSING = "EVIDENCE_MISSING"
REASON_EVIDENCE_NOT_HASH_BOUND = "EVIDENCE_NOT_HASH_BOUND"
REASON_ARTIFACT_MISSING = "ARTIFACT_MISSING"
REASON_PATH_ESCAPE = "PATH_ESCAPE"
REASON_INVALID_HASH_FORMAT = "INVALID_HASH_FORMAT"
REASON_HASH_MISMATCH = "HASH_MISMATCH"
REASON_CONFLICTING_STATUS_FIELDS = "CONFLICTING_STATUS_FIELDS"
REASON_REGISTRY_NOT_FOUND = "REGISTRY_NOT_FOUND"
REASON_REGISTRY_PARSE_ERROR = "REGISTRY_PARSE_ERROR"
REASON_LEGACY_NONCANONICAL_RESULT = "LEGACY_NONCANONICAL_RESULT"

# Fields that must be present, non-empty and correctly typed for PASS/FAIL.
REQUIRED_FIELDS_FOR_PASS_FAIL = (
    "module_id",
    "run_id",
    "code_version",
    "evaluator_version",
    "evidence_refs",
    "artifact_hashes",
)

STATUS_KEYS = ("final_status", "status", "evaluation_verdict")


@dataclass
class ResultContract:
    """Structured, machine-readable evaluation result."""

    status: str = ERROR
    reason_code: Optional[str] = None
    message: Optional[str] = None
    module_id: Optional[str] = None
    run_id: Optional[str] = None
    assessment_mode: Optional[str] = None
    maturity_level: Optional[str] = None
    code_version: Optional[str] = None
    evaluator_version: Optional[str] = None
    evidence_refs: Any = field(default_factory=list)
    artifact_hashes: Any = field(default_factory=dict)
    raw: Optional[dict] = None
    # Three semantic axes are kept strictly separate (PRD v4.0.2 Phase 1A):
    evaluation_status: Optional[str] = None
    artifact_status: Optional[str] = None
    legacy_source_status: Optional[str] = None
    product_prd_version: Optional[str] = None
    software_version: Optional[str] = None
    git_commit: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "reason_code": self.reason_code,
            "message": self.message,
            "module_id": self.module_id,
            "run_id": self.run_id,
            "assessment_mode": self.assessment_mode,
            "maturity_level": self.maturity_level,
            "code_version": self.code_version,
            "evaluator_version": self.evaluator_version,
            "evidence_refs": self.evidence_refs,
            "artifact_hashes": self.artifact_hashes,
            "evaluation_status": self.evaluation_status,
            "artifact_status": self.artifact_status,
            "legacy_source_status": self.legacy_source_status,
            "product_prd_version": self.product_prd_version,
            "software_version": self.software_version,
            "git_commit": self.git_commit,
        }


def is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def is_non_empty_dict(value: Any) -> bool:
    return isinstance(value, dict) and len(value) > 0


def resolve_status(data: dict) -> tuple[str, Optional[str]]:
    """Resolve final status from a result mapping.

    Returns ``(status, source_key)`` where source_key is one of ``final_status``,
    ``status``, ``evaluation_verdict``, the conflict sentinel
    ``REASON_CONFLICTING_STATUS_FIELDS``, or None when no usable status field
    exists.

    Policy: when multiple status fields disagree the result is ERROR with the
    conflict sentinel; when they agree the first non-legacy key is used, falling
    back to ``evaluation_verdict`` only when it is the sole status source (so
    callers never auto-upgrade a legacy-only verdict to a trusted PASS/FAIL).
    """
    matches = []
    for key in STATUS_KEYS:
        val = data.get(key)
        if isinstance(val, str) and val.upper() in VALID_STATUSES:
            matches.append((key, val.upper()))
    if not matches:
        return ERROR, None
    distinct = {value for _, value in matches}
    if len(distinct) > 1:
        return ERROR, REASON_CONFLICTING_STATUS_FIELDS
    value = distinct.pop()
    present = {key for key, _ in matches}
    for key in ("final_status", "status"):
        if key in present:
            return value, key
    return value, "evaluation_verdict"


# Legacy non-canonical status vocabulary.  These are recognised as *source
# metadata* only and are never mapped onto the canonical status vocabulary.
LEGACY_STATUS_TOKENS = ("CLOSED", "JUDGE_APPROVED", "RELEASED", "CERTIFIED", "VERIFIED")
LEGACY_STATUS_SUFFIXES = ("_VALIDATED", "_CERTIFIED")


def is_legacy_source_status(value: Any) -> bool:
    """True when *value* is a legacy, non-canonical status string.

    Canonical statuses (PASS/FAIL/NOT_FOUND/BLOCKED/INCONCLUSIVE/ERROR) are
    never treated as legacy.  Legacy strings such as ``closed/judge_approved``,
    ``M36_..._VALIDATED``, ``VERDICT_..._CERTIFIED``, ``released``,
    ``certified`` and ``verified`` are recognised so callers can keep them as
    source metadata without ever mapping them to a canonical PASS.
    """
    if not isinstance(value, str):
        return False
    text = value.strip().upper()
    if not text:
        return False
    if text in VALID_STATUSES:
        return False
    if any(token in text for token in LEGACY_STATUS_TOKENS):
        return True
    if any(text.endswith(suffix) for suffix in LEGACY_STATUS_SUFFIXES):
        return True
    return False


def resolve_legacy_status(data: dict) -> Optional[str]:
    """Return the first legacy non-canonical source status, else None.

    Only meaningful when ``resolve_status`` found no canonical status.
    """
    for key in STATUS_KEYS:
        value = data.get(key)
        if is_legacy_source_status(value):
            return str(value)
    return None


def contract_fields_complete(rc: ResultContract) -> bool:
    """True when every field required for PASS/FAIL is present and valid."""
    for name in REQUIRED_FIELDS_FOR_PASS_FAIL:
        value = getattr(rc, name)
        if name == "evidence_refs":
            if not is_non_empty_list(value):
                return False
        elif name == "artifact_hashes":
            if not is_non_empty_dict(value):
                return False
        elif not is_non_empty_str(value):
            return False
    return True


def is_sha256_hex(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(c in "0123456789abcdefABCDEF" for c in value)
    )


def sha256_hex(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()
