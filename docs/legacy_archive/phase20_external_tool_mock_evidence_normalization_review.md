# Phase 20 External Tool Mock Evidence Normalization Review

## Scope

Phase 20 validates that fake/mock external tool outputs can be normalized into the unified external tool evidence schema and surfaced in dashboard/report outputs.

This phase does not install, run, or connect any real external evaluation tool.

## Deliverables

| Area | Path | Status |
|---|---|---|
| Mock raw outputs | `external_tools/mock_outputs/` | ready |
| Normalizer | `scripts/normalize_external_tool_mock_evidence.py` | ready |
| Mock evidence mapping | `external_tools/mock_external_tool_evidence_mapping.yaml` | ready |
| Normalized evidence | `reports/evidence/external_tools/mock_external_tool_normalized_evidence.json` | generated |
| Evidence index | `reports/evidence/external_tools/mock_external_tool_evidence_index.json` | generated |
| Dashboard/report integration | `scripts/generate_atlas_dashboard.py`, `scripts/generate_enterprise_report.py` | ready |
| Quality check | `runners/run_quality_check.sh` | ready |

## Mock Outputs

| Tool | Target profile | Execution mode | Real target connected |
|---|---|---|---|
| garak | chatbot | mock_only | false |
| PyRIT | rag | mock_only | false |
| AgentDojo | generic_agent | mock_only | false |
| AgentDyn | generic_agent | mock_only | false |
| Browser Automation | manual_ui_replay | mock_only | false |
| API Provider | api | mock_only | false |

## Normalization Guarantees

All normalized evidence entries must include:

- `adapter_status: mock_normalization_ready`
- `execution_mode: mock_only`
- `external_tool_executed: false`
- `real_target_connected: false`
- `normalized_result.usable_for_formal_finding: false`
- fixed `created_at: 2026-01-01T00:00:00Z`

## Boundaries

Phase 20 does not do any of the following:

- install garak, PyRIT, AgentDojo, AgentDyn, Playwright, or browser automation tooling
- run any external tool
- run any `--execute`
- connect real API, real Agent, real page, real model, external network, or real credential
- write to any real external system
- add new offensive test corpus
- claim external tool integration is complete

## Quality Gates

The quality check verifies:

- required mock output and evidence directories exist
- normalizer script exists
- mock outputs do not contain real URL/token/email/endpoint markers
- normalized evidence and evidence index exist
- normalized evidence keeps `external_tool_executed=false`
- normalized evidence keeps `real_target_connected=false`
- adapter status does not exceed `mock_normalization_ready`
- dashboard/report do not claim real external tool execution or real target integration
- mock evidence is not usable for formal findings

## Result

Phase 20 can be marked complete when the normalizer, report generator, and quality check all pass, and the final commit contains only mock-only evidence normalization artifacts.
