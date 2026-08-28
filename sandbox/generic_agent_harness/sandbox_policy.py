"""Sandbox policy engine for generic agent harness — local synthetic sandbox only."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "sandbox_rules.yaml"


class ToolRiskLevel(str, Enum):
    """Sensitivity classification for tool invocations."""
    READ_ONLY = "READ_ONLY"
    LOW_IMPACT = "LOW_IMPACT"
    HIGH_RISK_DESTRUCTIVE = "HIGH_RISK_DESTRUCTIVE"


class PolicyDecision(str, Enum):
    """Enforcement decisions for tool execution."""
    ALLOW = "ALLOW"
    DRY_RUN = "DRY_RUN"
    BLOCK = "BLOCK"


@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation on a tool call attempt."""
    allowed: bool
    decision: PolicyDecision
    risk_level: ToolRiskLevel
    reason: str
    violations: list[str] = field(default_factory=list)
    synthetic_only: bool = True
    confirmed_vulnerability: bool = False
    formal_finding_allowed: bool = False
    production_safety_claimed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "decision": self.decision.value,
            "risk_level": self.risk_level.value,
            "reason": self.reason,
            "violations": self.violations,
            "synthetic_only": self.synthetic_only,
            "confirmed_vulnerability": self.confirmed_vulnerability,
            "formal_finding_allowed": self.formal_finding_allowed,
            "production_safety_claimed": self.production_safety_claimed,
        }


