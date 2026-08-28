"""Standalone localhost HTTP server exposing LangGraph MVP-1 Target over standard Black-box Protocol.

Uses pure Python standard library http.server (no external web framework dependencies).
Runs as an independent OS process in .venv-langgraph.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import sys
import uuid

# Ensure repository root is on path when executed directly
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tests.integration.external_targets.langgraph_mvp1.target_agent import (
    LangGraphMVP1TargetAgent,
)
from langchain_core.messages import AIMessage


class BlackboxTargetHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler implementing black-box protocol for LangGraph MVP-1."""

    agent: LangGraphMVP1TargetAgent = None  # Class-level target instance

    def _send_json(self, status_code: int, data: dict) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {
                "status": "ok",
                "target_id": "TARGET-LANGGRAPH-MVP1-BLACKBOX",
                "pid": os.getpid(),
            })
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "Invalid JSON payload"})
            return

        if self.path == "/session":
            session_id = body.get("session_id") or f"sess_{uuid.uuid4().hex[:8]}"
            self._send_json(200, {
                "session_id": session_id,
                "status": "created",
            })
            return

        if self.path == "/message":
            session_id = body.get("session_id", "default_session")
            user_input = body.get("input", "")

            # Execute real LangGraph target in this process
            state_result = self.agent.run(prompt=user_input, thread_id=session_id)

            # Extract standard black-box response and naturally exposed tool_calls
            messages = state_result.get("messages", [])
            response_text = ""
            tool_calls = []

            for msg in messages:
                if isinstance(msg, AIMessage):
                    if msg.content:
                        response_text = str(msg.content)
                    if msg.tool_calls:
                        for tc in msg.tool_calls:
                            tool_calls.append({
                                "name": tc["name"],
                                "args": tc["args"],
                                "id": tc["id"],
                            })

            self._send_json(200, {
                "session_id": session_id,
                "content": response_text,
                "response": response_text,
                "tool_calls": tool_calls,
                "status": "success",
            })
            return

        if self.path == "/reset":
            session_id = body.get("session_id", "default_session")
            self.agent.reset(thread_id=session_id)
            self._send_json(200, {
                "session_id": session_id,
                "status": "reset_accepted",
            })
            return

        self._send_json(404, {"error": "Endpoint Not Found"})

    def log_message(self, format: str, *args: object) -> None:
        # Suppress noisy standard server logs in tests
        pass


def run_server(port: int) -> None:
    BlackboxTargetHTTPHandler.agent = LangGraphMVP1TargetAgent()
    server = HTTPServer(("127.0.0.1", port), BlackboxTargetHTTPHandler)
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangGraph MVP-1 Blackbox HTTP Server")
    parser.add_argument("--port", type=int, required=True, help="Port to listen on (127.0.0.1 only)")
    args = parser.parse_args()
    run_server(args.port)
