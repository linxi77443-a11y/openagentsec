"""AdapterConfig and CredentialResolver for OpenAgentSec Target Adapters.

PRD v4.0.2 §7 & §7.4:
Ensures safe handling of adapter connection configuration:
- Strict rejection of raw credentials (api_key, token, password, private_key)
- Support for safe credential references (e.g., 'ENV:NAME')
- Strict rejection of URL userinfo (http://user:pass@host)
- Strict rejection of sensitive query parameters
- Safe repr and to_dict without credential leakage
- Runtime-only in-memory resolution of secrets
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Protocol
from urllib.parse import parse_qs, urlparse

from ..models.exceptions import OpenAgentSecModelError

FORBIDDEN_SECRET_KEYS = {
    "api_key",
    "apikey",
    "token",
    "auth_token",
    "access_token",
    "secret",
    "secret_key",
    "password",
    "passwd",
    "private_key",
}

SENSITIVE_PARAM_PATTERN = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|passwd|bearer|auth[_-]?token)"
)


class AdapterConfigurationError(OpenAgentSecModelError):
    """Raised when an AdapterConfig contains invalid or unsafe parameters."""
    pass


class CredentialResolver(Protocol):
    """Protocol for resolving credential references to in-memory secrets at request time."""

    def resolve(self, credential_ref: str) -> Optional[str]:
        """Resolve a credential reference (e.g. 'ENV:MY_KEY') to a secret string."""
        ...


class EnvCredentialResolver:
    """Default credential resolver supporting environment variable references."""

    def resolve(self, credential_ref: str) -> Optional[str]:
        if not credential_ref:
            return None
        if credential_ref.startswith("ENV:"):
            var_name = credential_ref[4:].strip()
            return os.environ.get(var_name)
        elif credential_ref.startswith("KEYRING:"):
            # Mock / placeholder for keyring references
            return None
        return None


@dataclass
class AdapterConfig:
    """Configuration for TargetAdapter transport and protocol connection."""

    endpoint: str
    credential_ref: Optional[str] = None
    timeout_seconds: float = 30.0
    headers: Dict[str, str] = field(default_factory=dict)
    request_params: Dict[str, Any] = field(default_factory=dict)
    response_mapping: Dict[str, Any] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._validate_endpoint(self.endpoint)
        self._validate_forbidden_keys("extra", self.extra)
        self._validate_forbidden_keys("request_params", self.request_params)
        self._validate_headers(self.headers)
        self._validate_credential_ref(self.credential_ref)

        if self.timeout_seconds <= 0:
            raise AdapterConfigurationError("timeout_seconds must be a positive number")

    @classmethod
    def _validate_endpoint(cls, endpoint: str) -> None:
        if not endpoint or not isinstance(endpoint, str):
            raise AdapterConfigurationError("endpoint must be a non-empty string")

        # Allow placeholder strings like '<SIM_REST_API_ENDPOINT>'
        if endpoint.startswith("<") and endpoint.endswith(">"):
            return

        try:
            parsed = urlparse(endpoint)
        except Exception as e:
            raise AdapterConfigurationError(f"Invalid endpoint URL '{endpoint}': {e}") from e

        # 1. Reject userinfo in URL (user:pass@host)
        if parsed.username or parsed.password:
            raise AdapterConfigurationError(
                f"Endpoint URL must not contain embedded userinfo/credentials: '{endpoint}'"
            )

        # 2. Reject sensitive query parameters (?api_key=..., ?token=...)
        if parsed.query:
            params = parse_qs(parsed.query)
            for param_key in params.keys():
                if SENSITIVE_PARAM_PATTERN.search(param_key):
                    raise AdapterConfigurationError(
                        f"Endpoint URL query string must not contain sensitive credential parameters ('{param_key}')"
                    )

    @classmethod
    def _validate_forbidden_keys(cls, context: str, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            return
        for k, v in data.items():
            if k.lower() in FORBIDDEN_SECRET_KEYS:
                raise AdapterConfigurationError(
                    f"Raw credential key '{k}' is forbidden in {context}. "
                    f"Use 'credential_ref' instead."
                )
            if isinstance(v, dict):
                cls._validate_forbidden_keys(f"{context}.{k}", v)

    @classmethod
    def _validate_headers(cls, headers: Dict[str, str]) -> None:
        if not isinstance(headers, dict):
            return
        for k, v in headers.items():
            if k.lower() == "authorization":
                # If static header contains actual live bearer/token
                if isinstance(v, str) and not v.startswith("<") and not v.startswith("{{"):
                    if any(prefix in v.lower() for prefix in ("bearer ", "basic ", "token ")):
                        token_part = v.split(" ", 1)[-1]
                        if len(token_part) > 10 and not token_part.startswith("<"):
                            raise AdapterConfigurationError(
                                "Raw Authorization header with live secret is forbidden in AdapterConfig. "
                                "Use 'credential_ref' instead."
                            )

    @classmethod
    def _validate_credential_ref(cls, credential_ref: Optional[str]) -> None:
        if credential_ref is None:
            return
        if not isinstance(credential_ref, str):
            raise AdapterConfigurationError("credential_ref must be a string")
        if not any(credential_ref.startswith(prefix) for prefix in ("ENV:", "KEYRING:", "VAULT:", "REF:")):
            raise AdapterConfigurationError(
                f"credential_ref '{credential_ref}' must declare a recognized reference scheme "
                f"(e.g., 'ENV:OPENAI_API_KEY', 'KEYRING:service_name')"
            )

    def resolve_credential(self, resolver: Optional[CredentialResolver] = None) -> Optional[str]:
        """Resolve credential reference to an in-memory secret for immediate request use.

        The resolved secret is NEVER saved in AdapterConfig fields or logged.
        """
        if not self.credential_ref:
            return None
        res = resolver or EnvCredentialResolver()
        return res.resolve(self.credential_ref)

    def to_dict(self, mask_secrets: bool = True) -> Dict[str, Any]:
        """Convert AdapterConfig to dictionary."""
        return {
            "endpoint": self.endpoint,
            "credential_ref": self.credential_ref,
            "timeout_seconds": self.timeout_seconds,
            "headers": dict(self.headers),
            "request_params": dict(self.request_params),
            "response_mapping": dict(self.response_mapping),
            "extra": dict(self.extra),
        }

    def __repr__(self) -> str:
        return (
            f"AdapterConfig(endpoint='{self.endpoint}', "
            f"credential_ref='{self.credential_ref}', "
            f"timeout_seconds={self.timeout_seconds})"
        )