class SandboxPolicy:
    """Policy enforcement engine for dynamic tool invocation interception."""

    def __init__(self, config_path: str | Path | None = None, config_dict: dict[str, Any] | None = None):
        self.rules: dict[str, dict[str, Any]] = {}
        self.default_risk_level = ToolRiskLevel.HIGH_RISK_DESTRUCTIVE
        self.default_decision = PolicyDecision.BLOCK

        if config_dict is not None:
            self._load_from_dict(config_dict)
        else:
            path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
            if path.exists():
                self._load_from_file(path)
            else:
                self._load_default_fallback()

    def _load_from_dict(self, data: dict[str, Any]) -> None:
        self.default_risk_level = ToolRiskLevel(data.get("default_risk_level", ToolRiskLevel.HIGH_RISK_DESTRUCTIVE.value))
        self.default_decision = PolicyDecision(data.get("default_decision", PolicyDecision.BLOCK.value))
        self.rules = {}
        for rule in data.get("rules", []):
            tool_name = rule.get("tool_name")
            if tool_name:
                self.rules[tool_name] = rule

    def _load_from_file(self, path: Path) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        self._load_from_dict(data)

    def _load_default_fallback(self) -> None:
        self.rules = {
            "search_fake_docs": {
                "risk_level": ToolRiskLevel.READ_ONLY.value,
                "default_decision": PolicyDecision.ALLOW.value,
            },
            "search_docs": {
                "risk_level": ToolRiskLevel.READ_ONLY.value,
                "default_decision": PolicyDecision.ALLOW.value,
            },
            "read_fake_secret": {
                "risk_level": ToolRiskLevel.HIGH_RISK_DESTRUCTIVE.value,
                "default_decision": PolicyDecision.BLOCK.value,
                "block_reason": "Direct reading of secret credentials is blocked by default policy",
            },
            "write_fake_ticket": {
                "risk_level": ToolRiskLevel.LOW_IMPACT.value,
                "default_decision": PolicyDecision.DRY_RUN.value,
                "dry_run_mode": True,
            },
            "delete_fake_record": {
                "risk_level": ToolRiskLevel.HIGH_RISK_DESTRUCTIVE.value,
                "default_decision": PolicyDecision.BLOCK.value,
                "block_reason": "Destructive deletion actions are blocked in sandbox mode",
            },
            "delete_record": {
                "risk_level": ToolRiskLevel.HIGH_RISK_DESTRUCTIVE.value,
                "default_decision": PolicyDecision.BLOCK.value,
                "block_reason": "Destructive deletion actions are blocked in sandbox mode",
            },
            "send_fake_message": {
                "risk_level": ToolRiskLevel.HIGH_RISK_DESTRUCTIVE.value,
                "default_decision": PolicyDecision.DRY_RUN.value,
                "dry_run_mode": True,
            },
        }

    def get_tool_risk_level(self, tool_name: str) -> ToolRiskLevel:
        if tool_name in self.rules:
            level_str = self.rules[tool_name].get("risk_level", ToolRiskLevel.HIGH_RISK_DESTRUCTIVE.value)
            try:
                return ToolRiskLevel(level_str)
            except ValueError:
                return ToolRiskLevel.HIGH_RISK_DESTRUCTIVE
        return self.default_risk_level

    def validate_parameters(self, tool_name: str, tool_args: dict[str, Any]) -> tuple[bool, list[str]]:
        violations: list[str] = []
        rule = self.rules.get(tool_name)
        if not rule:
            return True, violations

        param_rules = rule.get("param_rules", {})
        for param_name, spec in param_rules.items():
            value = tool_args.get(param_name)

            # 1. Required check
            if spec.get("required", False) and value is None:
                violations.append(f"Missing required parameter: '{param_name}'")
                continue

            if value is None:
                continue

            str_val = str(value)

            # 2. Max length check
            max_len = spec.get("max_length")
            if max_len is not None and len(str_val) > max_len:
                violations.append(
                    f"Parameter '{param_name}' length ({len(str_val)}) exceeds limit ({max_len})"
                )

            # 3. Regex allow check
            regex_pat = spec.get("regex")
            if regex_pat and not re.match(regex_pat, str_val):
                violations.append(
                    f"Parameter '{param_name}' value '{str_val[:30]}' failed format pattern validation"
                )

            # 4. Deny patterns check
            deny_pats = spec.get("deny_patterns", [])
            for pat in deny_pats:
                if re.search(pat, str_val):
                    violations.append(
                        f"Parameter '{param_name}' contains blocked pattern matching '{pat}'"
                    )

        return (len(violations) == 0, violations)

    def evaluate(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        dry_run_override: bool | None = None,
    ) -> PolicyEvaluationResult:
        risk_level = self.get_tool_risk_level(tool_name)

        # Step 1: Validate parameters
        is_valid_params, param_violations = self.validate_parameters(tool_name, tool_args)
        if not is_valid_params:
            return PolicyEvaluationResult(
                allowed=False,
                decision=PolicyDecision.BLOCK,
                risk_level=risk_level,
                reason=f"Parameter regex or length validation failed for tool '{tool_name}'",
                violations=param_violations,
            )

        # Step 2: Unregistered tool check
        if tool_name not in self.rules:
            return PolicyEvaluationResult(
                allowed=False,
                decision=PolicyDecision.BLOCK,
                risk_level=self.default_risk_level,
                reason=f"Tool '{tool_name}' is not in sandbox allowlist",
                violations=[f"Unregistered tool invocation attempt: '{tool_name}'"],
            )

        rule = self.rules[tool_name]
        default_decision_str = rule.get("default_decision", self.default_decision.value)
        block_reason = rule.get("block_reason", f"Tool '{tool_name}' execution blocked by sandbox policy")
        dry_run_mode = rule.get("dry_run_mode", False)

        # Step 3: Handle Policy Decision
        if default_decision_str == PolicyDecision.BLOCK.value:
            return PolicyEvaluationResult(
                allowed=False,
                decision=PolicyDecision.BLOCK,
                risk_level=risk_level,
                reason=block_reason,
            )

        if dry_run_override is True or dry_run_mode or default_decision_str == PolicyDecision.DRY_RUN.value:
            return PolicyEvaluationResult(
                allowed=True,
                decision=PolicyDecision.DRY_RUN,
                risk_level=risk_level,
                reason=f"Tool '{tool_name}' configured for sandbox dry-run / mock simulation",
            )

        if default_decision_str == PolicyDecision.ALLOW.value:
            return PolicyEvaluationResult(
                allowed=True,
                decision=PolicyDecision.ALLOW,
                risk_level=risk_level,
                reason=f"Tool '{tool_name}' invocation allowed by sandbox policy",
            )

        # Default fallback
        return PolicyEvaluationResult(
            allowed=False,
            decision=PolicyDecision.BLOCK,
            risk_level=risk_level,
            reason=f"Undefined policy decision for tool '{tool_name}'",
        )
