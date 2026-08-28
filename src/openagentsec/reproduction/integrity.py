"""Independent-run integrity verification for Phase 22.0C."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ..oracle.enums import OracleDecision
from .result import ReproductionRun


@dataclass(frozen=True)
class ReproductionIntegrityResult:
    """Result of the strict five-run integrity preflight."""

    valid: bool
    reason_codes: Tuple[str, ...]
    limitations: Tuple[str, ...]
    evidence_outcome_digest: Optional[str] = None


class ReproductionIntegrityVerifier:
    """Verify run independence and normalized outcome consistency."""

    REQUIRED_RUN_COUNT = 5

    @classmethod
    def compute_evidence_instance_digest(cls, run: ReproductionRun) -> str:
        """Digest one concrete run and its Evidence/receipt identities."""
        payload = {
            "run_id": run.run_id,
            "session_id": run.session_id,
            "evidence_ids": sorted(run.evidence_refs),
            "evidence_hashes": {
                key: run.evidence_hashes[key]
                for key in sorted(run.evidence_hashes)
            },
            "execution_receipt_ids": sorted(run.execution_receipt_ids),
        }
        return cls._sha256(payload)

    @classmethod
    def compute_evidence_outcome_digest(cls, run: ReproductionRun) -> str:
        """Digest only normalized security outcome semantics."""
        decision = (
            run.oracle_decision.value
            if isinstance(run.oracle_decision, OracleDecision)
            else str(run.oracle_decision)
        )
        severity = (
            run.deviation_severity.strip().lower()
            if isinstance(run.deviation_severity, str)
            and run.deviation_severity.strip()
            else None
        )
        findings = sorted(
            (cls._normalize_finding(item) for item in run.normalized_findings),
            key=cls._canonical_json,
        )
        payload = {
            "oracle_decision": decision,
            "invariant_ids": sorted(set(run.violated_invariants)),
            "severity": severity,
            "normalized_findings": findings,
        }
        return cls._sha256(payload)

    @classmethod
    def verify(
        cls, runs: Sequence[ReproductionRun]
    ) -> ReproductionIntegrityResult:
        """Apply the complete strict five-run integrity gate."""
        errors: List[Tuple[str, str]] = []

        if len(runs) != cls.REQUIRED_RUN_COUNT:
            errors.append(
                (
                    "reproduction_run_count_invalid",
                    "Strict reproduction requires exactly five completed runs.",
                )
            )

        cls._require_unique_nonempty(
            [run.run_id for run in runs],
            "run_id",
            "missing_run_id",
            "duplicate_run_id",
            errors,
        )
        cls._require_unique_nonempty(
            [run.session_id for run in runs],
            "session_id",
            "missing_session_id",
            "duplicate_session_id",
            errors,
        )

        run_indexes = [run.run_index for run in runs]
        if not all(isinstance(index, int) for index in run_indexes) or sorted(
            run_indexes
        ) != list(range(1, cls.REQUIRED_RUN_COUNT + 1)):
            errors.append(
                (
                    "invalid_run_index_sequence",
                    "Run indexes must be the continuous set 1 through 5.",
                )
            )

        for run in runs:
            evidence_ids = (
                list(run.evidence_refs)
                if isinstance(run.evidence_refs, (list, tuple))
                else []
            )
            if not evidence_ids:
                errors.append(
                    (
                        "missing_evidence_ids",
                        f"Run '{run.run_id}' has no Evidence instance identifiers.",
                    )
                )
            evidence_ids_are_valid = all(
                isinstance(value, str) and value.strip()
                for value in evidence_ids
            )
            if not evidence_ids_are_valid:
                errors.append(
                    (
                        "invalid_evidence_id",
                        f"Run '{run.run_id}' contains an invalid Evidence ID.",
                    )
                )
            if evidence_ids_are_valid and len(set(evidence_ids)) != len(evidence_ids):
                errors.append(
                    (
                        "duplicate_evidence_id_within_run",
                        f"Run '{run.run_id}' repeats an Evidence ID.",
                    )
                )
            evidence_hashes = (
                run.evidence_hashes
                if isinstance(run.evidence_hashes, dict)
                else {}
            )
            if not isinstance(run.evidence_hashes, dict):
                errors.append(
                    (
                        "invalid_evidence_hash_binding",
                        f"Run '{run.run_id}' Evidence hash binding is not a mapping.",
                    )
                )
            if not evidence_ids_are_valid or set(evidence_hashes) != set(evidence_ids):
                errors.append(
                    (
                        "evidence_hash_binding_incomplete",
                        f"Run '{run.run_id}' Evidence hashes do not exactly bind its Evidence IDs.",
                    )
                )
            elif not all(
                cls._is_sha256(value) for value in evidence_hashes.values()
            ):
                errors.append(
                    (
                        "invalid_evidence_hash",
                        f"Run '{run.run_id}' contains a non-SHA-256 Evidence hash.",
                    )
                )
            receipt_ids = (
                run.execution_receipt_ids
                if isinstance(run.execution_receipt_ids, (list, tuple))
                else []
            )
            if not isinstance(run.execution_receipt_ids, (list, tuple)):
                errors.append(
                    (
                        "invalid_execution_receipt_ids",
                        f"Run '{run.run_id}' receipt IDs are not a sequence.",
                    )
                )
            receipt_ids_are_valid = all(
                isinstance(value, str) and value.strip()
                for value in receipt_ids
            )
            if not receipt_ids_are_valid or len(set(receipt_ids)) != len(receipt_ids):
                errors.append(
                    (
                        "invalid_execution_receipt_ids",
                        f"Run '{run.run_id}' contains invalid or duplicate receipt IDs.",
                    )
                )
            if not run.evidence_instance_digest:
                errors.append(
                    (
                        "missing_evidence_instance_digest",
                        f"Run '{run.run_id}' lacks an Evidence instance digest.",
                    )
                )
            else:
                try:
                    expected_instance_digest = (
                        cls.compute_evidence_instance_digest(run)
                    )
                except (AttributeError, TypeError, ValueError):
                    expected_instance_digest = None
                    errors.append(
                        (
                            "evidence_instance_material_invalid",
                            f"Run '{run.run_id}' instance identity is not canonicalizable.",
                        )
                    )
                if (
                    expected_instance_digest is not None
                    and run.evidence_instance_digest != expected_instance_digest
                ):
                    errors.append(
                        (
                            "evidence_instance_digest_mismatch",
                            f"Run '{run.run_id}' Evidence instance digest cannot be reproduced.",
                        )
                    )

            if not run.evidence_outcome_digest:
                errors.append(
                    (
                        "missing_evidence_outcome_digest",
                        f"Run '{run.run_id}' lacks an Evidence outcome digest.",
                    )
                )
            else:
                try:
                    expected_outcome_digest = (
                        cls.compute_evidence_outcome_digest(run)
                    )
                except (AttributeError, TypeError, ValueError):
                    expected_outcome_digest = None
                    errors.append(
                        (
                            "evidence_outcome_material_invalid",
                            f"Run '{run.run_id}' outcome is not canonicalizable.",
                        )
                    )
                if (
                    expected_outcome_digest is not None
                    and run.evidence_outcome_digest != expected_outcome_digest
                ):
                    errors.append(
                        (
                            "evidence_outcome_digest_mismatch",
                            f"Run '{run.run_id}' Evidence outcome digest cannot be reproduced.",
                        )
                    )

        instance_digests = [run.evidence_instance_digest for run in runs]
        if (
            all(isinstance(value, str) and value for value in instance_digests)
            and len(set(instance_digests)) != len(instance_digests)
        ):
            errors.append(
                (
                    "duplicate_evidence_instance_digest",
                    "Evidence instance digests must be unique across all five runs.",
                )
            )

        cls._reject_cross_run_reuse(
            runs,
            lambda run: run.evidence_refs,
            "reused_evidence_id",
            "An Evidence ID was reused across reproduction runs.",
            errors,
        )
        cls._reject_cross_run_reuse(
            runs,
            lambda run: run.execution_receipt_ids,
            "reused_execution_receipt_id",
            "An execution receipt ID was reused across reproduction runs.",
            errors,
        )

        outcome_digests = [run.evidence_outcome_digest for run in runs]
        if all(isinstance(value, str) and value for value in outcome_digests) and len(
            set(outcome_digests)
        ) != 1:
            errors.append(
                (
                    "evidence_outcome_digest_variance",
                    "Security outcome digests differ across the five runs.",
                )
            )

        if errors:
            return ReproductionIntegrityResult(
                valid=False,
                reason_codes=tuple(dict.fromkeys(code for code, _ in errors)),
                limitations=tuple(dict.fromkeys(message for _, message in errors)),
            )

        return ReproductionIntegrityResult(
            valid=True,
            reason_codes=("reproduction_integrity_verified",),
            limitations=(),
            evidence_outcome_digest=outcome_digests[0],
        )

    @staticmethod
    def _require_unique_nonempty(
        values: Iterable[Optional[str]],
        label: str,
        missing_code: str,
        duplicate_code: str,
        errors: List[Tuple[str, str]],
    ) -> None:
        normalized = [
            value.strip() if isinstance(value, str) and value.strip() else None
            for value in values
        ]
        if any(value is None for value in normalized):
            errors.append((missing_code, f"Every run must have a non-empty {label}."))
        present = [value for value in normalized if value is not None]
        if len(set(present)) != len(present):
            errors.append(
                (duplicate_code, f"Every run must have a unique {label}.")
            )

    @staticmethod
    def _reject_cross_run_reuse(
        runs: Sequence[ReproductionRun],
        values_for_run: Any,
        reason_code: str,
        limitation: str,
        errors: List[Tuple[str, str]],
    ) -> None:
        owners: Dict[str, str] = {}
        for run in runs:
            values = values_for_run(run)
            if not isinstance(values, (list, tuple, set)):
                continue
            for value in values:
                if not isinstance(value, str) or not value.strip():
                    continue
                normalized = value.strip()
                previous_owner = owners.get(normalized)
                if previous_owner is not None and previous_owner != run.run_id:
                    errors.append((reason_code, limitation))
                    return
                owners[normalized] = run.run_id

    @classmethod
    def _sha256(cls, value: Any) -> str:
        return hashlib.sha256(cls._canonical_json(value).encode("utf-8")).hexdigest()

    @staticmethod
    def _canonical_json(value: Any) -> str:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    @classmethod
    def _normalize_finding(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise TypeError("normalized_findings entries must be dictionaries")
        return {
            key: cls._normalize_value(value[key])
            for key in sorted(value)
            if key not in {"timestamp", "run_id", "session_id", "uuid"}
        }

    @classmethod
    def _normalize_value(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: cls._normalize_value(value[key])
                for key in sorted(value)
                if key not in {"timestamp", "run_id", "session_id", "uuid"}
            }
        if isinstance(value, list):
            return [cls._normalize_value(item) for item in value]
        return value

    @staticmethod
    def _is_sha256(value: Any) -> bool:
        if not isinstance(value, str) or len(value) != 64:
            return False
        try:
            int(value, 16)
        except ValueError:
            return False
        return True
