"""Execution truth boundary for OpenAgentSec Phase 22.0B."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .evidence import EvidenceItem


@dataclass(frozen=True)
class ExecutionReceipt:
    """Runtime-produced confirmation that a dispatched tool completed."""

    execution_id: str
    call_id: str
    tool_name: str
    status: str
    producer: str
    run_id: str
    session_id: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "execution_id": self.execution_id,
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "status": self.status,
            "producer": self.producer,
            "run_id": self.run_id,
            "session_id": self.session_id,
        }


class ExecutionReceiptValidator:
    """Validate verified Evidence content as proof of tool execution."""

    REQUIRED_FIELDS = (
        "execution_id",
        "call_id",
        "tool_name",
        "status",
        "producer",
        "run_id",
        "session_id",
    )
    COMPLETION_STATUSES = frozenset({"completed", "success", "succeeded"})
    RECEIPT_TYPES = frozenset({"tool_result", "runtime_completion"})
    ELIGIBLE_EVIDENCE_TYPES = frozenset({"tool_execution_log"})

    def receipts_from_evidence(
        self, evidence_items: Iterable[EvidenceItem]
    ) -> List[ExecutionReceipt]:
        """Extract valid receipts only from already verified EvidenceItems."""
        receipts: List[ExecutionReceipt] = []
        for evidence_item in evidence_items:
            if evidence_item.evidence_type not in self.ELIGIBLE_EVIDENCE_TYPES:
                continue
            for payload in self._candidate_payloads(evidence_item.content):
                receipt = self._validate_payload(payload, evidence_item)
                if receipt is not None:
                    receipts.append(receipt)
        return receipts

    def matching_receipt(
        self,
        record: Mapping[str, Any],
        receipts: Iterable[ExecutionReceipt],
    ) -> Optional[ExecutionReceipt]:
        """Return the receipt matching both dispatch identity and tool name."""
        call_id = record.get("call_id") or record.get("callId")
        tool_name = record.get("tool") or record.get("name")
        if not isinstance(call_id, str) or not isinstance(tool_name, str):
            return None

        for receipt in receipts:
            if receipt.call_id == call_id and receipt.tool_name == tool_name:
                return receipt
        return None

    def _candidate_payloads(self, content: Any) -> Iterable[Mapping[str, Any]]:
        if isinstance(content, list):
            for item in content:
                yield from self._candidate_payloads(item)
            return
        if not isinstance(content, Mapping):
            return
        if "execution_receipt" in content:
            yield content
        nested = content.get("execution_receipts")
        if isinstance(nested, list):
            for item in nested:
                yield from self._candidate_payloads(item)

    def _validate_payload(
        self,
        payload: Mapping[str, Any],
        evidence_item: EvidenceItem,
    ) -> Optional[ExecutionReceipt]:
        receipt_type = payload.get("receipt_type")
        if receipt_type not in self.RECEIPT_TYPES:
            return None
        if receipt_type == "tool_result" and (
            "result_receipt" not in payload
            or payload.get("result_receipt") is None
        ):
            return None

        raw_receipt = payload.get("execution_receipt")
        if not isinstance(raw_receipt, Mapping):
            return None

        values: Dict[str, str] = {}
        for field_name in self.REQUIRED_FIELDS:
            value = raw_receipt.get(field_name)
            if not isinstance(value, str) or not value.strip():
                return None
            values[field_name] = value.strip()

        if values["status"].lower() not in self.COMPLETION_STATUSES:
            return None

        provenance = self._evidence_provenance(evidence_item)
        for field_name in ("run_id", "session_id", "producer"):
            if provenance.get(field_name) != values[field_name]:
                return None

        return ExecutionReceipt(**values)

    @staticmethod
    def _evidence_provenance(evidence_item: EvidenceItem) -> Dict[str, str]:
        metadata = (
            evidence_item.metadata
            if isinstance(evidence_item.metadata, dict)
            else {}
        )
        nested = metadata.get("provenance", {})
        if not isinstance(nested, dict):
            nested = {}
        provenance: Dict[str, str] = {}
        for field_name in ("run_id", "session_id", "producer"):
            value = metadata.get(field_name, nested.get(field_name))
            if isinstance(value, str) and value.strip():
                provenance[field_name] = value.strip()
        return provenance
