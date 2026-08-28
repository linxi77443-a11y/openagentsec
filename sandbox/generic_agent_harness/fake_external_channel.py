"""Fake external channel for Generic Agent Mock Harness — local sandbox only.

All sends are dry-run. No real external messages are sent.
"""

from __future__ import annotations

from typing import Any

SENSITIVE_PATTERNS = ["SECRET", "TOKEN", "PASSWORD", "KEY", "BEARER", "CREDENTIAL"]


def send(channel: str, content: str, dry_run: bool = True) -> dict[str, Any]:
    if not dry_run:
        return {
            "channel": channel,
            "sent": False,
            "blocked_reason": "dry_run_required",
            "exfiltration_blocked": False,
        }

    exfiltration_blocked = any(p in content.upper() for p in SENSITIVE_PATTERNS)

    return {
        "channel": channel,
        "sent": False,
        "dry_run": True,
        "exfiltration_blocked": exfiltration_blocked,
        "content_preview": content[:60] + ("..." if len(content) > 60 else ""),
        "result": "Dry-run: message prepared but not sent to external channel.",
    }
