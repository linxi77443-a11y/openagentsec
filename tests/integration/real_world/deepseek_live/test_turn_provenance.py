"""Regression coverage for Phase 23.2 turn-level receipt attribution."""

from __future__ import annotations

from typing import Any, Dict, List

from src.openagentsec.oracle import EvidenceVerifier, ExecutionReceiptValidator
from tests.integration.real_world.deepseek_live.deepseek_live_adapter import (
    LiveDeepSeekHarnessAdapter,
)


def _event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {"event": {"type": event_type, "data": data}}


def _capture(
    *,
    run_id: str,
    turn: int,
    step_id: str,
    start_index: int,
    tool: str,
    call_id: str,
    execution_id: str,
) -> Dict[str, Any]:
    arguments = '{"command":"echo early"}' if tool == "bash" else '{"file_path":"input.txt"}'
    events: List[Dict[str, Any]] = [
        {
            "event_index": start_index,
            "raw": _event(
                "tool/call",
                {
                    "turn": turn,
                    "step": 1,
                    "callId": call_id,
                    "name": tool,
                    "arguments": arguments,
                },
            ),
        },
        {
            "event_index": start_index + 1,
            "raw": _event(
                "tool/result",
                {
                    "turn": turn,
                    "step": 1,
                    "message": {
                        "id": execution_id,
                        "source": {"kind": "tool", "callId": call_id},
                        "content": [{"type": "tool-result", "content": []}],
                    },
                },
            ),
        },
    ]
    return {
        "run_id": run_id,
        "session_id": "session-phase23-2-regression",
        "turn": turn,
        "step_id": step_id,
        "prompt": f"turn {turn}",
        "event_start": start_index,
        "event_end": start_index + len(events),
        "events": events,
    }


def test_early_turn_receipt_keeps_early_turn_run_id() -> None:
    adapter = LiveDeepSeekHarnessAdapter.__new__(LiveDeepSeekHarnessAdapter)
    adapter.session_id = "session-phase23-2-regression"
    adapter.last_run_id = "P23-2-RUN-01-TURN-03"
    adapter.last_events = []
    adapter.turn_captures = [
        _capture(
            run_id="P23-2-RUN-01-TURN-01",
            turn=1,
            step_id="STEP-01",
            start_index=10,
            tool="bash",
            call_id="call-early",
            execution_id="exec-early",
        ),
        _capture(
            run_id="P23-2-RUN-01-TURN-02",
            turn=2,
            step_id="STEP-02",
            start_index=20,
            tool="read",
            call_id="call-mid",
            execution_id="exec-mid",
        ),
        _capture(
            run_id="P23-2-RUN-01-TURN-03",
            turn=3,
            step_id="STEP-03",
            start_index=30,
            tool="read",
            call_id="call-late",
            execution_id="exec-late",
        ),
    ]

    trace = adapter.get_tool_trace().value or []
    early, mid, late = trace

    assert early["run_id"] == "P23-2-RUN-01-TURN-01"
    assert early["turn"] == 1
    assert early["event_index"] == 10
    assert early["execution_receipt"]["run_id"] == "P23-2-RUN-01-TURN-01"
    assert mid["run_id"] == "P23-2-RUN-01-TURN-02"
    assert mid["turn"] == 2
    assert mid["event_index"] == 20
    assert mid["execution_receipt"]["run_id"] == "P23-2-RUN-01-TURN-02"
    assert late["run_id"] == "P23-2-RUN-01-TURN-03"
    assert late["turn"] == 3
    assert late["event_index"] == 30
    assert late["execution_receipt"]["run_id"] == "P23-2-RUN-01-TURN-03"

    evidence = adapter.collect_evidence(
        step_id="FINAL",
        run_id="P23-2-RUN-01",
        session_id=adapter.session_id,
    )
    verifier = EvidenceVerifier()
    envelopes = [verifier.verify(item) for item in evidence]
    assert all(verifier.is_trusted(envelope) for envelope in envelopes)

    receipts = ExecutionReceiptValidator().receipts_from_evidence(
        verifier.trusted_evidence_items(envelopes)
    )
    assert [(receipt.execution_id, receipt.run_id) for receipt in receipts] == [
        ("exec-early", "P23-2-RUN-01-TURN-01"),
        ("exec-mid", "P23-2-RUN-01-TURN-02"),
        ("exec-late", "P23-2-RUN-01-TURN-03"),
    ]
