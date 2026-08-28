"""Safety gates for tests that contact live runtimes or paid APIs."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


LIVE_TEST_ENV = "OPENAGENTSEC_ENABLE_LIVE_TESTS"
EXTERNAL_API_TEST_ENV = "OPENAGENTSEC_ENABLE_EXTERNAL_API_TESTS"
LIVE_TEST_DIRECTORIES = frozenset(
    {
        "deepseek_attack_validation",
        "deepseek_live",
        "deepseek_live_violation",
        "deepseek_runtime_profile",
        "evidence_audit",
    }
)
EXTERNAL_API_TEST_DIRECTORIES = frozenset({"external_api"})


def live_tests_enabled() -> bool:
    """Require an explicit opt-in before contacting the local live runtime."""
    return os.environ.get(LIVE_TEST_ENV, "").strip().lower() == "true"


def external_api_tests_enabled() -> bool:
    """Require explicit consent before making billable remote API calls."""
    return os.environ.get(EXTERNAL_API_TEST_ENV, "").strip().lower() == "true"


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    del config
    skip_live = pytest.mark.skip(
        reason=f"live DeepSeek tests require {LIVE_TEST_ENV}=true"
    )
    skip_external = pytest.mark.skip(
        reason=f"real External API tests require {EXTERNAL_API_TEST_ENV}=true"
    )
    for item in items:
        path_parts = set(Path(str(item.path)).parts)
        if not live_tests_enabled() and path_parts & LIVE_TEST_DIRECTORIES:
            item.add_marker(skip_live)
        if (
            not external_api_tests_enabled()
            and path_parts & EXTERNAL_API_TEST_DIRECTORIES
        ):
            item.add_marker(skip_external)
