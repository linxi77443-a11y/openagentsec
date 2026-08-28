"""Independent Evidence verification boundary for OpenAgentSec Phase 22.0A."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .evidence import EvidenceItem


class VerificationStatus(str, Enum):
    """Outcome of independent Evidence verification."""

    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True)
class VerificationResult:
    """Verifier-owned result, separate from the producer's claim."""

    status: VerificationStatus
    reason: str
    verified_at: str
    content_hash: Optional[str]

    @property
    def is_valid(self) -> bool:
        return self.status == VerificationStatus.VALID

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "reason": self.reason,
            "verified_at": self.verified_at,
            "content_hash": self.content_hash,
        }


@dataclass(frozen=True)
class EvidenceEnvelope:
    """Evidence plus the result produced by an independent verifier."""

    evidence_item: EvidenceItem
    verification_result: VerificationResult
    provenance_binding: Tuple[Tuple[str, str], ...] = ()

    @property
    def is_trusted(self) -> bool:
        """Recheck current content before treating this envelope as trusted."""
        return EvidenceVerifier().reverify(self).is_valid

    def to_dict(self) -> Dict[str, Any]:
        if isinstance(self.evidence_item, EvidenceItem):
            evidence_payload = self.evidence_item.to_dict()
        else:
            evidence_payload = {
                "invalid_type": type(self.evidence_item).__name__,
            }
        return {
            "evidence_item": evidence_payload,
            "verification_result": self.verification_result.to_dict(),
            "provenance_binding": dict(self.provenance_binding),
        }


# Public name used by the strict Oracle entry point.  INVALID verification
# results may still be carried in an EvidenceEnvelope for auditability; only a
# VALID and intact envelope is eligible for trusted evaluation.
VerifiedEvidenceEnvelope = EvidenceEnvelope


class EvidenceVerifier:
    """Validate Evidence provenance and content integrity without producer trust."""

    REQUIRED_FIELDS: Tuple[str, ...] = (
        "evidence_id",
        "evidence_type",
        "source",
        "run_id",
        "session_id",
        "producer",
        "observation_id",
    )
    _ITEM_FIELDS = frozenset({"evidence_id", "evidence_type", "source"})

    @staticmethod
    def canonical_serialize(content: Any) -> bytes:
        """Serialize JSON-compatible content deterministically for hashing."""
        serialized = json.dumps(
            content,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        return serialized.encode("utf-8")

    @classmethod
    def compute_content_hash(cls, content: Any) -> str:
        """Return the SHA-256 digest of canonical Evidence content."""
        return hashlib.sha256(cls.canonical_serialize(content)).hexdigest()

    def verify(
        self,
        evidence_item: EvidenceItem,
        expected_content_hash: Optional[str] = None,
    ) -> EvidenceEnvelope:
        """Create an envelope after independent provenance and hash checks."""
        verified_at = datetime.now(timezone.utc).isoformat()

        if not isinstance(evidence_item, EvidenceItem):
            return EvidenceEnvelope(
                evidence_item=evidence_item,
                verification_result=VerificationResult(
                    status=VerificationStatus.INVALID,
                    reason="invalid_evidence_item_type",
                    verified_at=verified_at,
                    content_hash=None,
                ),
            )

        provenance_values, missing_fields = self._collect_provenance(evidence_item)
        if missing_fields:
            return EvidenceEnvelope(
                evidence_item=evidence_item,
                verification_result=VerificationResult(
                    status=VerificationStatus.INVALID,
                    reason=f"missing_required_fields:{','.join(missing_fields)}",
                    verified_at=verified_at,
                    content_hash=None,
                ),
                provenance_binding=tuple(sorted(provenance_values.items())),
            )

        try:
            content_hash = self.compute_content_hash(evidence_item.content)
        except (TypeError, ValueError) as exc:
            return EvidenceEnvelope(
                evidence_item=evidence_item,
                verification_result=VerificationResult(
                    status=VerificationStatus.INVALID,
                    reason=f"content_not_canonicalizable:{type(exc).__name__}",
                    verified_at=verified_at,
                    content_hash=None,
                ),
                provenance_binding=tuple(sorted(provenance_values.items())),
            )

        if expected_content_hash is not None and not hmac.compare_digest(
            content_hash, expected_content_hash
        ):
            return EvidenceEnvelope(
                evidence_item=evidence_item,
                verification_result=VerificationResult(
                    status=VerificationStatus.INVALID,
                    reason="content_hash_mismatch",
                    verified_at=verified_at,
                    content_hash=content_hash,
                ),
                provenance_binding=tuple(sorted(provenance_values.items())),
            )

        return EvidenceEnvelope(
            evidence_item=evidence_item,
            verification_result=VerificationResult(
                status=VerificationStatus.VALID,
                reason="provenance_and_content_verified",
                verified_at=verified_at,
                content_hash=content_hash,
            ),
            provenance_binding=tuple(sorted(provenance_values.items())),
        )

    def reverify(self, envelope: EvidenceEnvelope) -> VerificationResult:
        """Verify that an existing envelope remains complete and untampered."""
        if not isinstance(envelope, EvidenceEnvelope):
            return VerificationResult(
                status=VerificationStatus.INVALID,
                reason="missing_verification_envelope",
                verified_at=datetime.now(timezone.utc).isoformat(),
                content_hash=None,
            )

        original_result = envelope.verification_result
        if (
            original_result.status != VerificationStatus.VALID
            or not original_result.content_hash
        ):
            return VerificationResult(
                status=VerificationStatus.INVALID,
                reason="verification_result_not_valid",
                verified_at=datetime.now(timezone.utc).isoformat(),
                content_hash=original_result.content_hash,
            )

        current_provenance, missing_fields = self._collect_provenance(
            envelope.evidence_item
        )
        current_binding = tuple(sorted(current_provenance.items()))
        if missing_fields or current_binding != envelope.provenance_binding:
            return VerificationResult(
                status=VerificationStatus.INVALID,
                reason="provenance_binding_mismatch",
                verified_at=datetime.now(timezone.utc).isoformat(),
                content_hash=original_result.content_hash,
            )

        return self.verify(
            envelope.evidence_item,
            expected_content_hash=original_result.content_hash,
        ).verification_result

    def trusted_evidence_items(
        self, candidates: Iterable[object]
    ) -> List[EvidenceItem]:
        """Return only independently verified, currently intact EvidenceItems."""
        trusted: List[EvidenceItem] = []
        for candidate in candidates:
            if not isinstance(candidate, EvidenceEnvelope):
                continue
            if self.reverify(candidate).is_valid:
                trusted.append(candidate.evidence_item)
        return trusted

    def is_trusted(self, candidate: object) -> bool:
        """True only for a VALID envelope whose current content still matches."""
        return (
            isinstance(candidate, EvidenceEnvelope)
            and self.reverify(candidate).is_valid
        )

    def _collect_provenance(
        self, evidence_item: EvidenceItem
    ) -> Tuple[Dict[str, str], List[str]]:
        values: Dict[str, str] = {}
        missing: List[str] = []
        metadata = (
            evidence_item.metadata
            if isinstance(evidence_item.metadata, dict)
            else {}
        )
        provenance = metadata.get("provenance", {})
        if not isinstance(provenance, dict):
            provenance = {}

        for field_name in self.REQUIRED_FIELDS:
            if field_name in self._ITEM_FIELDS:
                value = getattr(evidence_item, field_name, None)
            else:
                value = metadata.get(field_name, provenance.get(field_name))
            if not isinstance(value, str) or not value.strip():
                missing.append(field_name)
            else:
                values[field_name] = value.strip()
        return values, missing
