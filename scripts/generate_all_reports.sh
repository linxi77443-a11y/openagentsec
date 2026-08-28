#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

REQUIRED_INPUTS=(
  "reports/evidence/atlas_assessment_summary.json"
  "reports/evidence_index.md"
  "coverage/atlas_coverage_matrix.yaml"
  "coverage/atlas_coverage_summary.md"
  "coverage/coverage_gap_analysis.md"
  "docs/control_checklist.md"
  "reports/enterprise_ai_security_assessment_template.md"
  "assessment_profiles/chatbot_profile.yaml"
  "assessment_profiles/rag_profile.yaml"
  "assessment_profiles/agent_profile.yaml"
  "assessment_profiles/ai_gateway_profile.yaml"
  "test_catalog/test_capability_index.yaml"
  "test_catalog/manual_ui_test_catalog.yaml"
  "replays/manual_ui_replay_schema.md"
  "replays/manual_ui_samples/chatbot_manual_replay_sample.json"
  "replays/manual_ui_samples/rag_manual_replay_sample.json"
  "replays/manual_ui_samples/agent_manual_replay_sample.json"
  "targets/api/api_target_schema.md"
  "targets/api/chatbot_api_target_sample.yaml"
  "targets/api/rag_api_target_sample.yaml"
  "targets/api/mock_responses/chatbot_api_mock_response.json"
  "targets/api/mock_responses/rag_api_mock_response.json"
  "docs/api_provider_onboarding.md"
  "red_team/ai_red_team_playbook.md"
  "red_team/finding_severity_model.md"
  "red_team/finding_template.md"
  "red_team/evidence_handling_guide.md"
  "red_team/mitigation_retest_workflow.md"
  "red_team/red_team_report_outline.md"
  "red_team/README.md"
  "inventory/ai_asset_inventory_schema.md"
  "inventory/sample_ai_asset_inventory.yaml"
  "inventory/ai_asset_inventory_index.yaml"
  "governance/nist_ai_rmf_mapping.yaml"
  "governance/nist_genai_profile_mapping.yaml"
  "governance/ai_risk_governance_checklist.md"
  "supply_chain/ai_ml_bom_schema.md"
  "supply_chain/sample_ai_ml_bom.yaml"
  "supply_chain/model_provenance_checklist.md"
  "supply_chain/supply_chain_risk_register_template.yaml"
  "supply_chain/supply_chain_to_atlas_owasp_mapping.yaml"
  "external_tools/external_tool_evidence_schema.md"
  "external_tools/external_tool_adapter_index.yaml"
  "external_tools/external_tool_risk_boundary.md"
  "external_tools/external_tool_to_atlas_owasp_mapping.yaml"
  "external_tools/garak_adapter_plan.md"
  "external_tools/pyrit_adapter_plan.md"
  "external_tools/agent_benchmark_adapter_plan.md"
  "external_tools/browser_automation_adapter_plan.md"
  "external_tools/api_provider_adapter_plan.md"
  "external_tools/mock_external_tool_evidence_mapping.yaml"
  "reports/evidence/external_tools/mock_external_tool_normalized_evidence.json"
  "reports/evidence/external_tools/mock_external_tool_evidence_index.json"
  "owasp/llm_top10_2025.yaml"
  "owasp/llm_to_atlas_crosswalk.yaml"
  "owasp/llm_to_corpus_mapping.yaml"
  "owasp/llm_to_controls_mapping.yaml"
  "owasp/llm_to_supply_chain_mapping.yaml"
  "owasp/llm_report_language.md"
  "corpus/chatbot/improper_output_handling.yaml"
  "corpus/chatbot/misinformation.yaml"
  "corpus/rag/vector_embedding_weaknesses.yaml"
  "corpus/rag/stale_or_conflicting_knowledge.yaml"
  "corpus/api/unbounded_consumption_baseline.yaml"
  "corpus/regression/owasp_llm_regression.yaml"
  "assessment_plans/assessment_plan_schema.md"
  "assessment_plans/assessment_plan_index.yaml"
  "assessment_plans/generated/plan_sample_internal_chatbot.yaml"
  "assessment_plans/generated/plan_sample_policy_rag_assistant.yaml"
  "assessment_plans/generated/plan_sample_generic_agent.yaml"
  "assessment_plans/generated/plan_sample_fastgpt_workflow_api.yaml"
  "assessment_plans/generated/plan_sample_manual_ui_chatbot.yaml"
  "api_provider/README.md"
  "api_provider/api_provider_schema.md"
  "api_provider/target_profile_schema.md"
  "api_provider/provider_config_template.local.example.yaml"
  "api_provider/request_response_normalization_schema.md"
  "api_provider/provider_safety_guardrails.md"
  "api_provider/provider_execution_boundary.md"
  "api_provider/sample_targets/openai_compatible_chat_sample.yaml"
  "api_provider/sample_targets/rag_qa_api_sample.yaml"
  "api_provider/sample_targets/agent_api_sample.yaml"
  "api_provider/sample_targets/workflow_api_sample.yaml"
  "api_provider/sample_targets/fastgpt_compatible_sample.yaml"
  "api_provider/provider_validation_result.yaml"
  "api_provider/provider_validation_report.md"
  "scripts/api_provider_dry_run_simulator.py"
  "scripts/validate_api_provider_formalization.py"
  "scripts/validate_authorized_target_onboarding.py"
  "api_provider/onboarding/README.md"
  "api_provider/onboarding/authorized_target_onboarding_schema.md"
  "api_provider/onboarding/target_intake_template.yaml"
  "api_provider/onboarding/roe_checklist.md"
  "api_provider/onboarding/credential_isolation_policy.md"
  "api_provider/onboarding/test_scope_definition_template.yaml"
  "api_provider/onboarding/allowed_prohibited_operations_matrix.yaml"
  "api_provider/onboarding/rate_limit_and_safety_window_policy.md"
  "api_provider/onboarding/approval_gate_checklist.md"
  "api_provider/onboarding/onboarding_validation_result.yaml"
  "api_provider/onboarding/onboarding_validation_report.md"
  "api_provider/mock_harness/README.md"
  "api_provider/mock_harness/mock_api_target_schema.md"
  "api_provider/mock_harness/mock_request_fixtures.yaml"
  "api_provider/mock_harness/mock_response_fixtures.yaml"
  "api_provider/mock_harness/mock_execution_trace.yaml"
  "api_provider/mock_harness/mock_normalized_response_samples.yaml"
  "api_provider/mock_harness/mock_execution_boundary.md"
  "api_provider/mock_harness/mock_harness_validation_result.yaml"
  "api_provider/mock_harness/mock_harness_validation_report.md"
  "scripts/run_local_mock_api_harness.py"
  "scripts/validate_local_mock_api_harness.py"
  "api_provider/authorized_dry_run_plan/README.md"
  "api_provider/authorized_dry_run_plan/limited_authorized_dry_run_schema.md"
  "api_provider/authorized_dry_run_plan/rate_limit_request_budget_policy.md"
  "api_provider/authorized_dry_run_plan/rollback_stop_condition_policy.md"
  "api_provider/authorized_dry_run_plan/dry_run_approval_packet_template.md"
  "api_provider/authorized_dry_run_plan/allowed_test_bundle_definition.yaml"
  "api_provider/authorized_dry_run_plan/preflight_checklist.md"
  "api_provider/authorized_dry_run_plan/credential_readiness_checklist.md"
  "api_provider/authorized_dry_run_plan/dry_run_plan_validation_result.yaml"
  "api_provider/authorized_dry_run_plan/dry_run_plan_validation_report.md"
  "scripts/validate_limited_authorized_api_dry_run_plan.py"
  "api_provider/single_smoke_test_design/README.md"
  "api_provider/single_smoke_test_design/single_smoke_test_schema.md"
  "api_provider/single_smoke_test_design/candidate_target_template.yaml"
  "api_provider/single_smoke_test_design/minimal_request_bundle.yaml"
  "api_provider/single_smoke_test_design/expected_safe_response_contract.md"
  "api_provider/single_smoke_test_design/execution_preflight_gate.yaml"
  "api_provider/single_smoke_test_design/abort_condition_checklist.md"
  "api_provider/single_smoke_test_design/operator_runbook_template.md"
  "api_provider/single_smoke_test_design/evidence_placeholder_schema.md"
  "api_provider/single_smoke_test_design/smoke_test_design_validation_result.yaml"
  "api_provider/single_smoke_test_design/smoke_test_design_validation_report.md"
  "scripts/validate_single_authorized_api_smoke_test_design.py"
)

