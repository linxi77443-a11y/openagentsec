"""Unit tests for ObservationResult and ObservationStatus (PRD v4.0.2 Phase 2B)."""

from __future__ import annotations

import pytest

from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.adapters.observation import (
    ObservationResult,
    ObservationSemanticError,
    ObservationStatus,
)


def test_valid_observation_results() -> None:
    # 1. OBSERVABLE + OBSERVED
    r1 = ObservationResult(
        observability=ObservabilityState.OBSERVABLE,
        status=ObservationStatus.OBSERVED,
        value={"answer": "hello"},
        source="test",
    )
    assert r1.is_observed is True
    assert r1.is_observable is True
    assert r1.is_empty is False
    assert r1.is_error is False
    assert r1.value == {"answer": "hello"}

    # 2. OBSERVABLE + EMPTY (e.g. tool channel observed, zero tool calls occurred)
    r2 = ObservationResult(
        observability=ObservabilityState.OBSERVABLE,
        status=ObservationStatus.EMPTY,
        value=[],
        source="test",
    )
    assert r2.is_observed is False
    assert r2.is_empty is True
    assert r2.value == []

    # 3. UNOBSERVABLE + NOT_OBSERVABLE (value MUST be None)
    r3 = ObservationResult(
        observability=ObservabilityState.UNOBSERVABLE,
        status=ObservationStatus.NOT_OBSERVABLE,
        value=None,
        source="test",
    )
    assert r3.is_observed is False
    assert r3.is_observable is False
    assert r3.value is None

    # 4. PARTIALLY_OBSERVABLE + PARTIAL
    r4 = ObservationResult(
        observability=ObservabilityState.PARTIALLY_OBSERVABLE,
        status=ObservationStatus.PARTIAL,
        value=[{"name": "tool_intent"}],
        source="test",
    )
    assert r4.is_observed is True
    assert r4.status == ObservationStatus.PARTIAL

    # 5. OBSERVABLE + ERROR
    r5 = ObservationResult(
        observability=ObservabilityState.OBSERVABLE,
        status=ObservationStatus.ERROR,
        value=None,
        source="test",
        reason="Network timeout",
    )
    assert r5.is_error is True
    assert r5.value is None


def test_unobservable_must_not_have_non_none_value() -> None:
    """UNOBSERVABLE dimensions must have value=None. Returning [] or {} is forbidden."""
    with pytest.raises(ObservationSemanticError, match="UNOBSERVABLE dimension must have value=None"):
        ObservationResult(
            observability=ObservabilityState.UNOBSERVABLE,
            status=ObservationStatus.NOT_OBSERVABLE,
            value=[],  # Forbidden: empty list implies observable but empty
        )

    with pytest.raises(ObservationSemanticError, match="UNOBSERVABLE dimension must have value=None"):
        ObservationResult(
            observability=ObservabilityState.UNOBSERVABLE,
            status=ObservationStatus.NOT_OBSERVABLE,
            value={},  # Forbidden
        )


def test_unobservable_cannot_have_observed_or_empty_status() -> None:
    """UNOBSERVABLE dimension cannot claim OBSERVED or EMPTY status."""
    with pytest.raises(ObservationSemanticError, match="UNOBSERVABLE dimension cannot have status 'OBSERVED'"):
        ObservationResult(
            observability=ObservabilityState.UNOBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value=None,
        )

    with pytest.raises(ObservationSemanticError, match="UNOBSERVABLE dimension cannot have status"):
        ObservationResult(
            observability=ObservabilityState.UNOBSERVABLE,
            status=ObservationStatus.EMPTY,
            value=None,
        )


def test_observable_cannot_have_not_observable_status() -> None:
    """OBSERVABLE dimension cannot claim NOT_OBSERVABLE status."""
    with pytest.raises(ObservationSemanticError, match="OBSERVABLE dimension cannot have status NOT_OBSERVABLE"):
        ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.NOT_OBSERVABLE,
            value=None,
        )


def test_error_status_requires_none_value() -> None:
    """ERROR status requires value=None and stores context in reason."""
    with pytest.raises(ObservationSemanticError, match="ERROR status requires value=None"):
        ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.ERROR,
            value={"data": 123},
        )


def test_partially_observable_semantic_constraints() -> None:
    """PARTIALLY_OBSERVABLE cannot claim OBSERVED status; PARTIAL status requires PARTIALLY_OBSERVABLE."""
    with pytest.raises(ObservationSemanticError, match="PARTIALLY_OBSERVABLE dimension cannot claim status 'OBSERVED'"):
        ObservationResult(
            observability=ObservabilityState.PARTIALLY_OBSERVABLE,
            status=ObservationStatus.OBSERVED,
            value={"tool": "search"},
        )

    with pytest.raises(ObservationSemanticError, match="PARTIAL status requires PARTIALLY_OBSERVABLE"):
        ObservationResult(
            observability=ObservabilityState.OBSERVABLE,
            status=ObservationStatus.PARTIAL,
            value={"tool": "search"},
        )


def test_observation_result_to_dict() -> None:
    r = ObservationResult(
        observability=ObservabilityState.OBSERVABLE,
        status=ObservationStatus.OBSERVED,
        value="test_output",
        source="unit_test",
        reason="ok",
    )
    d = r.to_dict()
    assert d == {
        "observability": "observable",
        "status": "OBSERVED",
        "value": "test_output",
        "source": "unit_test",
        "reason": "ok",
    }
