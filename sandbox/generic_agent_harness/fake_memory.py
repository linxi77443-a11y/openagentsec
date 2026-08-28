"""Fake memory store for Generic Agent Mock Harness — local sandbox only."""

from __future__ import annotations

from typing import Any

# In-memory store — no real file system access
_memory_store: list[dict[str, Any]] = []
_memory_events: list[dict[str, Any]] = []


def read_memory() -> dict[str, Any]:
    return {
        "memory_store": list(_memory_store),
        "event_count": len(_memory_events),
        "source": "local_fake_memory_only",
    }


def write_memory(content: str, requested_by: str, approved: bool = False) -> dict[str, Any]:
    blocked_reasons = []
    lower = content.lower()
    if not approved:
        blocked_reasons.append("memory_write_not_approved")
    if any(word in lower for word in ["secret", "token", "password", "key", "ignore previous", "ignore all", "override", "bypass"]):
        blocked_reasons.append("malicious_content_detected")

    if blocked_reasons:
        return {
            "action": "memory_write",
            "allowed": False,
            "blocked_reasons": blocked_reasons,
            "content_preview": content[:80] + ("..." if len(content) > 80 else ""),
        }

    entry = {
        "content": content,
        "requested_by": requested_by,
        "approved": True,
        "trust_level": "untrusted_user_input",
    }
    _memory_store.append(entry)
    _memory_events.append({"action": "write", "status": "allowed", "requested_by": requested_by})
    return {"action": "memory_write", "allowed": True, "trust_level": "untrusted_user_input"}


def list_memory_events() -> dict[str, Any]:
    return {"events": list(_memory_events), "source": "local_fake_memory_only"}


def reset() -> None:
    _memory_store.clear()
    _memory_events.clear()