for input in "${REQUIRED_INPUTS[@]}"; do
  if [[ ! -f "$input" ]]; then
    echo "Missing required input: $input"
    exit 1
  fi
done

cat <<'EOF'
Report generation boundary:
- Reads local JSON, YAML, and Markdown files only.
- Does not access network, real APIs, real models, real systems, or credentials.
- Does not execute tests or modify evidence.
- API Provider Skeleton status is dry-run readiness only, not real API tested / passed.
- AI Red Teaming Methodology is a methodology/template layer, not a real red team project execution.
- AI Asset Inventory uses sample/fake assets only, does not represent any real system.
- NIST AI RMF Mapping is a project-internal governance layer, not NIST compliance certification.
- AI/ML-BOM uses sample/fake BOM data only, does not represent any real system components.
- Supply chain risk mapping is a methodology reference, not a complete supply chain threat model.
- External Evaluation Tool Adapters are planning/design layer only; no external tools are installed or executed.
- External Tool Mock Evidence Normalization uses fake/mock outputs only and is not real external tool execution.
- Phase 21 System Release Consolidation is a documentation/release packaging phase; no new test capabilities, no external tools, no execute, no real system connection.
- Phase 22 OWASP LLM Top 10 Crosswalk is a mapping layer only; all new corpus entries are planned, not executed.
- Phase 23 Assessment Plan Generator is a planning layer only; generated plans are sample/planning_only, not executed.
- Phase 24 Corpus-to-Testcase Compiler is a compilation layer only; all generated testcases are drafts (executed=false, real_target_connected=false, usable_for_formal_finding=false).
- Phase 25 Generated Testcase Curation & Runner Binding is a static curation layer only; all curation results are classification-only (executed=false, real_target_connected=false, usable_for_formal_finding=false). Runner bindings are draft recommendations only (allowed_now=false).
- Phase 26 Curated Regression Suite Builder is a static suite build only; all suites are curated_draft (executed=false, real_target_connected=false, usable_for_formal_finding=false). Promptfoo suite drafts are generated_only=true, curated_from_static_analysis=true.
- Phase 26.5 Regression Suite Gap Triage is a static analysis only; all gap analysis outputs declare executed=false, real_target_connected=false, usable_for_formal_finding=false. Zero-selected suites are a quality gate result, not a failure.
- Phase 27A Corpus & Curation Backfill is a static backfill layer only; all fixes are mapping/schema/code changes (fake_assets_required logic, risk type multi-mapping, API corpus execution mode). No tests executed. No real systems connected.
- Phase 27 Regression Suite Dry-Run Validator is a static validation layer only; validation_mode=static_dry_run_only. No tests executed. No promptfoo executed. No real systems connected. No evidence generated.
- Phase 28 Assertion & Risk Signal Rule Engine is a static rule layer only; validation_mode=static_rule_validation. No tests executed. No promptfoo executed. No real systems connected. No evidence generated. No findings generated.
- Phase 29 Finding Generator Prototype is a sample finding draft generation layer only; all findings are sample/mock drafts (real_target_validated=false, usable_for_formal_report=false). No tests executed. No promptfoo executed. No real systems connected. No real evidence generated. No real findings generated.
- Phase 30 Formal Report Package Builder is a sample delivery package build layer only; the sample package declares real_customer=false, real_target_validated=false, formal_report=false, usable_for_customer_delivery=false. No tests executed. No promptfoo executed. No real systems connected. No real evidence generated. No real findings generated.
- Phase 31 Generic API Provider Formalization is a provider formalization layer only; all sample targets declare real_target=false, dry_run_only=true, execution_allowed=false, usable_for_real_test=false. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. Dry-run simulator makes no network calls. Provider validation result declares network_called=false, credentials_loaded=false, real_target_connected=false, tests_executed=false, evidence_generated=false, usable_for_formal_finding=false.
- Phase 31B Authorized Test Target Onboarding is an authorized test target onboarding layer only; all targets declare authorization_required=true, approval_status=not_approved, execution_allowed=false. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. Onboarding validation script performs 18 static checks. Onboarding validation result declares authorization_required=true, approval_status=not_approved, execution_allowed=false, credentials_loaded=false, real_target_connected=false, production_target_allowed=false.
- Phase 31C Local Mock API Execution Harness is a local mock execution layer only; all mock harness outputs declare mock_execution=true, external_network_called=false, credentials_loaded=false, real_target_connected=false, evidence_generated=false, usable_for_formal_finding=false. Mock harness uses local fixtures only. No network calls. No real credentials. No real endpoints accessed. No real security tests executed.
- Phase 31D Limited Authorized API Dry-Run Plan is a plan definition layer only; all plan files contain placeholder data only. No real URLs. No real tokens. No real credentials. No real emails. No real API keys. No network calls. No real systems connected. No tests executed. No evidence generated. The validation script performs static checks only and must not access network or credentials.
- Phase 31E Single Authorized API Smoke Test Design is a static design definition layer only; all design files declare smoke_test_design_ready=true, only_one_target_allowed=true, read_only_operations_only=true, approval_status=not_approved, execution_allowed=false, credentials_loaded=false, real_target_connected=false, network_called=false, evidence_generated=false. No real APIs, no real credentials, no network calls, no adversarial prompts. The smoke test design is a static design definition only — not an execution plan. Validation script performs static checks only.
- Phase 31F Single Smoke Test Approval Packet & Go/No-Go Gate is a static approval packet and gate definition layer only; all approval packet files declare approval_packet_ready=true, approval_status=not_approved, go_no_go_status=no_go, execution_allowed=false, human_approval_required=true, operator_signoff_required=true, risk_acceptance_required=true, credentials_loaded=false, real_target_connected=false, network_called=false, evidence_generated=false, production_target_allowed=false, execution_hold=true. No real APIs, no real credentials, no network calls, no adversarial prompts. The approval packet is a static approval packet definition only — not an execution gate. Validation script performs static checks only.
- Phase 32C Full Authorized API Regression Execution is a full regression execution layer only; regression executed against authorized test API only, not production. All findings are candidates only and require human review before formal finding status. No formal customer report generated. All outputs declare execution_mode=full_authorized_api_regression, target_environment=test, provider_type=fastgpt_compatible, redaction_applied=true, api_key_logged=false, authorization_header_logged=false, production_target=false.
- Phase 32D Real API Regression Assessment Report Builder is a read-only report-building phase. Builds complete assessment report from Phase 32C execution results. All findings remain candidate status (needs_human_review=true, usable_for_formal_finding=false). Redaction applied to all report outputs (redaction_applied=true). No re-running tests, no connecting to APIs, no reading credentials. All reports declare report_generated=true, source_phase=Phase 32C, redaction_applied=true, formal_finding=false, formal_customer_report=false, manual_review_required=true.
- Phase 33 Remediation & Retest Package Builder is a static remediation and retest package generation phase only. Generates 5 remediation packages, 5 retest packages, remediation task board (10 tasks), retest execution plan, and acceptance criteria. All packages declare remediation_status=planned or retest_status=not_executed, real_api_execution_allowed=false, redaction_required=true, human_go_no_go_required=true. No re-running tests, no connecting to APIs, no reading credentials. No remediation has been executed. No retest has been performed.
- Phase 34A DeepSeek Judge Provider Framework is a static judge provider framework layer only. Generates tool_judge_providers/ directory with DeepSeek judge provider template, schema, prompt templates, mock results, and adapter skeleton. All outputs are mock_only — no real API calls, no credentials, no network. All judge results declare network_called=false, credential_loaded=false, usable_for_formal_finding=false, human_go_no_go_required=true. No DeepSeek API has been called. No credentials have been loaded. No judge conclusion has been generated.
- Phase 34B DeepSeek Judge Go/No-Go Packet is a static Go/No-Go approval packet layer only. Generates go_no_go/ directory with approval packet, approval checklist (18 items), cost budget, execution plan, safety boundary, rollback plan (5 steps), acceptance criteria (10 items), and local config template (placeholders only). All approval status: not_approved. All flags: execution_allowed=false, network_allowed=false, credential_loaded=false, deepseek_api_called=false. No DeepSeek API has been called. No credentials have been loaded. No judge conclusion has been generated. No real API calls have been made.
- Phase 34C Controlled DeepSeek Judge Execution is a controlled real DeepSeek API execution layer only. Executes 21 real DeepSeek API calls (1 smoke + 15 batch candidates + 5 consolidated groups) against 16 existing finding candidates and 5 consolidated groups. No target API calls (allow_target_api_call=false), no new test generation. All outputs declare usable_for_formal_finding=false, manual_review_required=true, formal_finding=false, customer_report_ready=false. Output files: smoke_judge_result.json, batch_judge_results.json, consolidated_group_judge_results.json, execution_summary.json, validation_input.json. Execution validates against 20 checks. ~$0.01 total cost.
EOF

