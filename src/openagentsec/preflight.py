"""Environment Preflight — unified, independent, fail-closed safety gate.

PRD v4.0.2 §17.1 requires a preflight gate covering ten dimensions before any
model or target-tool invocation:

    network / credential / tool inventory / filesystem / identity / audit /
    tenant / target binding / authorization scope / runtime mode

Design rules (fail-closed):
  * Runs before any model call or target tool call.
  * Payload declarations never substitute for real local probing.
  * ``PASS`` is only returned when every critical dimension is verifiable.
  * ``BLOCKED`` / ``INCONCLUSIVE`` / ``ERROR`` never continue execution.
  * Plaintext credentials are never recorded (values are masked).
  * Network probes never contact arbitrary internet targets (loopback only).

This module is standalone: it does not refactor existing execution entry
points.  It is also dependency-light (standard library plus the project's
existing ``yaml`` dependency).
"""
from __future__ import annotations

import os
import re
import socket
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from src.openagentsec.result_contract import (
    PASS,
    BLOCKED,
    INCONCLUSIVE,
    ERROR,
)

STATUS_PASS = PASS  # "PASS"
STATUS_FAIL = "FAIL"  # explicit violation -> hard block
STATUS_BLOCKED = BLOCKED  # "BLOCKED"
STATUS_INCONCLUSIVE = INCONCLUSIVE  # "INCONCLUSIVE"
STATUS_ERROR = ERROR  # "ERROR"

# Aggregation priority, highest first.
_STATUS_PRIORITY = (STATUS_BLOCKED, STATUS_FAIL, STATUS_ERROR, STATUS_INCONCLUSIVE, STATUS_PASS)

_DEFAULT_CREDENTIAL_PATTERN = re.compile(
    r"^(<[A-Z0-9_]+>|FAKE_[A-Z0-9_]+|DUMMY_[A-Z0-9_]+|HONEYTOKEN_[A-Z0-9_]+)"
)


@dataclass
class PreflightCheck:
    """A single dimension check.  ``detail`` never carries plaintext secrets."""

    name: str
    status: str
    detail: str = ""
    sensitive: bool = False

    def to_dict(self) -> dict:
        return {"name": self.name, "status": self.status, "detail": self.detail}


@dataclass
class PreflightResult:
    """Aggregated preflight outcome.  ``ready`` is True only on full PASS."""

    overall: str = STATUS_INCONCLUSIVE
    ready: bool = False
    checks: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overall": self.overall,
            "ready": self.ready,
            "checks": [check.to_dict() for check in self.checks],
        }


def _aggregate(checks: list) -> tuple[str, bool]:
    """Fail-closed aggregation: BLOCKED > FAIL > ERROR > INCONCLUSIVE > PASS."""
    overall = STATUS_PASS
    for check in checks:
        if check.status == STATUS_BLOCKED:
            return STATUS_BLOCKED, False
        if check.status == STATUS_FAIL:
            overall = STATUS_FAIL
        elif check.status == STATUS_ERROR and overall == STATUS_PASS:
            overall = STATUS_ERROR
        elif check.status == STATUS_INCONCLUSIVE and overall == STATUS_PASS:
            overall = STATUS_INCONCLUSIVE
    return overall, overall == STATUS_PASS


def _mask(value: Any) -> str:
    text = str(value)
    if len(text) <= 4:
        return "****"
    return text[:2] + "*" * (len(text) - 4) + text[-2:]


