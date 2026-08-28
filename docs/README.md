# OpenAgentSec Documentation Center

**Research baseline (Phase 24.1):** start at [`research/README.md`](research/README.md).  
Claim source of truth: [`research/openagentsec_current_research_state.md`](research/openagentsec_current_research_state.md).  
Older pages in this tree may use pre-freeze language; freeze documents win on conflict.

**Documentation Baseline**: `OpenAgentSec v1.x`  
**Status**: Index (historical reports retained; claims frozen in `docs/research/`)  

---

## 1. Documentation Structure

```text
docs/
├── research/           # Academic Research Papers, Threat Models & Empirical Reports
├── release/            # Developer Quickstart, Demo Workflows & Benchmark Results
├── architecture/       # System Architecture Specifications & Debt Audits
├── governance/         # Enterprise CI/CD Governance & Compliance Charters
├── operations/         # Security Operations, Asset Inventory & Finding Life Cycle
└── legacy_archive/     # Historical Phase Design Notes & Exploration Logs (Phases 1–5)
```

---

## 2. Core Documentation Guide

### 🔬 Research (`docs/research/`) — **read the freeze index first**
- [`research/README.md`](research/README.md): Current research index.
- [`openagentsec_current_research_state.md`](research/openagentsec_current_research_state.md): What was shown and what was not.
- [`validated_results.md`](research/validated_results.md): Final Phase 23 table.
- [`claim_boundaries.md`](research/claim_boundaries.md): Allowed / forbidden claims.
- [`OPENAGENTSEC_V1_RESEARCH_FREEZE.md`](research/OPENAGENTSEC_V1_RESEARCH_FREEZE.md): Freeze statement.

Historical papers (superseded for claims if they conflict):
- [`technical_report.md`](research/technical_report.md): Master Academic Technical Report for OpenAgentSec v1.x.
- [`related_work.md`](research/related_work.md): Ecosystem Taxonomy & Comparative Analysis (vs. PyRIT, garak, HarmBench, Inspect AI).
- [`framework_positioning_review.md`](research/framework_positioning_review.md): Evaluation Philosophy & Comparative Epistemology Review.
- [`real_world_validation_report.md`](research/real_world_validation_report.md): Real-world Agent Runtime Validation (LangGraph, MCP, LangChain, Commercial APIs).
- [`external_review.md`](research/external_review.md): Independent Peer Review & Scientific Stress Test Report.
- [`external_researcher_feedback.md`](research/external_researcher_feedback.md): AI Safety & Security Researcher Evaluation Feedback.
- [`developer_integration_feedback.md`](research/developer_integration_feedback.md): Agent Framework Developer Integration Experience.
- [`research_value_assessment.md`](research/research_value_assessment.md): Strategic Research Value & Scientific Impact Assessment.
- [`artifact_completeness_audit.md`](research/artifact_completeness_audit.md): Scientific Chain-of-Evidence Completeness Audit.
- [`final_claim_review.md`](research/final_claim_review.md): Final Document-by-Document Claim Calibration Review.
- [`post_v1_strategy.md`](research/post_v1_strategy.md): Strategic Maintenance Decision & Post-v1.0 Research Roadmap.
- [`validation_design_review.md`](research/validation_design_review.md): Real-World Runtime Validation Design & Multi-Paradigm Architecture.
- [`langgraph_validation_report.md`](research/langgraph_validation_report.md): LangGraph Reference Runtime Security Validation Report.
- [`langgraph_native_validation_report.md`](research/langgraph_native_validation_report.md): LangGraph Native Runtime Security Validation Report.
- [`llm_agent_validation_report.md`](research/llm_agent_validation_report.md): LLM-Powered Agent Runtime Security Validation Report.
- [`external_llm_validation_report.md`](research/external_llm_validation_report.md): External LLM API Runtime Validation Report.
- [`live_llm_validation_report.md`](research/live_llm_validation_report.md): Live LLM Provider Runtime Security Validation Report.
- [`deepseek_harness_validation_report.md`](research/deepseek_harness_validation_report.md): Real Agent Runtime Validation Report (DeepSeek Harness + DeepSeek V4 Flash).
- [`deepseek_live_validation_report.md`](research/deepseek_live_validation_report.md): Live DeepSeek Harness Runtime Security Validation Report (127.0.0.1:3080).
- [`deepseek_live_violation_validation.md`](research/deepseek_live_violation_validation.md): Controlled Real Runtime Violation Validation Report (DeepSeek Harness).
- [`deepseek_runtime_security_profile.md`](research/deepseek_runtime_security_profile.md): DeepSeek Harness Runtime Security Profile & Boundary Assessment.
- [`deepseek_real_attack_validation.md`](research/deepseek_real_attack_validation.md): Real-World Agent Attack Validation Report (DeepSeek Harness + DeepSeek V4 Flash).
- [`evidence_audit_report.md`](research/evidence_audit_report.md): Evidence Quality & Scientific Evaluation Audit Report (Phase 21.7).
- [`threat_model.md`](research/threat_model.md): Formal 4-Domain Threat Model (Memory, Retrieval, Authorization, Tool).
- [`evaluation_methodology.md`](research/evaluation_methodology.md): 7-Stage Universal Pipeline & Epistemological Axioms.
- [`benchmark_specification.md`](research/benchmark_specification.md): Canonical Benchmark Suite v1.0.0 Specification.
- [`claim_audit_final.md`](research/claim_audit_final.md): Calibrated Research Claims & Academic Precision Register.

### 🚀 Release & Developer Guides (`docs/release/`)
- [`quick_start.md`](release/quick_start.md): 5-Minute Installation, Configuration & CLI Usage.
- [`demo_workflow.md`](release/demo_workflow.md): Interactive Step-by-Step Evaluation Walkthrough.
- [`reproducibility_guide.md`](release/reproducibility_guide.md): Scientific Replication Protocol for External Researchers.
- [`first_time_user_report.md`](release/first_time_user_report.md): First-Time User Experience & Adoption Report.
- [`developer_onboarding_report.md`](release/developer_onboarding_report.md): Benchmark Onboarding & Research Evaluation Report.
- [`adapter_authoring_experience_report.md`](release/adapter_authoring_experience_report.md): Adapter Authoring Experience & Third-Party Extension Report.
- [`open_source_readiness_assessment.md`](release/open_source_readiness_assessment.md): Open Source Adoption & Readiness Assessment.
- [`benchmark_results.md`](release/benchmark_results.md): Official Benchmark Scores & Reproduction Matrix.
- [`contribution_guide.md`](release/contribution_guide.md): Target Adapter & Evaluation Scenario Contribution Guidelines.
- [`v1_release_checklist.md`](release/v1_release_checklist.md): Statutory Release Gate Requirements.

### 🏛️ Architecture & Governance (`docs/architecture/`, `docs/governance/`, `docs/operations/`)
- [`architecture/repository_architecture.md`](architecture/repository_architecture.md): Repository Architecture & Technical Debt Audit.
- [`architecture/architecture_overview.md`](architecture/architecture_overview.md): Subsystem Design & Observation Flow.
- [`governance/enterprise_governance.md`](governance/enterprise_governance.md): Enterprise CI/CD Security Gate & Regression Runner.
- [`operations/operations_guide.md`](operations/operations_guide.md): Finding Lifecycle Management & Posture Dashboard.

### 📦 Historical Archive (`docs/legacy_archive/`)
- Contains archived notes, exploratory playbooks, and design logs from historical phases (Phases 1–5).
- See [`legacy_archive/README.md`](legacy_archive/README.md).