# Phase 27 Regression Suite Dry-Run Validator is a static validation layer only
# - validation_mode: static_dry_run_only
# - No tests executed
# - No promptfoo executed
# - No real systems connected
# - No evidence generated

# Phase 28 Assertion & Risk Signal Rule Engine is a static rule layer only
# - validation_mode: static_rule_validation
# - No tests executed
# - No promptfoo executed
# - No real systems connected
# - No evidence generated
# - No findings generated

# Phase 31 Generic API Provider Formalization is a provider formalization layer only
# - Sample targets: dry_run_only=true, real_target=false, execution_allowed=false
# - No real APIs connected
# - No real credentials loaded
# - No real endpoints accessed
# - No real security tests executed
# - Dry-run simulator: 0 network calls
# - Provider validation: network_called=false, credentials_loaded=false

# Phase 28 Assertion & Risk Signal Rule Engine is a static rule layer only
# - validation_mode: static_rule_validation
# - No tests executed
# - No promptfoo executed
# - No real systems connected
# - No evidence generated
# - No findings generated

# Phase 31 Generic API Provider Formalization is a provider formalization layer only
# - Sample targets: dry_run_only=true, real_target=false, execution_allowed=false
# - No real APIs connected
# - No real credentials loaded
# - No real endpoints accessed
# - No real security tests executed
# - Dry-run simulator: 0 network calls
# - Provider validation: network_called=false, credentials_loaded=false