def default_preflight_config() -> dict:
    """Safe default configuration (all dimensions isolated/test-oriented)."""
    return {
        "network_mode": "off",
        "network_approved": False,
        "external_targets": [],
        "audit_enabled": True,
        "audit_dir": None,
        "synthetic_only": True,
        "fake_runtime_only": True,
        "runtime_mode": "synthetic",
        "dry_run": True,
        "tool_inventory": [],
        "allowed_tool_prefixes": ("fake_",),
        "deny_tools": ("execute_shell_command", "delete_record", "read_fake_secret"),
        "sandbox_root": None,
        "filesystem_paths": [],
        "target": None,
        "target_type": "local",
        "allowed_target_types": ("local", "sandbox", "loopback"),
        "tenant": "test_tenant",
        "deny_tenants": ("prod", "production"),
        "identity": "test_user",
        "identity_pattern": r"^(test_|tester_|sim_)",
        "authorization_ref": None,
        "authorization_scope": "read_only",
        "write_approved": False,
        "credentials": {},
        "credential_placeholder_pattern": (
            r"^(<[A-Z0-9_]+>|FAKE_[A-Z0-9_]+|DUMMY_[A-Z0-9_]+|HONEYTOKEN_[A-Z0-9_]+)"
        ),
    }


class EnvironmentPreflight:
    """Ten-dimension, fail-closed environment preflight gate."""

    def __init__(self, config: Optional[dict] = None, root: Optional[Path] = None) -> None:
        self.cfg = dict(default_preflight_config())
        if config:
            self.cfg.update(config)
        self.root = Path(root) if root else Path.cwd()
        self.checks: list = []

    # ------------------------------------------------------------------ probe
    def _probe_loopback(self) -> bool:
        """Real but strictly local probe: bind a loopback socket, never egress."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(("127.0.0.1", 0))
            finally:
                sock.close()
            return True
        except OSError:
            return False

    # ------------------------------------------------------------ dimensions
    def _check_network(self) -> PreflightCheck:
        mode = str(self.cfg.get("network_mode", "off")).lower()
        if mode not in ("off", "loopback_only", "approved_external"):
            return PreflightCheck("network", STATUS_BLOCKED, f"unknown network_mode: {mode!r}")
        if not self._probe_loopback():
            return PreflightCheck(
                "network", STATUS_INCONCLUSIVE, "cannot determine local network capability"
            )
        external = self.cfg.get("external_targets") or []
        if mode in ("off", "loopback_only"):
            if external:
                return PreflightCheck(
                    "network",
                    STATUS_BLOCKED,
                    f"external targets configured while network_mode={mode}",
                )
            return PreflightCheck("network", STATUS_PASS, f"network_mode={mode}; loopback probe ok")
        # approved_external: policy verified here; outbound I/O stays gated by sandbox.
        if not self.cfg.get("network_approved", False):
            return PreflightCheck("network", STATUS_BLOCKED, "external network requires explicit approval")
        if not external:
            return PreflightCheck("network", STATUS_INCONCLUSIVE, "external targets declared but list empty")
        return PreflightCheck("network", STATUS_PASS, "external network approved; outbound I/O gated by sandbox")

    def _check_credential(self) -> PreflightCheck:
        creds = self.cfg.get("credentials")
        if creds is None:
            creds = {}
        if not isinstance(creds, dict):
            return PreflightCheck("credential", STATUS_INCONCLUSIVE, "credentials is not a mapping")
        pattern = re.compile(str(self.cfg.get("credential_placeholder_pattern")))
        for name, value in creds.items():
            if value is None or value == "":
                continue
            text = str(value).strip()
            if not pattern.match(text):
                # Never echo the secret itself; only the field name + masked tail.
                return PreflightCheck(
                    "credential",
                    STATUS_FAIL,
                    f"credential {name!r} is not a synthetic placeholder (value masked: {_mask(text)})",
                    sensitive=True,
                )
        return PreflightCheck("credential", STATUS_PASS, "all credential fields use synthetic placeholders")

    def _check_tool_inventory(self) -> PreflightCheck:
        inventory = self.cfg.get("tool_inventory")
        prefixes = tuple(self.cfg.get("allowed_tool_prefixes") or ("fake_",))
        deny = set(self.cfg.get("deny_tools") or ())
        tools: list = []
        if isinstance(inventory, (str, Path)):
            path = Path(inventory)
            if not path.is_absolute():
                path = self.root / path
            if not path.is_file():
                return PreflightCheck("tool_inventory", STATUS_INCONCLUSIVE, f"tool inventory file not found: {inventory}")
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError) as exc:
                return PreflightCheck("tool_inventory", STATUS_ERROR, f"tool inventory parse error: {exc}")
            if isinstance(data, dict):
                tools = data.get("tools", [])
            elif isinstance(data, list):
                tools = data
        elif isinstance(inventory, list):
            tools = inventory
        else:
            return PreflightCheck("tool_inventory", STATUS_INCONCLUSIVE, "tool_inventory not configured")

        if not isinstance(tools, list) or not tools:
            return PreflightCheck("tool_inventory", STATUS_INCONCLUSIVE, "tool inventory is empty; cannot verify")

        for tool in tools:
            name = tool.get("tool_name") if isinstance(tool, dict) else tool
            if not isinstance(name, str) or not name:
                return PreflightCheck("tool_inventory", STATUS_INCONCLUSIVE, "tool entry missing tool_name")
            if name in deny:
                return PreflightCheck("tool_inventory", STATUS_BLOCKED, f"tool {name!r} is on the deny list")
            if not name.startswith(prefixes):
                return PreflightCheck(
                    "tool_inventory", STATUS_BLOCKED, f"tool {name!r} is not on the allow prefix {prefixes!r}"
                )
        return PreflightCheck("tool_inventory", STATUS_PASS, f"{len(tools)} tool(s) verified")

    def _check_filesystem(self) -> PreflightCheck:
        sandbox_root = self.cfg.get("sandbox_root")
        if not sandbox_root:
            return PreflightCheck("filesystem", STATUS_INCONCLUSIVE, "sandbox_root not configured")
        root_real = os.path.realpath(str(sandbox_root))
        if not os.path.isdir(root_real):
            return PreflightCheck("filesystem", STATUS_INCONCLUSIVE, f"sandbox_root is not a directory: {sandbox_root}")
        paths = self.cfg.get("filesystem_paths")
        if not isinstance(paths, list):
            return PreflightCheck("filesystem", STATUS_INCONCLUSIVE, "filesystem_paths is not a list")
        for path in paths:
            resolved = os.path.realpath(str(path))
            if resolved != root_real and not resolved.startswith(root_real + os.sep):
                return PreflightCheck("filesystem", STATUS_BLOCKED, f"path {path!r} escapes sandbox root")
        return PreflightCheck("filesystem", STATUS_PASS, "all filesystem paths stay within sandbox root")

    def _check_identity(self) -> PreflightCheck:
        identity = self.cfg.get("identity")
        if not identity:
            return PreflightCheck("identity", STATUS_INCONCLUSIVE, "identity not configured")
        pattern = re.compile(str(self.cfg.get("identity_pattern")))
        if not pattern.match(str(identity).strip()):
            return PreflightCheck("identity", STATUS_FAIL, "identity is not a test/synthetic identity")
        return PreflightCheck("identity", STATUS_PASS, f"identity {identity!r} is a test identity")

    def _check_audit(self) -> PreflightCheck:
        if not self.cfg.get("audit_enabled", False):
            return PreflightCheck("audit", STATUS_BLOCKED, "audit_enabled is false")
        audit_dir = self.cfg.get("audit_dir")
        if not audit_dir:
            return PreflightCheck("audit", STATUS_INCONCLUSIVE, "audit_dir not configured")
        adir = Path(str(audit_dir))
        if not adir.is_absolute():
            adir = self.root / adir
        try:
            adir.mkdir(parents=True, exist_ok=True)
            with (adir / "preflight.log").open("a", encoding="utf-8") as fh:
                fh.write(f"preflight_probe {time.time():.0f}\n")
        except OSError as exc:
            return PreflightCheck("audit", STATUS_INCONCLUSIVE, f"audit dir not writable: {exc}")
        return PreflightCheck("audit", STATUS_PASS, f"audit dir writable: {adir}")

    def _check_tenant(self) -> PreflightCheck:
        tenant = self.cfg.get("tenant")
        if not tenant:
            return PreflightCheck("tenant", STATUS_INCONCLUSIVE, "tenant not configured")
        deny = [str(item).lower() for item in (self.cfg.get("deny_tenants") or ())]
        text = str(tenant).lower()
        if any(item in text for item in deny):
            return PreflightCheck("tenant", STATUS_FAIL, "tenant matches the deny list (non-test tenant)")
        return PreflightCheck("tenant", STATUS_PASS, f"tenant {tenant!r} is a test tenant")

    def _check_target_binding(self) -> PreflightCheck:
        target = self.cfg.get("target")
        if not target:
            return PreflightCheck("target_binding", STATUS_INCONCLUSIVE, "target not configured")
        target_type = str(self.cfg.get("target_type", "local")).lower()
        allowed = set(self.cfg.get("allowed_target_types") or ("local", "sandbox", "loopback"))
        if target_type not in allowed:
            if not self.cfg.get("network_approved", False):
                return PreflightCheck(
                    "target_binding", STATUS_BLOCKED, f"target_type {target_type!r} requires approval"
                )
        return PreflightCheck("target_binding", STATUS_PASS, f"target {target!r} bound to {target_type}")

    def _check_authorization_scope(self) -> PreflightCheck:
        auth_ref = self.cfg.get("authorization_ref")
        if not auth_ref:
            return PreflightCheck("authorization_scope", STATUS_INCONCLUSIVE, "authorization_ref not configured")
        scope = str(self.cfg.get("authorization_scope", "read_only")).lower()
        if scope in ("write", "admin"):
            if not self.cfg.get("write_approved", False):
                return PreflightCheck(
                    "authorization_scope", STATUS_BLOCKED, f"authorization scope {scope!r} requires write_approved"
                )
        return PreflightCheck("authorization_scope", STATUS_PASS, f"authorization scope {scope!r} ok")

    def _check_runtime_mode(self) -> PreflightCheck:
        if not self.cfg.get("synthetic_only", False):
            return PreflightCheck("runtime_mode", STATUS_BLOCKED, "synthetic_only is false")
        if not self.cfg.get("fake_runtime_only", True):
            return PreflightCheck("runtime_mode", STATUS_BLOCKED, "fake_runtime_only is false")
        mode = str(self.cfg.get("runtime_mode", "synthetic")).lower()
        if mode in ("production", "real", "live"):
            return PreflightCheck("runtime_mode", STATUS_BLOCKED, f"runtime_mode {mode!r} is not allowed")
        return PreflightCheck("runtime_mode", STATUS_PASS, f"runtime_mode {mode!r} ok")

    # ---------------------------------------------------------------- runner
    def run(self) -> PreflightResult:
        self.checks = [
            self._check_network(),
            self._check_credential(),
            self._check_tool_inventory(),
            self._check_filesystem(),
            self._check_identity(),
            self._check_audit(),
            self._check_tenant(),
            self._check_target_binding(),
            self._check_authorization_scope(),
            self._check_runtime_mode(),
        ]
        overall, ready = _aggregate(self.checks)
        return PreflightResult(overall=overall, ready=ready, checks=self.checks)


def run_preflight(config: Optional[dict] = None, root: Optional[Path] = None) -> PreflightResult:
    """Convenience entry point: run the ten-dimension preflight gate."""
    return EnvironmentPreflight(config=config, root=root).run()


def assert_preflight_ready(config: Optional[dict] = None, root: Optional[Path] = None) -> bool:
    """Fail-closed convenience: True only when every dimension is PASS."""
    return run_preflight(config, root).ready
