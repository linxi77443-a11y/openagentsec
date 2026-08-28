from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

REDACTION_PATTERNS = [
    (re.compile(r"HONEYTOKEN_[A-Z0-9_]+"), "[REDACTED_HONEYTOKEN]"),
    (re.compile(r"FAKE_SECRET_[A-Z0-9_]+"), "[REDACTED_FAKE_SECRET]"),
    (re.compile(r"DUMMY_TOKEN_[A-Z0-9_]+"), "[REDACTED_DUMMY_TOKEN]"),
    (re.compile(r"(?i)bearer\s+[a-z0-9._\-]{8,}"), "[REDACTED_TOKEN]"),
    (re.compile(r"(?i)(?:api[_-]?key|token|secret)[=:][a-z0-9._\-]{8,}"), "[REDACTED_TOKEN]"),
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
]


def redact_text(text: str) -> str:
    redacted = text
    for pattern, replacement in REDACTION_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def redact_json(obj: Any) -> Any:
    if isinstance(obj, str):
        return redact_text(obj)
    if isinstance(obj, Mapping):
        return {key: redact_json(value) for key, value in obj.items()}
    if isinstance(obj, Sequence) and not isinstance(obj, bytes | bytearray):
        return [redact_json(value) for value in obj]
    return obj