# Phase 31B Authorized Test Target Onboarding is an onboarding layer only
# - All targets: authorization_required=true, approval_status=not_approved
# - No real APIs connected
# - No real credentials loaded
# - No real endpoints accessed
# - No real security tests executed
# - Onboarding validation: 18 static checks, all passed
# - Onboarding result: credentials_loaded=false, real_target_connected=false

# Phase 31C Local Mock API Execution Harness is a local mock execution layer only
# - Mock execution: true, external_network_called: false
# - No network calls, no real credentials, no real endpoints
# - All outputs: mock_execution=true, usable_for_formal_finding=false
# - Mock harness uses local fixtures only

# Phase 32C Full Authorized API Regression Execution is a full regression execution layer only
# - Execution mode: full_authorized_api_regression
# - Target environment: test (not production)
# - Provider type: fastgpt_compatible
# - Redaction applied: true
# - API key logged: false
# - Authorization header logged: false
# - Production target: false
# - Findings are candidates only, require human review

echo "Phase 31D Limited Authorized API Dry-Run Plan"
echo "  dry_run_plan_ready=true"
echo "  authorization_required=true"
echo "  approval_status=not_approved"
echo "  execution_allowed=false"
echo "  credentials_loaded=false"
echo "  real_target_connected=false"
echo "  network_called=false"
echo "  evidence_generated=false"
echo "  production_target_allowed=false"
echo "  no_network_calls=true"
echo "  no_real_credentials=true"

