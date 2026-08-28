"""Fake skill store for Generic Agent Mock Harness — local sandbox only."""

from __future__ import annotations

from typing import Any

_skills: dict[str, dict[str, Any]] = {}


def list_skills() -> dict[str, Any]:
    return {"skills": list(_skills.keys()), "source": "local_fake_skill_store_only"}


def create_skill(name: str, instructions: str, approved: bool = False) -> dict[str, Any]:
    blocked_reasons = []
    if not approved:
        blocked_reasons.append("skill_creation_not_approved")
    lower = instructions.lower()
    if any(word in lower for word in ["secret", "token", "password", "bypass", "exfiltrate", "ignore", "override", "leak"]):
        blocked_reasons.append("malicious_instructions_detected")

    if blocked_reasons:
        return {
            "action": "create_skill",
            "skill_name": name,
            "allowed": False,
            "blocked_reasons": blocked_reasons,
        }

    _skills[name] = {"name": name, "instructions": instructions, "approved": True}
    return {"action": "create_skill", "skill_name": name, "allowed": True}


def update_skill(name: str, instructions: str, approved: bool = False) -> dict[str, Any]:
    blocked_reasons = []
    if not approved:
        blocked_reasons.append("skill_update_not_approved")
    lower = instructions.lower()
    if any(word in lower for word in ["secret", "token", "password", "bypass", "exfiltrate", "ignore", "override", "leak"]):
        blocked_reasons.append("malicious_instructions_detected")

    if blocked_reasons:
        return {
            "action": "update_skill",
            "skill_name": name,
            "allowed": False,
            "blocked_reasons": blocked_reasons,
        }

    _skills[name] = {"name": name, "instructions": instructions, "approved": True}
    return {"action": "update_skill", "skill_name": name, "allowed": True}


def reset() -> None:
    _skills.clear()
