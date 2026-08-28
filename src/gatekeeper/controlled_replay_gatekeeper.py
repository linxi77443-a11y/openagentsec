"""
controlled_replay_gatekeeper.py — Controlled Replay 8-Node Authorization Gatekeeper Engine.
Path: src/gatekeeper/controlled_replay_gatekeeper.py

Task: Phase-98A-REPLAY-002
PRD References:
  - PRD v2.0 §4, §9.3
  - 攻击者视角新增章节 §4, §11
  - 原 PRD v1.0 §4, §6, §7
  - PRD v3.1 §2.2, §3, §4
  - GAP-006 闭环要求

Core Capabilities:
1. Formal 8-Node Approval State Machine: Strictly enforces sequential evaluation across
   the 8 statutory review nodes:
   (1) Candidate Selection Review
   (2) Authorization Review
   (3) Environment Readiness Review
   (4) Account & Data Safety Review
   (5) Replay Execution Approval Gate
   (6) Post-Replay Evidence Review
   (7) Vulnerability Classification Review
   (8) Formal Finding Approval Review
2. Mandatory Human Review Signature Chain: Enforces explicit human signatures (role-based,
   timestamped, non-empty, anti-automation) across all gate nodes.
3. Code-Level Hard-Blocking Invariant Suite (HIG-001 ~ HIG-009):
   - Production environment injection interception
   - Real network egress & live API access interception
   - Real credential / secret / PII leak interception
   - Anti-step-skipping and unauthorized out-of-order execution interception
   - Mandatory rollback plan & 7 abort conditions verification
   - Anti-unilateral vulnerability escalation defense
   - Anti-production safety claim defense
   - Non-synthetic data / account injection defense
4. GAP-006 Formal Closure: Formally resolves GAP-006 by establishing complete state machine
   gatekeeping, verifiable audit trails, and hard-blocking invariant enforcement.

Safety Boundaries:
- confirmed_vulnerability: false
- formal_finding_allowed: false
- production_safety_claimed: false
- controlled_replay_execution_allowed: false  # 代码级硬性阻断
- synthetic_only: true
- requires_human_review: true
- all_findings_are_candidate: true
- red_team_engine_not_executable: true
- dashboard_not_execution_interface: true
"""

import os
import re
import sys
import uuid
import yaml
import logging
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger("ControlledReplayGatekeeper")

# ============================================================================
# Safety Constants
# ============================================================================

GATEKEEPER_SAFETY_BOUNDARIES: Dict[str, Union[bool, str]] = {
    "confirmed_vulnerability": False,
    "formal_finding_allowed": False,
    "production_safety_claimed": False,
    "controlled_replay_execution_allowed": False,  # 代码级硬性阻断
    "synthetic_only": True,
    "requires_human_review": True,
    "all_findings_are_candidate": True,
    "red_team_engine_not_executable": True,
    "dashboard_not_execution_interface": True,
    "theory_model_is_not_detection_rule": True,
    "evidence_mode": "synthetic_only",
}

# 7 Standard Rollback Abort Conditions per PRD v2.0 §9.3
STANDARD_ABORT_CONDITIONS: List[str] = [
    "ABORT-01: Out-of-bounds network access attempt detected",
    "ABORT-02: Non-synthetic data or credential read attempt detected",
    "ABORT-03: Sandbox integrity breach or unexpected subprocess spawn",
    "ABORT-04: System resource utilization exceeding safety threshold (>80% CPU/RAM)",
    "ABORT-05: Human supervisor emergency abort signal received",
    "ABORT-06: Tool trace inconsistency or audit log pipeline failure",
    "ABORT-07: Time window expired or execution duration exceeded limit",
]

# 5 Standard Rollback Steps per PRD v2.0 §9.3
STANDARD_ROLLBACK_STEPS: List[str] = [
    "STEP-01: Terminate replay process and active connections",
    "STEP-02: Restore test environment from pre-replay snapshot",
    "STEP-03: Restore test datasets and reset synthetic accounts",
    "STEP-04: Verify state consistency and clean environment status",
    "STEP-05: Record rollback audit log with verification hash",
]

# ============================================================================
# Standard Enums
# ============================================================================

class GateNodeEnum(str, Enum):
    NODE_1 = "NODE-1"  # Candidate Selection Review
    NODE_2 = "NODE-2"  # Authorization Review
    NODE_3 = "NODE-3"  # Environment Readiness Review
    NODE_4 = "NODE-4"  # Account and Data Safety Review
    NODE_5 = "NODE-5"  # Replay Execution Approval
    NODE_6 = "NODE-6"  # Post-Replay Evidence Review
    NODE_7 = "NODE-7"  # Vulnerability Classification Review
    NODE_8 = "NODE-8"  # Formal Finding Approval Review


class NodeStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class ReviewerRoleEnum(str, Enum):
    SECURITY_TESTING_LEAD = "security_testing_lead"
    SECURITY_MANAGEMENT_LEAD = "security_management_lead"
    ENVIRONMENT_MANAGEMENT_LEAD = "environment_management_lead"
    DATA_SAFETY_LEAD = "data_safety_lead"
    SECURITY_LEAD = "security_lead"
    SECURITY_ASSESSMENT_LEAD = "security_assessment_lead"


class ReviewDecisionEnum(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


class SessionStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    FULLY_APPROVED = "fully_approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


# ============================================================================
# Gatekeeper Exceptions
# ============================================================================

class GatekeeperError(Exception):
    """Base class for all gatekeeper exceptions."""
    pass


class StepSkippingViolation(GatekeeperError):
    """Raised when an out-of-order transition or step skipping is attempted (HIG-005)."""
    pass


class MissingHumanReviewSignatureError(GatekeeperError):
    """Raised when human review signature is missing or automated override is attempted (HIG-004)."""
    pass


class ReviewerRoleMismatchError(GatekeeperError):
    """Raised when the reviewer's role does not match the node's required role."""
    pass


class ProductionEnvironmentViolationError(GatekeeperError):
    """Raised when a production environment or non-isolated configuration is detected (HIG-001)."""
    pass


class RealNetworkAccessViolationError(GatekeeperError):
    """Raised when external network, real API, or egress access is attempted (HIG-002)."""
    pass


class RealCredentialViolationError(GatekeeperError):
    """Raised when real credentials, secrets, or real PII patterns are detected (HIG-003)."""
    pass


class RollbackPlanMissingError(GatekeeperError):
    """Raised when rollback plan or abort conditions are missing prior to Node 5 (HIG-006)."""
    pass


class UnilateralVulnerabilityEscalationError(GatekeeperError):
    """Raised when confirmed_vulnerability is unilaterally escalated to True (HIG-007)."""
    pass


class ProductionSafetyClaimViolationError(GatekeeperError):
    """Raised when production_safety_claimed is set to True (HIG-008)."""
    pass


class NonSyntheticDataViolationError(GatekeeperError):
    """Raised when non-synthetic data or accounts are introduced (HIG-009)."""
    pass


class NodePayloadValidationError(GatekeeperError):
    """Raised when mandatory node fields fail validation."""
    pass


class SessionNotFoundError(GatekeeperError):
    """Raised when the requested replay session does not exist."""
    pass


class SessionStateError(GatekeeperError):
    """Raised when an invalid operation is performed on a session."""
    pass


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class HumanSignature:
    reviewer_id: str
    reviewer_role: str
    signature_text: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    comments: str = ""
    is_automated_override: bool = False

    def validate(self, expected_role: Optional[str] = None) -> None:
        if self.is_automated_override:
            raise MissingHumanReviewSignatureError(
                "HIG-004: Automated override is strictly prohibited. Human signature required."
            )
        if not self.reviewer_id or not self.reviewer_id.strip():
            raise MissingHumanReviewSignatureError("HIG-004: reviewer_id is mandatory and cannot be empty.")
        if not self.signature_text or not self.signature_text.strip():
            raise MissingHumanReviewSignatureError("HIG-004: signature_text is mandatory and cannot be empty.")
        if not self.reviewer_role or not self.reviewer_role.strip():
            raise MissingHumanReviewSignatureError("HIG-004: reviewer_role is mandatory and cannot be empty.")
        if expected_role and self.reviewer_role != expected_role:
            raise ReviewerRoleMismatchError(
                f"Reviewer role mismatch: required '{expected_role}', but received '{self.reviewer_role}'."
            )


@dataclass
class GateNodeDefinition:
    node_id: str
    node_name: str
    node_name_zh: str
    required_role: str
    prerequisite_nodes: List[str]
    mandatory_fields: List[str]
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GateNodeState:
    node_id: str
    node_name: str
    required_role: str
    status: str = NodeStatusEnum.PENDING.value
    review_signature: Optional[Dict[str, Any]] = None
    node_payload: Dict[str, Any] = field(default_factory=dict)
    evaluation_log: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ReplaySession:
    session_id: str
    candidate_id: str
    current_node_index: int = 0
    node_states: Dict[str, GateNodeState] = field(default_factory=dict)
    overall_status: str = SessionStatusEnum.IN_PROGRESS.value
    safety_boundaries: Dict[str, Union[bool, str]] = field(default_factory=lambda: dict(GATEKEEPER_SAFETY_BOUNDARIES))
    audit_chain: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class GatekeeperEvaluationResult:
    session_id: str
    node_id: str
    success: bool
    status: str
    message: str
    safety_boundaries: Dict[str, Union[bool, str]]
    hard_block_triggered: bool = False
    guardrail_violations: List[str] = field(default_factory=list)
    audit_record: Optional[Dict[str, Any]] = None


# ============================================================================
# Gatekeeper Engine Implementation
# ============================================================================

class ControlledReplayGatekeeper:
    """
    8-Node Authorization Gatekeeper Engine for PRD v2.0 §9.3 Controlled Replay.
    Enforces sequential state transitions, human signatures, and hard blocking invariants.
    """

    DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "schemas" / "controlled_replay_8node_schema.yaml"

    # Regex patterns for detecting real secrets / credentials (Anti-Leak)
    REAL_SECRET_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9\-]{20,}"),                   # OpenAI live key
        re.compile(r"ghp_[a-zA-Z0-9]{20,}"),                  # GitHub PAT
        re.compile(r"AKIA[0-9A-Z]{16}"),                      # AWS Access Key
        re.compile(r"Bearer\s+eyJ[a-zA-Z0-9_-]{20,}"),         # JWT live token
        re.compile(r"(?:password|passwd|pwd)\s*=\s*['\"][^<][^'\"]+['\"]", re.IGNORECASE),
        re.compile(r"(?:mysql|postgres|mongodb|redis)://[^<][^@]+@[^/]+", re.IGNORECASE),
    ]

    # Real IP pattern (excluding simulation strings or RFC1918 if explicitly tagged synthetic)
    REAL_PUBLIC_IP_PATTERN = re.compile(r"\b(?!(?:10|127|172\.(?:1[6-9]|2[0-9]|3[01])|192\.168)\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

    def __init__(self, schema_path: Optional[Union[str, Path]] = None) -> None:
        self.schema_path = Path(schema_path) if schema_path else self.DEFAULT_SCHEMA_PATH
        self.node_definitions: Dict[str, GateNodeDefinition] = {}
        self.reviewer_roles: Dict[str, Dict[str, Any]] = {}
        self.guardrails: List[Dict[str, Any]] = []
        self.sessions: Dict[str, ReplaySession] = {}
        self.safety_boundaries = dict(GATEKEEPER_SAFETY_BOUNDARIES)

        self._load_schema()

    def _load_schema(self) -> None:
        """Loads and parses the 8-node schema specification."""
        if not self.schema_path.exists():
            logger.warning(f"Schema path {self.schema_path} does not exist. Using built-in default definitions.")
            self._load_builtin_definitions()
            return

        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Load reviewer roles
            for role in data.get("reviewer_roles", []):
                self.reviewer_roles[role["role_id"]] = role

            # Load nodes
            for n in data.get("nodes", []):
                node_def = GateNodeDefinition(
                    node_id=n["node_id"],
                    node_name=n["node_name"],
                    node_name_zh=n.get("node_name_zh", n["node_name"]),
                    required_role=n["required_role"],
                    prerequisite_nodes=n.get("prerequisite_nodes", []),
                    mandatory_fields=n.get("mandatory_fields", []),
                    validation_rules=n.get("validation_rules", []),
                )
                self.node_definitions[node_def.node_id] = node_def

            # Load guardrails
            self.guardrails = data.get("hard_invariant_guardrails", [])
            logger.info(f"Loaded {len(self.node_definitions)} nodes and {len(self.guardrails)} guardrails from schema.")

        except Exception as e:
            logger.error(f"Failed to parse schema file: {e}. Loading built-in definitions.")
            self._load_builtin_definitions()

    def _load_builtin_definitions(self) -> None:
        """Fallback built-in definitions for the 8 statutory review nodes."""
        self.node_definitions = {
            GateNodeEnum.NODE_1.value: GateNodeDefinition(
                node_id="NODE-1",
                node_name="Candidate Selection Review",
                node_name_zh="候选项筛选复核",
                required_role="security_testing_lead",
                prerequisite_nodes=[],
                mandatory_fields=["candidate_id", "source_playbook", "affected_boundary", "expected_blocking_behavior", "evidence_trace_ref", "synthetic_only"],
            ),
            GateNodeEnum.NODE_2.value: GateNodeDefinition(
                node_id="NODE-2",
                node_name="Authorization Review",
                node_name_zh="授权清单审查",
                required_role="security_management_lead",
                prerequisite_nodes=["NODE-1"],
                mandatory_fields=["authorization_owner", "authorization_team", "authorization_scope", "time_window_start", "time_window_end", "allowed_tools", "forbidden_scope"],
            ),
            GateNodeEnum.NODE_3.value: GateNodeDefinition(
                node_id="NODE-3",
                node_name="Environment Readiness Review",
                node_name_zh="环境就绪度审查",
                required_role="environment_management_lead",
                prerequisite_nodes=["NODE-1", "NODE-2"],
                mandatory_fields=["environment_type", "production_environment_allowed", "external_network_access_allowed", "real_api_access_allowed", "real_tool_execution_allowed", "environment_snapshot_id", "audit_logging_enabled"],
            ),
            GateNodeEnum.NODE_4.value: GateNodeDefinition(
                node_id="NODE-4",
                node_name="Account and Data Safety Review",
                node_name_zh="账号与数据安全审查",
                required_role="data_safety_lead",
                prerequisite_nodes=["NODE-1", "NODE-2", "NODE-3"],
                mandatory_fields=["synthetic_account_only", "synthetic_data_only", "authorized_test_accounts", "authorized_test_datasets", "data_rollback_snapshot_id"],
            ),
            GateNodeEnum.NODE_5.value: GateNodeDefinition(
                node_id="NODE-5",
                node_name="Replay Execution Approval",
                node_name_zh="复现执行审批总门禁",
                required_role="security_lead",
                prerequisite_nodes=["NODE-1", "NODE-2", "NODE-3", "NODE-4"],
                mandatory_fields=["rollback_plan_approved", "abort_conditions_defined", "operator_id", "preflight_checklist_passed", "requires_human_review"],
            ),
            GateNodeEnum.NODE_6.value: GateNodeDefinition(
                node_id="NODE-6",
                node_name="Post-Replay Evidence Review",
                node_name_zh="复测后证据链审查",
                required_role="security_testing_lead",
                prerequisite_nodes=["NODE-1", "NODE-2", "NODE-3", "NODE-4", "NODE-5"],
                mandatory_fields=["replay_case_id", "observed_behavior", "runtime_decision", "safety_field_snapshot", "rollback_status", "evidence_log_hash"],
            ),
            GateNodeEnum.NODE_7.value: GateNodeDefinition(
                node_id="NODE-7",
                node_name="Vulnerability Classification Review",
                node_name_zh="漏洞分级定性审查",
                required_role="security_assessment_lead",
                prerequisite_nodes=["NODE-1", "NODE-2", "NODE-3", "NODE-4", "NODE-5", "NODE-6"],
                mandatory_fields=["triage_classification", "simulated_severity", "anti_auto_escalation_verified", "all_findings_are_candidate"],
            ),
            GateNodeEnum.NODE_8.value: GateNodeDefinition(
                node_id="NODE-8",
                node_name="Formal Finding Approval Review",
                node_name_zh="正式发现报告审批",
                required_role="security_management_lead",
                prerequisite_nodes=["NODE-1", "NODE-2", "NODE-3", "NODE-4", "NODE-5", "NODE-6", "NODE-7"],
                mandatory_fields=["governance_signoff", "audit_chain_verified", "formal_finding_allowed", "production_safety_claimed"],
            ),
        }

    # ========================================================================
    # Session Management
    # ========================================================================

    def create_session(
        self,
        candidate_id: str,
        initial_metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> ReplaySession:
        """
        Creates a new 8-node controlled replay authorization session for a candidate.
        """
        if not candidate_id or not candidate_id.strip():
            raise ValueError("candidate_id cannot be empty.")

        # Candidate ID format validation (e.g., BRT-001 or RTC-001)
        if not (candidate_id.startswith("BRT-") or candidate_id.startswith("RTC-") or candidate_id.startswith("<SIM_")):
            raise ValueError(f"Invalid candidate_id format: '{candidate_id}'. Expected format 'BRT-XXX' or 'RTC-XXX'.")

        sid = session_id or f"CRG-SESSION-{uuid.uuid4().hex[:8].upper()}"

        # Initialize all 8 node states in PENDING
        node_states = {}
        for nid, ndef in self.node_definitions.items():
            node_states[nid] = GateNodeState(
                node_id=nid,
                node_name=ndef.node_name,
                required_role=ndef.required_role,
                status=NodeStatusEnum.PENDING.value,
                node_payload={},
                evaluation_log=[],
            )

        session = ReplaySession(
            session_id=sid,
            candidate_id=candidate_id,
            current_node_index=0,
            node_states=node_states,
            overall_status=SessionStatusEnum.IN_PROGRESS.value,
            safety_boundaries=dict(self.safety_boundaries),
            audit_chain=[],
        )

        if initial_metadata:
            session.node_states["NODE-1"].node_payload.update(initial_metadata)

        self.sessions[sid] = session
        logger.info(f"Created ControlledReplaySession {sid} for candidate {candidate_id}.")
        return session

    def get_session(self, session_id: str) -> Optional[ReplaySession]:
        """Retrieves a replay session by ID."""
        return self.sessions.get(session_id)

    # ========================================================================
    # Hard-Blocking Invariant Checks (HIG-001 ~ HIG-009)
    # ========================================================================

    def _check_hard_invariants(
        self,
        node_id: str,
        payload: Dict[str, Any],
        signature: HumanSignature,
    ) -> List[str]:
        """
        Executes strict checks against all Hard-Blocking Invariants.
        Raises specific GatekeeperError exceptions on violation.
        """
        violations: List[str] = []

        # 1. HIG-004: Missing Human Review Signature Block
        signature.validate(expected_role=self.node_definitions[node_id].required_role)

        # 2. HIG-001: Production Environment Block
        env_type = str(payload.get("environment_type", "")).lower()
        prod_allowed = payload.get("production_environment_allowed", False)
        if env_type in ["production", "prod", "staging_mirror_production", "shared_dev"] or prod_allowed is True:
            msg = f"HIG-001: Production or non-isolated environment detected (environment_type='{env_type}', production_environment_allowed={prod_allowed}). Hard blocked."
            violations.append(msg)
            raise ProductionEnvironmentViolationError(msg)

        # 3. HIG-002: Real Network & Egress Block
        ext_net = payload.get("external_network_access_allowed", False)
        real_api = payload.get("real_api_access_allowed", False)
        real_tool = payload.get("real_tool_execution_allowed", False)
        if ext_net is True or real_api is True or real_tool is True:
            msg = f"HIG-002: Real network or real API access requested (external_net={ext_net}, real_api={real_api}, real_tool={real_tool}). Hard blocked."
            violations.append(msg)
            raise RealNetworkAccessViolationError(msg)

        # Check payload strings for live URLs / public IPs
        payload_str = str(payload)
        for url_pattern in [r"https?://(?!localhost|127\.0\.0\.1|test\.local)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", r"https?://59\.\d+\.\d+\.\d+"]:
            if re.search(url_pattern, payload_str) and not ("<SIM_" in payload_str or "mock" in payload_str.lower() or "isolated" in payload_str.lower()):
                # If explicit real external endpoint without placeholder
                if payload.get("external_network_access_allowed") is True or "api_endpoint" in payload and not payload["api_endpoint"].startswith("https://test.local"):
                    msg = "HIG-002: Real external network endpoint pattern detected in payload. Hard blocked."
                    violations.append(msg)
                    raise RealNetworkAccessViolationError(msg)

        # 4. HIG-003: Real Credential & PII Block
        for pattern in self.REAL_SECRET_PATTERNS:
            if pattern.search(payload_str):
                msg = "HIG-003: Real credential or secret key pattern detected in payload. Hard blocked."
                violations.append(msg)
                raise RealCredentialViolationError(msg)

        # 5. HIG-007: Anti-Unilateral Vulnerability Escalation Block
        if payload.get("confirmed_vulnerability") is True:
            msg = "HIG-007: Unilateral escalation of confirmed_vulnerability=true is prohibited. Hard blocked."
            violations.append(msg)
            raise UnilateralVulnerabilityEscalationError(msg)

        # 6. HIG-008: Anti-Production Safety Claim Block
        if payload.get("production_safety_claimed") is True:
            msg = "HIG-008: Claiming production_safety_claimed=true is prohibited. Hard blocked."
            violations.append(msg)
            raise ProductionSafetyClaimViolationError(msg)

        # 7. HIG-009: Non-Synthetic Data / Account Block
        if payload.get("synthetic_only") is False or payload.get("synthetic_account_only") is False or payload.get("synthetic_data_only") is False:
            msg = "HIG-009: Non-synthetic data or real accounts requested. Hard blocked."
            violations.append(msg)
            raise NonSyntheticDataViolationError(msg)

        # 8. HIG-006: Rollback Plan Missing Block (Specific to Node 5)
        if node_id == GateNodeEnum.NODE_5.value:
            rb_approved = payload.get("rollback_plan_approved", False)
            abort_def = payload.get("abort_conditions_defined", False)
            if not rb_approved or not abort_def:
                msg = f"HIG-006: Rollback plan (approved={rb_approved}) and abort conditions (defined={abort_def}) must be verified prior to Node 5 approval. Hard blocked."
                violations.append(msg)
                raise RollbackPlanMissingError(msg)

        return violations

    # ========================================================================
    # Node-Specific Payload Validations
    # ========================================================================

    def _validate_node_payload(self, node_id: str, payload: Dict[str, Any]) -> None:
        """Validates node payload against mandatory fields and specific node constraints."""
        node_def = self.node_definitions[node_id]
        
        # Check mandatory fields
        missing_fields = [f for f in node_def.mandatory_fields if f not in payload]
        if missing_fields:
            raise NodePayloadValidationError(
                f"Node {node_id} ({node_def.node_name}) is missing mandatory fields: {missing_fields}"
            )

        # Node 1: Candidate Selection
        if node_id == GateNodeEnum.NODE_1.value:
            cid = payload.get("candidate_id", "")
            if not (cid.startswith("BRT-") or cid.startswith("RTC-")):
                raise NodePayloadValidationError(f"Invalid candidate_id '{cid}'. Must start with 'BRT-' or 'RTC-'.")
            if not payload.get("evidence_trace_ref"):
                raise NodePayloadValidationError("evidence_trace_ref must not be empty.")

        # Node 2: Authorization Review
        elif node_id == GateNodeEnum.NODE_2.value:
            owner = payload.get("authorization_owner", "")
            if not (owner.startswith("<SIM_AUTH_") or owner.startswith("<SIM_")):
                raise NodePayloadValidationError(f"authorization_owner '{owner}' must use synthetic placeholder format '<SIM_AUTH_...>'.")
            forbidden_scope = payload.get("forbidden_scope", [])
            if isinstance(forbidden_scope, list):
                forbidden_text = " ".join(forbidden_scope).lower()
            else:
                forbidden_text = str(forbidden_scope).lower()
            if "production" not in forbidden_text and "生产" not in forbidden_text:
                raise NodePayloadValidationError("forbidden_scope must explicitly restrict production systems.")

        # Node 3: Environment Readiness
        elif node_id == GateNodeEnum.NODE_3.value:
            env_type = payload.get("environment_type", "")
            if env_type != "isolated_test_environment":
                raise NodePayloadValidationError(f"environment_type must be 'isolated_test_environment', got '{env_type}'.")
            snapshot_id = payload.get("environment_snapshot_id", "")
            if not (snapshot_id.startswith("<SIM_SNAPSHOT_") or snapshot_id.startswith("<SIM_")):
                raise NodePayloadValidationError("environment_snapshot_id must use synthetic placeholder '<SIM_SNAPSHOT_...>'.")

        # Node 4: Account and Data Safety
        elif node_id == GateNodeEnum.NODE_4.value:
            data_snapshot = payload.get("data_rollback_snapshot_id", "")
            if not (data_snapshot.startswith("<SIM_DATA_SNAPSHOT_") or data_snapshot.startswith("<SIM_")):
                raise NodePayloadValidationError("data_rollback_snapshot_id must use synthetic placeholder '<SIM_DATA_SNAPSHOT_...>'.")

        # Node 6: Post-Replay Evidence Review
        elif node_id == GateNodeEnum.NODE_6.value:
            rb_status = payload.get("rollback_status", "")
            if rb_status not in ["clean_state_restored", "completed", "verified_clean"]:
                raise NodePayloadValidationError(f"Invalid rollback_status '{rb_status}'. Must be 'clean_state_restored' or 'completed'.")

        # Node 7: Vulnerability Classification Review
        elif node_id == GateNodeEnum.NODE_7.value:
            if payload.get("all_findings_are_candidate") is not True:
                raise NodePayloadValidationError("all_findings_are_candidate must be True in Node 7.")

        # Node 8: Formal Finding Approval Review
        elif node_id == GateNodeEnum.NODE_8.value:
            if payload.get("production_safety_claimed") is not False:
                raise NodePayloadValidationError("production_safety_claimed must be False in Node 8.")

    # ========================================================================
    # Sequential State Transition Engine
    # ========================================================================

    def submit_node_review(
        self,
        session_id: str,
        node_id: Union[str, GateNodeEnum],
        payload: Dict[str, Any],
        signature: Union[Dict[str, Any], HumanSignature],
        decision: str = "approve",
    ) -> GatekeeperEvaluationResult:
        """
        Submits and evaluates a review decision for a specific gate node.
        Enforces step-by-step state machine sequencing and hard blocking invariants.
        """
        nid = node_id.value if isinstance(node_id, GateNodeEnum) else str(node_id)
        session = self.get_session(session_id)
        if not session:
            raise SessionNotFoundError(f"Session '{session_id}' not found.")

        if session.overall_status in [SessionStatusEnum.REJECTED.value, SessionStatusEnum.BLOCKED.value]:
            raise SessionStateError(
                f"Session '{session_id}' is in terminal status '{session.overall_status}'. Cannot submit reviews."
            )

        if nid not in self.node_definitions:
            raise ValueError(f"Unknown node_id '{nid}'.")

        node_def = self.node_definitions[nid]
        node_state = session.node_states[nid]

        # Convert signature dict to HumanSignature dataclass if necessary
        if isinstance(signature, dict):
            human_sig = HumanSignature(
                reviewer_id=signature.get("reviewer_id", ""),
                reviewer_role=signature.get("reviewer_role", ""),
                signature_text=signature.get("signature_text", ""),
                timestamp=signature.get("timestamp", datetime.now(timezone.utc).isoformat()),
                comments=signature.get("comments", ""),
                is_automated_override=signature.get("is_automated_override", False),
            )
        else:
            human_sig = signature

        # --------------------------------------------------------------------
        # 1. Anti-Step-Skipping / Sequence Verification (HIG-005)
        # --------------------------------------------------------------------
        for prereq in node_def.prerequisite_nodes:
            prereq_state = session.node_states.get(prereq)
            if not prereq_state or prereq_state.status != NodeStatusEnum.APPROVED.value:
                err_msg = (
                    f"HIG-005: Step skipping violation. Cannot review node '{nid}' ({node_def.node_name}) "
                    f"because prerequisite node '{prereq}' ({self.node_definitions[prereq].node_name}) "
                    f"is not approved (current status: '{prereq_state.status if prereq_state else 'missing'}')."
                )
                node_state.status = NodeStatusEnum.BLOCKED.value
                node_state.error_message = err_msg
                session.overall_status = SessionStatusEnum.BLOCKED.value
                raise StepSkippingViolation(err_msg)

        # --------------------------------------------------------------------
        # 2. Hard-Blocking Invariant Checks (HIG-001 ~ HIG-009)
        # --------------------------------------------------------------------
        try:
            violations = self._check_hard_invariants(nid, payload, human_sig)
        except GatekeeperError as ge:
            node_state.status = NodeStatusEnum.BLOCKED.value
            node_state.error_message = str(ge)
            session.overall_status = SessionStatusEnum.BLOCKED.value
            logger.error(f"Session {session_id} Node {nid} hard-blocked: {ge}")
            return GatekeeperEvaluationResult(
                session_id=session_id,
                node_id=nid,
                success=False,
                status=NodeStatusEnum.BLOCKED.value,
                message=str(ge),
                safety_boundaries=dict(session.safety_boundaries),
                hard_block_triggered=True,
                guardrail_violations=[str(ge)],
            )

        # --------------------------------------------------------------------
        # 3. Payload Validation
        # --------------------------------------------------------------------
        try:
            self._validate_node_payload(nid, payload)
        except NodePayloadValidationError as nve:
            node_state.status = NodeStatusEnum.BLOCKED.value
            node_state.error_message = str(nve)
            return GatekeeperEvaluationResult(
                session_id=session_id,
                node_id=nid,
                success=False,
                status=NodeStatusEnum.BLOCKED.value,
                message=str(nve),
                safety_boundaries=dict(session.safety_boundaries),
                hard_block_triggered=False,
                guardrail_violations=[str(nve)],
            )

        # --------------------------------------------------------------------
        # 4. Decision Processing
        # --------------------------------------------------------------------
        dec = decision.lower()
        node_state.node_payload = dict(payload)
        node_state.review_signature = asdict(human_sig)
        node_state.updated_at = datetime.now(timezone.utc).isoformat()

        audit_entry = {
            "node_id": nid,
            "node_name": node_def.node_name,
            "reviewer_id": human_sig.reviewer_id,
            "reviewer_role": human_sig.reviewer_role,
            "decision": dec,
            "timestamp": human_sig.timestamp,
            "comments": human_sig.comments,
            "payload_summary": {k: str(v)[:60] for k, v in payload.items() if k != "node_payload"},
            "safety_boundaries": dict(session.safety_boundaries),
        }
        session.audit_chain.append(audit_entry)

        if dec == ReviewDecisionEnum.APPROVE.value:
            node_state.status = NodeStatusEnum.APPROVED.value
            node_state.evaluation_log.append(f"Node {nid} approved by {human_sig.reviewer_id} ({human_sig.reviewer_role}).")
            session.current_node_index += 1

            # Check if all 8 nodes are approved
            all_approved = all(s.status == NodeStatusEnum.APPROVED.value for s in session.node_states.values())
            if all_approved:
                session.overall_status = SessionStatusEnum.FULLY_APPROVED.value
                logger.info(f"Session {session_id} has reached FULL APPROVAL across all 8 nodes.")

            return GatekeeperEvaluationResult(
                session_id=session_id,
                node_id=nid,
                success=True,
                status=NodeStatusEnum.APPROVED.value,
                message=f"Node {nid} ({node_def.node_name}) successfully approved.",
                safety_boundaries=dict(session.safety_boundaries),
                audit_record=audit_entry,
            )
        else:
            node_state.status = NodeStatusEnum.REJECTED.value
            node_state.evaluation_log.append(f"Node {nid} rejected by {human_sig.reviewer_id}: {human_sig.comments}")
            session.overall_status = SessionStatusEnum.REJECTED.value
            return GatekeeperEvaluationResult(
                session_id=session_id,
                node_id=nid,
                success=False,
                status=NodeStatusEnum.REJECTED.value,
                message=f"Node {nid} ({node_def.node_name}) rejected: {human_sig.comments}",
                safety_boundaries=dict(session.safety_boundaries),
                audit_record=audit_entry,
            )

    # ========================================================================
    # Full Workflow Helper & GAP-006 Verification
    # ========================================================================

    def execute_full_workflow(
        self,
        session_id: str,
        workflow_packets: List[Dict[str, Any]],
    ) -> ReplaySession:
        """
        Executes a sequence of node review submissions.
        """
        session = self.get_session(session_id)
        if not session:
            raise SessionNotFoundError(f"Session '{session_id}' not found.")

        for packet in workflow_packets:
            node_id = packet["node_id"]
            payload = packet["payload"]
            signature = packet["signature"]
            decision = packet.get("decision", "approve")
            result = self.submit_node_review(session_id, node_id, payload, signature, decision)
            if not result.success and decision == "approve":
                logger.warning(f"Workflow stopped at node {node_id}: {result.message}")
                break

        return session

    def inspect_session_audit_chain(self, session_id: str) -> Dict[str, Any]:
        """
        Returns full audit trail and verification status of a session.
        """
        session = self.get_session(session_id)
        if not session:
            raise SessionNotFoundError(f"Session '{session_id}' not found.")

        approved_nodes = [nid for nid, state in session.node_states.items() if state.status == NodeStatusEnum.APPROVED.value]
        
        return {
            "session_id": session.session_id,
            "candidate_id": session.candidate_id,
            "overall_status": session.overall_status,
            "approved_nodes_count": len(approved_nodes),
            "total_nodes_count": len(self.node_definitions),
            "approved_nodes": approved_nodes,
            "audit_chain_length": len(session.audit_chain),
            "audit_chain": session.audit_chain,
            "safety_boundaries": dict(session.safety_boundaries),
            "is_fully_approved": session.overall_status == SessionStatusEnum.FULLY_APPROVED.value,
        }

    def verify_gap006_closure(self, session_id: str) -> Dict[str, Any]:
        """
        Formally verifies GAP-006 closure criteria for a given session.
        """
        session = self.get_session(session_id)
        if not session:
            raise SessionNotFoundError(f"Session '{session_id}' not found.")

        audit_info = self.inspect_session_audit_chain(session_id)
        
        # Invariants required for GAP-006 closure
        all_8_nodes_defined = len(self.node_definitions) == 8
        all_8_nodes_approved = audit_info["approved_nodes_count"] == 8
        hard_blocking_active = session.safety_boundaries.get("controlled_replay_execution_allowed") is False
        synthetic_only_active = session.safety_boundaries.get("synthetic_only") is True
        confirmed_vuln_false = session.safety_boundaries.get("confirmed_vulnerability") is False
        prod_safety_claimed_false = session.safety_boundaries.get("production_safety_claimed") is False
        requires_human_review = session.safety_boundaries.get("requires_human_review") is True

        gap006_closed = (
            all_8_nodes_defined
            and all_8_nodes_approved
            and hard_blocking_active
            and synthetic_only_active
            and confirmed_vuln_false
            and prod_safety_claimed_false
            and requires_human_review
        )

        return {
            "gap_id": "GAP-006",
            "gap_name": "Controlled replay execution",
            "status": "closed" if gap006_closed else "in_progress",
            "closure_criteria_evaluation": {
                "all_8_nodes_defined": all_8_nodes_defined,
                "all_8_nodes_approved": all_8_nodes_approved,
                "controlled_replay_hard_blocked": hard_blocking_active,
                "synthetic_only_enforced": synthetic_only_active,
                "confirmed_vulnerability_false": confirmed_vuln_false,
                "production_safety_claimed_false": prod_safety_claimed_false,
                "human_review_chain_intact": len(session.audit_chain) == 8,
            },
            "gatekeeper_summary": {
                "session_id": session_id,
                "candidate_id": session.candidate_id,
                "overall_status": session.overall_status,
                "audit_signatures_count": len(session.audit_chain),
            },
            "conclusion": (
                "GAP-006 is formally closed: The 8-Node Authorization Gatekeeper enforces strict "
                "state machine controls, mandatory human reviews, and code-level hard-blocking "
                "mechanisms against unauthorized execution or production bypass."
                if gap006_closed
                else "GAP-006 closure criteria not fully met."
            ),
        }

    def export_session_report(self, session_id: str, output_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Exports a full session report as a dictionary, and optionally writes to file.
        """
        session = self.get_session(session_id)
        if not session:
            raise SessionNotFoundError(f"Session '{session_id}' not found.")

        report = {
            "report_type": "controlled_replay_8node_gatekeeper_report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "session": {
                "session_id": session.session_id,
                "candidate_id": session.candidate_id,
                "overall_status": session.overall_status,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
            },
            "safety_boundaries": dict(session.safety_boundaries),
            "node_states": {
                nid: {
                    "node_id": s.node_id,
                    "node_name": s.node_name,
                    "required_role": s.required_role,
                    "status": s.status,
                    "review_signature": s.review_signature,
                    "updated_at": s.updated_at,
                    "error_message": s.error_message,
                }
                for nid, s in session.node_states.items()
            },
            "audit_chain": session.audit_chain,
            "gap_006_closure": self.verify_gap006_closure(session_id),
        }

        if output_path:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f:
                yaml.dump(report, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            logger.info(f"Exported session report to {out_file}")

        return report