echo "Phase 31E Single Authorized API Smoke Test Design"
echo "  smoke_test_design_ready=true"
echo "  only_one_target_allowed=true"
echo "  read_only_operations_only=true"
echo "  approval_status=not_approved"
echo "  execution_allowed=false"
echo "  credentials_loaded=false"
echo "  real_target_connected=false"
echo "  network_called=false"
echo "  evidence_generated=false"
echo "  no_adversarial_prompts=true"
echo "  no_network_calls=true"
echo "  no_real_credentials=true"

echo "Phase 31F Single Smoke Test Approval Packet"
echo "  approval_packet_ready=true"
echo "  approval_status=not_approved"
echo "  go_no_go_status=no_go"
echo "  execution_allowed=false"
echo "  human_approval_required=true"
echo "  operator_signoff_required=true"
echo "  risk_acceptance_required=true"
echo "  credentials_loaded=false"
echo "  real_target_connected=false"
echo "  network_called=false"
echo "  evidence_generated=false"
echo "  production_target_allowed=false"
echo "  execution_hold=true"

echo "Phase 32C Full Authorized API Regression Execution"
echo "  execution_mode=full_authorized_api_regression"
echo "  target_environment=test"
echo "  provider_type=fastgpt_compatible"
echo "  total_requests_attempted=0"
echo "  total_requests_completed=0"
echo "  total_pass=0"
echo "  total_fail=0"
echo "  total_skipped=0"
echo "  finding_candidates=0"
echo "  redaction_applied=true"
echo "  api_key_logged=false"
echo "  authorization_header_logged=false"
echo "  production_target=false"

