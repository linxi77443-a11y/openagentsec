"""HTTP Client Backend implementing TargetBackend contract for Black-box LangGraph Target."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request

from src.openagentsec.adapters.backend import TargetBackend


class HTTPBlackboxTargetBackend(TargetBackend):
    """TargetBackend implementation connecting to localhost HTTP Blackbox Server over process boundary."""

    def __init__(self, endpoint_url: str, session_id: Optional[str] = None) -> None:
        self.endpoint_url = endpoint_url.rstrip("/")
        self.session_id = session_id or "session_blackbox_01"
        self._history: List[Dict[str, Any]] = []
        self._last_response: Optional[Dict[str, Any]] = None

    def _post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.endpoint_url}{path}"
        req_body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            resp_body = resp.read().decode("utf-8")
            return json.loads(resp_body)

    def send_input(self, stimulus: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {
            "session_id": self.session_id,
            "input": stimulus,
        }
        res = self._post("/message", payload)
        self._last_response = res
        self._history.append({
            "input": stimulus,
            "response": res.get("response", ""),
            "tool_calls": res.get("tool_calls", []),
        })
        return res

    def reset(self) -> bool:
        payload = {"session_id": self.session_id}
        res = self._post("/reset", payload)
        self._history.clear()
        self._last_response = None
        return res.get("status") == "reset_accepted"

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def get_last_response(self) -> Optional[Dict[str, Any]]:
        return self._last_response
