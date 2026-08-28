"""Unit tests for AdapterConfig and CredentialResolver safeguards (PRD v4.0.2 Phase 2B)."""

from __future__ import annotations

import os
import pytest

from src.openagentsec.adapters.config import (
    AdapterConfig,
    AdapterConfigurationError,
    EnvCredentialResolver,
)


def test_valid_adapter_config_with_credential_ref() -> None:
    config = AdapterConfig(
        endpoint="https://api.openai.com/v1",
        credential_ref="ENV:TEST_OPENAI_KEY",
        timeout_seconds=15.0,
        headers={"Content-Type": "application/json"},
    )
    assert config.endpoint == "https://api.openai.com/v1"
    assert config.credential_ref == "ENV:TEST_OPENAI_KEY"
    assert config.timeout_seconds == 15.0
    assert repr(config) == "AdapterConfig(endpoint='https://api.openai.com/v1', credential_ref='ENV:TEST_OPENAI_KEY', timeout_seconds=15.0)"


def test_rejection_of_raw_secret_keys() -> None:
    """Raw credential parameters in extra or request_params must be strictly rejected."""
    with pytest.raises(AdapterConfigurationError, match="Raw credential key 'api_key' is forbidden"):
        AdapterConfig(
            endpoint="https://api.example.com",
            extra={"api_key": "sk-1234567890"},
        )

    with pytest.raises(AdapterConfigurationError, match="Raw credential key 'token' is forbidden"):
        AdapterConfig(
            endpoint="https://api.example.com",
            request_params={"token": "secret_token"},
        )

    with pytest.raises(AdapterConfigurationError, match="Raw credential key 'password' is forbidden"):
        AdapterConfig(
            endpoint="https://api.example.com",
            extra={"nested": {"password": "admin_password"}},
        )


def test_rejection_of_embedded_url_credentials() -> None:
    """URLs containing embedded userinfo (user:pass@host) must be rejected."""
    with pytest.raises(AdapterConfigurationError, match="must not contain embedded userinfo"):
        AdapterConfig(endpoint="https://admin:secret123@api.example.com/v1")


def test_rejection_of_sensitive_url_query_parameters() -> None:
    """URLs containing sensitive credential query parameters must be rejected."""
    with pytest.raises(AdapterConfigurationError, match="must not contain sensitive credential parameters"):
        AdapterConfig(endpoint="https://api.example.com/v1/chat?api_key=secret_value")

    with pytest.raises(AdapterConfigurationError, match="must not contain sensitive credential parameters"):
        AdapterConfig(endpoint="https://api.example.com/v1/chat?auth_token=xyz")


def test_rejection_of_raw_authorization_header_with_secret() -> None:
    """Static Authorization header containing a real token must be rejected in favor of credential_ref."""
    with pytest.raises(AdapterConfigurationError, match="Raw Authorization header with live secret is forbidden"):
        AdapterConfig(
            endpoint="https://api.example.com/v1",
            headers={"Authorization": "Bearer sk-live-secret-token-1234567890"},
        )


def test_runtime_credential_resolution_without_persistence() -> None:
    """CredentialResolver must resolve secrets only in-memory without storing into AdapterConfig fields."""
    os.environ["TEST_TARGET_KEY_123"] = "resolved_secret_token_val"
    try:
        config = AdapterConfig(
            endpoint="https://api.example.com/v1",
            credential_ref="ENV:TEST_TARGET_KEY_123",
        )
        resolver = EnvCredentialResolver()
        resolved = config.resolve_credential(resolver)
        assert resolved == "resolved_secret_token_val"

        # Verify secret is NOT stored on config instance fields or in repr/to_dict
        assert "resolved_secret_token_val" not in repr(config)
        assert "resolved_secret_token_val" not in str(config.to_dict())
    finally:
        os.environ.pop("TEST_TARGET_KEY_123", None)