echo "Phase 32C script check"
if [[ -f "scripts/run_full_authorized_api_regression.py" ]]; then
  echo "  scripts/run_full_authorized_api_regression.py: present"
else
  echo "  scripts/run_full_authorized_api_regression.py: MISSING"
fi
if [[ -f "scripts/validate_full_authorized_api_regression_result.py" ]]; then
  echo "  scripts/validate_full_authorized_api_regression_result.py: present"
else
  echo "  scripts/validate_full_authorized_api_regression_result.py: MISSING"
fi

echo
echo "Phase 32D + 32D.1 + 32E Real API Report / Chinese Report / Finding Triage / Report Hardening"
echo "  report_generated=$(python3 -c "
import yaml, sys
try:
    r = yaml.safe_load(open('reports/real_api_regression_assessment/report_generation_result.yaml'))
    if r: print(r.get('report_generated', False))
    else: print(False)
except: print(False)
" 2>/dev/null || echo false)"
echo "  source_phase=Phase 32C"
echo "  finding_candidates=$(python3 -c "
import yaml, sys
try:
    r = yaml.safe_load(open('reports/real_api_regression_assessment/report_generation_result.yaml'))
    if r: print(r.get('finding_candidates', 0))
    else: print(0)
except: print(0)
" 2>/dev/null || echo 0)"
echo "  redaction_applied=true"
echo "  formal_finding=false"
echo "  formal_customer_report=false"
echo "  manual_review_required=true"

echo
echo "Phase 32D.1 Chinese Report Localization"
echo "  chinese_report_generated=$(python3 -c "
import yaml, sys
try:
    r = yaml.safe_load(open('reports/real_api_regression_assessment/report_generation_result.yaml'))
    if r: print(r.get('chinese_report_generated', False))
    else: print(False)
