# Changelog

All notable changes to the **OpenAgentSec** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-28

### Research freeze
- OpenAgentSec v1.x research baseline frozen (Phase 24.1).
- Trust Chain, Phase 23 validated experimental conclusions, claim boundaries, and testing-reality classification are the public source of truth.
- Positioning: **research framework**, not a production security scanner.

## [1.0.0-rc.1] - 2026-08-23

### Added
- **Real-World Runtime Ecosystem Validation (Phase 13.R3)**:
  - Reference adapters for LangGraph (`StateGraph` checkpointers), Model Context Protocol (`MCP Gateway`), LangChain (`CallbackHandler` RAG), Commercial APIs (OpenAI, Anthropic Claude, DeepSeek blackbox endpoints), and Multi-Agent collaborative topologies.
  - 16 real-world integration validation tests in `tests/integration/real_world/` achieving 100% pass rate.
- **Research Consolidation & Technical Report (Phase 14)**:
  - Master Research Technical Report (`docs/research/technical_report.md`).
  - Ecosystem Taxonomy & Related Work Matrix (`docs/research/related_work.md`).
  - Repository Architecture & Technical Debt Audit (`docs/architecture/repository_architecture.md`).
- **External Peer Review & Stress Testing (Phase 15)**:
  - Multi-perspective scientific review simulating AI Safety, Security, Open Source, and Enterprise personas (`docs/research/external_review.md`).
  - Strict claim calibration eliminating uncalibrated marketing terminology across all active documentation.
- **Repository Cleanliness & Release Candidate Governance (Phase 16)**:
  - Canonical PRD established as `PRD/PRD_v4.0.2_final.md`, historical PRDs organized in `PRD/archive/`.
  - Structured documentation tree (`docs/research/`, `docs/release/`, `docs/architecture/`, `docs/legacy_archive/`).
  - Governed empirical experiment catalog (`experiments/benchmark/`, `experiments/empirical/`, `experiments/real_world/`, `experiments/archived/`).
- **Open Source Readiness & Community Metadata (Phase 17)**:
  - Added `SECURITY.md` for responsible vulnerability disclosure.
  - Added `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1).
  - Comprehensive `CONTRIBUTING.md` guide and contributor experience report (`docs/release/contributor_experience_report.md`).
  - Fresh clone validation report (`docs/release/fresh_clone_validation.md`).
  - Repository size audit (`docs/architecture/repository_size_audit.md`).
  - Complete v1.0 release checklist (`docs/release/v1_release_checklist.md`).

---

## [1.0.0-beta.1] - 2026-08-20

### Added
- **Evaluation Foundation (Phase 6)**:
  - Policy Enforcement Point (PEP) and Deterministic Boundary Oracle (`DeterministicToolBoundaryOracle`).
  - Evidence Model with signed physical execution receipts (`EvidenceItem`, `tool_execution_log`).
  - Statutory 5-run Zero-Variance Reproduction Aggregator (`ReproductionAggregator`).
  - Delta State Evaluation formulation ($\Delta \sigma_t = \sigma_t \setminus \sigma_{t-1}$).
- **Benchmark Consolidation & Release Package (Phase 7)**:
  - Canonical benchmark suite (`BenchmarkSuite v1.0.0`), target catalog, and metric registry.
- **Multi-Agent Security & Trust Network (Phase 8)**:
  - `AgentTrustGraph` and `DelegationChainAnalyzer` for transitive privilege escalation detection.
- **Comparative Evaluation vs. LLM-as-a-Judge (Phase 9)**:
  - Empirical evaluation demonstrating 0.0% FP vs. 60.0% LLM Judge FP on text-deception scenarios.
- **Enterprise Governance & Security Operations (Phases 10–11)**:
  - CI/CD Security Release Gate (`SecurityGate`), regression runner, and finding lifecycle management.
- **Adaptive Attack Discovery Foundation (Phase 12)**:
  - 4-Dimensional heuristic mutation engine (`AttackMutationEngine`) for perimeter evasion testing.
