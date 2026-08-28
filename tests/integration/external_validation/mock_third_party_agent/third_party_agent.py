"""Custom Third-Party Agent Runtime (PRD v4.0.2 Phase 7.5.1).

Simulates an external developer's proprietary Python agent runtime with zero knowledge
of LangGraph, LangChain, MCP, OpenAgentSec core, or Oracles.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid


class CustomEnterpriseAgent:
    """Proprietary enterprise agent executing private tool dispatch workflows."""

    def __init__(self, agent_name: str = "EnterpriseAssistantV2") -> None:
        self.agent_name = agent_name
        self.session_id: str = f"sess_ent_{uuid.uuid4().hex[:6]}"
        self.turn_history: List[Dict[str, Any]] = []
        self.executed_tools: List[Dict[str, Any]] = []

    def handle_user_prompt(self, prompt: str) -> Dict[str, Any]:
        """Execute conversational reasoning and dispatch local tools."""
        self.turn_history.append({"role": "user", "text": prompt})
        prompt_lower = prompt.lower()
        call_id = f"call_ent_{uuid.uuid4().hex[:6]}"

        if any(w in prompt_lower for w in ["webhook", "exfiltrate", "export", "send_data"]):
            # Dispatches outbound webhook tool
            target_url = "https://external.webhook.test/ingest" if "external" in prompt_lower else "https://internal.vault.local/backup"
            tool_record = {
                "call_id": call_id,
                "tool_name": "send_outbound_webhook",
                "args": {"url": target_url, "payload": "ENCRYPTED_USER_PAYLOAD_001"},
                "status": "success",
                "output": f"Webhook transmitted to {target_url}",
            }
            self.executed_tools.append(tool_record)
            reply = f"Dispatched webhook to {target_url}."
        elif any(w in prompt_lower for w in ["lookup", "directory", "search"]):
            # Dispatches internal directory lookup tool
            tool_record = {
                "call_id": call_id,
                "tool_name": "lookup_internal_directory",
                "args": {"query": prompt},
                "status": "success",
                "output": "Directory records: 12 matches found.",
            }
            self.executed_tools.append(tool_record)
            reply = "Found 12 matching directory records."
        else:
            reply = f"Hello! How can I assist your enterprise workflow today?"

        self.turn_history.append({"role": "assistant", "text": reply})
        return {
            "reply": reply,
            "tool_dispatches": list(self.executed_tools),
            "session_id": self.session_id,
        }

    def clear_state(self) -> None:
        """Reset internal session state."""
        self.session_history = []
        self.executed_tools.clear()
        self.session_id = f"sess_ent_{uuid.uuid4().hex[:6]}"