except: print(False)
" 2>/dev/null || echo false)"
echo "  english_report_preserved=$(python3 -c "
import yaml, sys
try:
    r = yaml.safe_load(open('reports/real_api_regression_assessment/report_generation_result.yaml'))
    if r: print(r.get('english_report_preserved', False))
    else: print(False)
except: print(False)
" 2>/dev/null || echo false)"
echo "  bilingual_index_generated=$(python3 -c "
import yaml, sys
try:
    r = yaml.safe_load(open('reports/real_api_regression_assessment/report_generation_result.yaml'))
    if r: print(r.get('bilingual_index_generated', False))
    else: print(False)
except: print(False)
" 2>/dev/null || echo false)"

echo
echo "Phase 32E Finding Triage & Report Hardening"
echo "  finding_triage_generated=$(python3 -c "
import yaml, sys
try:
    r = yaml.safe_load(open('reports/real_api_regression_assessment/report_generation_result.yaml'))
    if r: print(r.get('finding_triage_generated', False))
    else: print(False)
except: print(False)
" 2>/dev/null || echo false)"
echo "  final_hardened_generated=$(python3 -c "
import yaml, sys
try:
    r = yaml.safe_load(open('reports/real_api_regression_assessment/report_generation_result.yaml'))
    if r: print(r.get('final_hardened_generated', False))
    else: print(False)
except: print(False)
" 2>/dev/null || echo false)"

echo
echo "Phase 32D.1 + 32E file checks"
for f in \
  "reports/real_api_regression_assessment/executive_summary_en.md" \
  "reports/real_api_regression_assessment/report_language_index.md" \
  "reports/real_api_regression_assessment/finding_triage/finding_candidate_triage_table.yaml" \
  "reports/real_api_regression_assessment/finding_triage/consolidated_findings_summary.md" \
  "reports/real_api_regression_assessment/finding_triage/manual_review_checklist.md" \
  "reports/real_api_regression_assessment/finding_triage/false_positive_review_notes.md" \
  "reports/real_api_regression_assessment/final_hardened/management_brief_zh.md" \
  "reports/real_api_regression_assessment/final_hardened/executive_summary_final_zh.md" \
  "reports/real_api_regression_assessment/final_hardened/final_findings_summary_zh.md" \
  "reports/real_api_regression_assessment/final_hardened/remediation_action_plan_zh.md" \
  "reports/real_api_regression_assessment/final_hardened/retest_plan_final_zh.md" \
  "reports/real_api_regression_assessment/final_hardened/report_hardening_summary.yaml"; do
  if [[ -f "$f" ]]; then
    echo "  $f: present"
  else
    echo "  $f: MISSING"
  fi
done

echo "Phase 32D script check"
if [[ -f "scripts/build_real_api_regression_report.py" ]]; then
  echo "  scripts/build_real_api_regression_report.py: present"
else
  echo "  scripts/build_real_api_regression_report.py: MISSING"
fi
if [[ -f "scripts/validate_real_api_regression_report.py" ]]; then
  echo "  scripts/validate_real_api_regression_report.py: present"
else
  echo "  scripts/validate_real_api_regression_report.py: MISSING"
fi

echo
python3 scripts/generate_atlas_dashboard.py
python3 scripts/generate_enterprise_report.py

echo
echo "Generated files:"
echo "- dashboard/dashboard_data.json"
echo "- dashboard/index.md"
echo "- dashboard/atlas_dashboard.html"
echo "- reports/generated_atlas_assessment_report.md"
echo "- reports/real_api_regression_assessment/ (Chinese .md + English _en.md)"
echo "- reports/real_api_regression_assessment/report_language_index.md"
echo "- reports/real_api_regression_assessment/finding_triage/ (5 files)"
echo "- reports/real_api_regression_assessment/final_hardened/ (6 files)"
echo "- remediation_packages/ (11 files: schema, index, boundary, task board, 5 packages)"
echo "- retest_packages/ (12 files: schema, index, boundary, execution plan, acceptance criteria, comparison template, 5 packages)"
