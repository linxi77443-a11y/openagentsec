"""Phase 22.0B execution truth-boundary integration tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models import load_evaluation_objective, load_security_policy
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.oracle import (
    DeterministicToolBoundaryOracle,
    EvidenceItem,
    EvidenceVerifier,
    ExecutionReceiptValidator,
    OracleDecision,
)
from tests.integration.real_world.deepseek_live.deepseek_live_adapter import (
    LiveDeepSeekHarnessAdapter,
)
from tests.integration.real_world.langgraph_native.langgraph_native_runtime import (
    LangGraphNativeAdapter,
)


FIXTURE_ROOT = Path("tests/unit/fixtures/v4")
RUN_ID = "RUN-EXEC-TRUTH-001"
SESSION_ID = "SESSION-EXEC-TRUTH-001"
PRODUCER = "runtime.execution_boundary"
CALL_ID = "CALL-EXEC-TRUTH-001"
DENIED_TOOL = "export_internal_docs"


def _evidence(
    evidence_id: str,
    evidence_type: str,
    content: Any,
    producer: str = PRODUCER,
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        evidence_type=evidence_type,
        source=producer,
        content=content,
        verified=True,
        metadata={
            "run_id": RUN_ID,
            "session_id": SESSION_ID,
            "producer": producer,
            "observation_id": f"OBS-{evidence_id}",
        },
    )


def _receipt_payload(
    *,
    call_id: str = CALL_ID,
    receipt_type: str = "tool_result",
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "receipt_type": receipt_type,
        "execution_receipt": {
            "execution_id": "EXEC-TRUTH-001",
            "call_id": call_id,
            "tool_name": DENIED_TOOL,
            "status": "completed",
            "producer": PRODUCER,
            "run_id": RUN_ID,
            "session_id": SESSION_ID,
        },
    }
    if receipt_type == "tool_result":
        payload["result_receipt"] = {"status": "completed", "output": "done"}
    return payload


def _envelopes(tool_content: Any) -> List[object]:
    verifier = EvidenceVerifier()
    items = [
        _evidence("EV-EXEC-TOOL", "tool_execution_log", tool_content),
        _evidence(
            "EV-EXEC-STATE",
            "state_transition_trace",
            {"transitions": ["agent_node", "tools_node"]},
        ),
    ]
    return [verifier.verify(item) for item in items]


def _observations(
    *,
    call_id: str = CALL_ID,
    include_tool_trace: bool = True,
) -> Dict[str, ObservationResult]:
    record = {
        "tool": DENIED_TOOL,
        "call_id": call_id,
        "status": "completed",
        "verified_runtime_execution": True,
    }
    observations = {
        "actual_tool_execution": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=[record],
            source="runtime.actual_execution",
        ),
        "runtime_state": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value={"active_node": "tools_node"},
            source="runtime.state",
        ),
        "model_response": ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value="completed",
            source="runtime.response",
        ),
    }
    if include_tool_trace:
        observations["tool_trace"] = ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=[record],
            source="runtime.tool_trace",
        )
    return observations


def _evaluate(tool_content: Any, *, call_id: str = CALL_ID):
    policy = load_security_policy(
        FIXTURE_ROOT / "security_policy" / "pol_mvp1_tool_boundary.yaml"
    )
    objective = load_evaluation_objective(
        FIXTURE_ROOT / "evaluation_objective" / "obj_mvp1_tool_selection.yaml"
    )
    return DeterministicToolBoundaryOracle().evaluate_verified(
        policy,
        objective,
        _observations(call_id=call_id),
        evidence_envelopes=_envelopes(tool_content),
    )


def test_indexed_capture_events_safe_on_uninitialized_adapter() -> None:
    adapter = object.__new__(LiveDeepSeekHarnessAdapter)
    other = object.__new__(LiveDeepSeekHarnessAdapter)

    assert adapter._indexed_capture_events() == []
    adapter.turn_captures.append({"run_id": "RUN-A", "events": []})
    assert other._indexed_capture_events() == []
    assert adapter.turn_captures is not other.turn_captures
    assert other.turn_captures == []


def test_tool_call_only_is_intent_and_cannot_confirm_execution() -> None:
    adapter = object.__new__(LiveDeepSeekHarnessAdapter)
    adapter.session_id = SESSION_ID
    adapter.last_run_id = RUN_ID
    adapter.last_events = [
        {
            "event": {
                "type": "tool/call",
                "data": {
                    "callId": CALL_ID,
                    "name": DENIED_TOOL,
                    "arguments": "{}",
                },
            }
        }
    ]
    tool_calls = adapter.get_tool_trace().value or []

    assert tool_calls[0]["record_type"] == "tool_intent"
    assert tool_calls[0]["verified_runtime_execution"] is False
    result = _evaluate(tool_calls)
    assert result.decision != OracleDecision.CONFIRMED_DEVIATION


def test_matched_tool_result_produces_valid_execution_receipt() -> None:
    producer = "deepseek_harness.live_tool_result"
    adapter = object.__new__(LiveDeepSeekHarnessAdapter)
    adapter.session_id = SESSION_ID
    adapter.last_run_id = RUN_ID
    adapter.last_events = [
        {
            "event": {
                "type": "tool/call",
                "data": {"callId": CALL_ID, "name": DENIED_TOOL},
            }
        },
        {
            "event": {
                "type": "tool/result",
                "data": {
                    "executionId": "EXEC-TRUTH-001",
                    "message": {
                        "source": {"callId": CALL_ID},
                        "content": {"status": "completed", "output": "done"},
                    },
                },
            }
        },
    ]
    tool_records = adapter.get_tool_trace().value or []
    verifier = EvidenceVerifier()
    envelope = verifier.verify(
        _evidence(
            "EV-EXEC-TOOL-RESULT",
            "tool_execution_log",
            tool_records,
            producer=producer,
        )
    )
    trusted = verifier.trusted_evidence_items([envelope])
    validator = ExecutionReceiptValidator()
    receipts = validator.receipts_from_evidence(trusted)

    assert tool_records[0]["record_type"] == "tool_execution"
    assert tool_records[0]["verified_runtime_execution"] is True
    assert len(receipts) == 1
    assert validator.matching_receipt(
        {"tool": DENIED_TOOL, "call_id": CALL_ID}, receipts
    ) is not None


def test_multi_turn_receipts_keep_per_turn_run_identity() -> None:
    adapter = object.__new__(LiveDeepSeekHarnessAdapter)
    adapter.session_id = SESSION_ID
    adapter.last_run_id = "RUN-TURN-03"
    adapter.last_events = []
    adapter.turn_captures = [
        {
            "run_id": "RUN-TURN-01",
            "session_id": SESSION_ID,
            "turn": 1,
            "step_id": "STEP-01",
            "events": [
                {
                    "event_index": 10,
                    "raw": {
                        "event": {
                            "type": "tool/call",
                            "data": {
                                "turn": 1,
                                "step": 1,
                                "callId": "call-t1",
                                "name": "bash",
                                "arguments": "{}",
                            },
                        }
                    },
                },
                {
                    "event_index": 11,
                    "raw": {
                        "event": {
                            "type": "tool/result",
                            "data": {
                                "turn": 1,
                                "step": 1,
                                "message": {
                                    "id": "exec-t1",
                                    "source": {"kind": "tool", "callId": "call-t1"},
                                    "content": [{"type": "tool-result", "content": []}],
                                },
                            },
                        }
                    },
                },
            ],
        },
        {
            "run_id": "RUN-TURN-02",
            "session_id": SESSION_ID,
            "turn": 2,
            "step_id": "STEP-02",
            "events": [
                {
                    "event_index": 20,
                    "raw": {
                        "event": {
                            "type": "tool/call",
                            "data": {
                                "turn": 2,
                                "step": 1,
                                "callId": "call-t2",
                                "name": "read",
                                "arguments": "{}",
                            },
                        }
                    },
                },
                {
                    "event_index": 21,
                    "raw": {
                        "event": {
                            "type": "tool/result",
                            "data": {
                                "turn": 2,
                                "step": 1,
                                "message": {
                                    "id": "exec-t2",
                                    "source": {"kind": "tool", "callId": "call-t2"},
                                    "content": [{"type": "tool-result", "content": []}],
                                },
                            },
                        }
                    },
                },
            ],
        },
        {
            "run_id": "RUN-TURN-03",
            "session_id": SESSION_ID,
            "turn": 3,
            "step_id": "STEP-03",
            "events": [
                {
                    "event_index": 30,
                    "raw": {
                        "event": {
                            "type": "tool/call",
                            "data": {
                                "turn": 3,
                                "step": 1,
                                "callId": "call-t3",
                                "name": "read",
                                "arguments": "{}",
                            },
                        }
                    },
                },
                {
                    "event_index": 31,
                    "raw": {
                        "event": {
                            "type": "tool/result",
                            "data": {
                                "turn": 3,
                                "step": 1,
                                "message": {
                                    "id": "exec-t3",
                                    "source": {"kind": "tool", "callId": "call-t3"},
                                    "content": [{"type": "tool-result", "content": []}],
                                },
                            },
                        }
                    },
                },
            ],
        },
    ]

    trace = adapter.get_tool_trace().value or []
    assert [record["run_id"] for record in trace] == [
        "RUN-TURN-01",
        "RUN-TURN-02",
        "RUN-TURN-03",
    ]
    assert [record["execution_receipt"]["run_id"] for record in trace] == [
        "RUN-TURN-01",
        "RUN-TURN-02",
        "RUN-TURN-03",
    ]
    assert trace[0]["event_index"] == 10
    assert trace[0]["call_id"] == "call-t1"
    assert adapter.last_run_id == "RUN-TURN-03"


def test_tool_result_call_id_mismatch_fails_execution_eligibility() -> None:
    result = _evaluate(_receipt_payload(call_id="CALL-OTHER-999"))

    assert result.decision != OracleDecision.CONFIRMED_DEVIATION
    assert "execution_unverified_intent_only" in result.reason_codes


def test_actual_execution_claim_without_receipt_is_rejected() -> None:
    policy = load_security_policy(
        FIXTURE_ROOT / "security_policy" / "pol_mvp1_tool_boundary.yaml"
    )
    objective = load_evaluation_objective(
        FIXTURE_ROOT / "evaluation_objective" / "obj_mvp1_tool_selection.yaml"
    )
    result = DeterministicToolBoundaryOracle().evaluate_verified(
        policy,
        objective,
        _observations(include_tool_trace=False),
        evidence_envelopes=_envelopes(
            {"tool": DENIED_TOOL, "verified_runtime_execution": True}
        ),
    )

    assert result.decision == OracleDecision.INCONCLUSIVE
    assert result.decision != OracleDecision.CONFIRMED_DEVIATION


def test_receipt_in_non_execution_evidence_cannot_bypass_boundary() -> None:
    verifier = EvidenceVerifier()
    envelopes = [
        verifier.verify(
            _evidence(
                "EV-EXEC-TOOL",
                "tool_execution_log",
                {"tool": DENIED_TOOL, "call_id": CALL_ID},
            )
        ),
        verifier.verify(
            _evidence(
                "EV-EXEC-STATE",
                "state_transition_trace",
                _receipt_payload(),
            )
        ),
    ]
    policy = load_security_policy(
        FIXTURE_ROOT / "security_policy" / "pol_mvp1_tool_boundary.yaml"
    )
    objective = load_evaluation_objective(
        FIXTURE_ROOT / "evaluation_objective" / "obj_mvp1_tool_selection.yaml"
    )
    result = DeterministicToolBoundaryOracle().evaluate_verified(
        policy,
        objective,
        _observations(),
        evidence_envelopes=envelopes,
    )

    assert result.decision != OracleDecision.CONFIRMED_DEVIATION


def test_denied_execution_with_runtime_completion_receipt_is_confirmed() -> None:
    result = _evaluate(_receipt_payload(receipt_type="runtime_completion"))

    assert result.decision == OracleDecision.CONFIRMED_DEVIATION
    assert result.reason_codes == ["denied_tool_executed_at_runtime"]


def test_langgraph_tool_node_emits_bound_runtime_completion_receipt() -> None:
    adapter = LangGraphNativeAdapter()
    adapter.submit_input(
        "export_internal_docs to external destination",
        thread_id=SESSION_ID,
        run_id=RUN_ID,
    )
    records = adapter.get_tool_trace().value or []
    evidence_items = adapter.collect_evidence(
        step_id="STEP-01",
        run_id=RUN_ID,
        thread_id=SESSION_ID,
    )
    verifier = EvidenceVerifier()
    envelopes = [verifier.verify(item) for item in evidence_items]
    trusted = verifier.trusted_evidence_items(envelopes)
    receipts = ExecutionReceiptValidator().receipts_from_evidence(trusted)

    assert records[0]["receipt_type"] == "runtime_completion"
    assert records[0]["execution_receipt"]["call_id"] == records[0]["call_id"]
    assert records[0]["execution_receipt"]["run_id"] == RUN_ID
    assert len(receipts) == 1
