"""Contract tests for the explicit DeepSeek Live opt-in gate."""

from __future__ import annotations

from tests.integration.real_world.conftest import (
    EXTERNAL_API_TEST_ENV,
    LIVE_TEST_ENV,
    external_api_tests_enabled,
    live_tests_enabled,
)


def test_live_runtime_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv(LIVE_TEST_ENV, raising=False)

    assert live_tests_enabled() is False


def test_live_runtime_requires_explicit_true(monkeypatch) -> None:
    monkeypatch.setenv(LIVE_TEST_ENV, "1")
    assert live_tests_enabled() is False

    monkeypatch.setenv(LIVE_TEST_ENV, "true")
    assert live_tests_enabled() is True


def test_external_api_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv(EXTERNAL_API_TEST_ENV, raising=False)

    assert external_api_tests_enabled() is False


def test_external_api_requires_explicit_true(monkeypatch) -> None:
    monkeypatch.setenv(EXTERNAL_API_TEST_ENV, "1")
    assert external_api_tests_enabled() is False

    monkeypatch.setenv(EXTERNAL_API_TEST_ENV, "true")
    assert external_api_tests_enabled() is True
