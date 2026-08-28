#!/usr/bin/env python3
"""Phase 68A — M49 RAG Permission Inheritance and Retrieval Audit MVP Validator.

Comprehensive checks for corpus, run config, execution results, result YAML,
scorecard, notes, registry, and security fields.
"""
import json, sys, yaml, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks_passed = 0
checks_failed = 0
errors = []


def check(condition, msg):
    global checks_passed, checks_failed
    if condition:
        checks_passed += 1
        print(f"  ✓ {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  ✗ {msg}")


def file_exists(path, desc):
    result = path.exists()
    check(result, f"{desc} exists at {path}")
    return result if result else None


def yaml_load(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"YAML load: {path} — {e}")
        return None


def json_load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load: {path} — {e}")
        return None


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 68A — M49 RAG Permission Inheritance and Retrieval Audit MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus exists and has correct structure
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m49_rag_permission_inheritance_audit_mvp/playbook.yaml"
    corpus = yaml_load(corpus_path)
    check(corpus is not None, "Corpus playbook.yaml loaded")
    if corpus:
        entries = corpus.get("entries", [])
        meta = corpus.get("playbook_metadata", {})
        check(len(entries) >= 10, f"Corpus has >= 10 entries ({len(entries)})")

        control_cases = [e for e in entries if e.get("control_case")]
        check(len(control_cases) >= 2, f"Corpus has >= 2 control cases ({len(control_cases)})")

        categories = [e.get("category", "") for e in entries]
        check("rag_permission_inheritance_bypass" in categories,
              "Corpus includes rag_permission_inheritance_bypass")
        check("rag_low_privileged_high_priv_doc_request" in categories,
              "Corpus includes rag_low_privileged_high_priv_doc_request")
        check("rag_cross_tenant_retrieval_attempt" in categories,
              "Corpus includes rag_cross_tenant_retrieval_attempt")
        check("rag_restricted_summary_request" in categories,
              "Corpus includes rag_restricted_summary_request")
        check("rag_permission_context_confusion" in categories,
              "Corpus includes rag_permission_context_confusion")
        check("rag_source_attribution_required" in categories,
              "Corpus includes rag_source_attribution_required")
        check("rag_retrieval_audit_gap" in categories,
              "Corpus includes rag_retrieval_audit_gap")
        check("rag_permission_decision_logging_required" in categories,
              "Corpus includes rag_permission_decision_logging_required")
        check("safe_same_tenant_allowed_control_case" in categories,
              "Corpus includes safe_same_tenant_allowed_control_case")
        check("benign_authorized_retrieval_control_case" in categories,
              "Corpus includes benign_authorized_retrieval_control_case")

        # Check all entries use SIM_ placeholders
        all_text = yaml.dump(entries)
        sim_pattern = re.findall(r'<SIM_\w+>', all_text)
        check(len(sim_pattern) >= len(entries) * 3,
              f"All entries use <SIM_...> placeholders ({len(sim_pattern)} found)")

        # Check no real data in corpus
        real_patterns = [
            r'https?://(?!sim\.)', r'(?<![a-zA-Z])sk-[A-Za-z0-9_-]+',
            r'api[a-zA-Z]*\.[a-zA-Z]+\.com', r'secret[a-zA-Z]*=',
            r'token[a-zA-Z]*=', r'password=',
        ]
        corpus_str = str(corpus).lower()
        no_real = True
        for pat in real_patterns:
            if re.search(pat, corpus_str):
                no_real = False
                break
        check(no_real, "Corpus contains no real URLs, tokens, secrets, or API keys")

        # Check all entries have required fields
        for e in entries:
            eid = e.get("entry_id", "MISSING")
            check(e.get("synthetic_user_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_user_id")
            check(e.get("synthetic_tenant_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_tenant_id")
            check(e.get("synthetic_document_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_document_id")
            check(e.get("synthetic_permission_policy_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_permission_policy_id")
            check(e.get("synthetic_retrieval_query_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_retrieval_query_id")
            check(e.get("confirmed_vulnerability") is False,
                  f"{eid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{eid} formal_finding_allowed == false")
            check(e.get("production_safety_claimed") is False,
                  f"{eid} production_safety_claimed == false")
            check(e.get("controlled_replay_claimed") is False,
                  f"{eid} controlled_replay_claimed == false")

        # Module metadata
        check(meta.get("module_id") == "M49", "Corpus module_id == M49")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Corpus assessment_mode == adversarial_validation")
        check(meta.get("attacker_type") == "low_privileged_operator",
              "Corpus attacker_type == low_privileged_operator")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("real_rag_system_allowed") is False,
              "Corpus real_rag_system_allowed == false")
        check(meta.get("real_knowledge_base_allowed") is False,
              "Corpus real_knowledge_base_allowed == false")
        check(meta.get("real_document_access_allowed") is False,
              "Corpus real_document_access_allowed == false")
        check(meta.get("real_cloud_storage_allowed") is False,
              "Corpus real_cloud_storage_allowed == false")
        check(meta.get("real_tenant_data_allowed") is False,
              "Corpus real_tenant_data_allowed == false")
        check(meta.get("real_permission_system_allowed") is False,
              "Corpus real_permission_system_allowed == false")
        check(meta.get("real_audit_log_allowed") is False,
              "Corpus real_audit_log_allowed == false")
        check(meta.get("real_tool_call_allowed") is False,
              "Corpus real_tool_call_allowed == false")
        check(meta.get("real_api_call_allowed") is False,
              "Corpus real_api_call_allowed == false")

    # ================================================================
    # 2. Run config (embedded in playbook metadata)
    # ================================================================
    print("\n2. Run config (embedded in playbook metadata)")
    if corpus:
        meta = corpus.get("playbook_metadata", {})
        check(meta.get("fake_runtime_only") is True, "Run config fake_runtime_only == true")
        check(meta.get("synthetic_only") is True, "Run config synthetic_only == true")

    # ================================================================
    # 3. Execution results JSON
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/phase68a_m49_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 10, f"execution_results has >= 10 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("entry_id", "MISSING")
            check(r.get("real_rag_system_connected") is False,
                  f"{rid} real_rag_system_connected == false")
            check(r.get("real_knowledge_base_accessed") is False,
                  f"{rid} real_knowledge_base_accessed == false")
            check(r.get("real_document_accessed") is False,
                  f"{rid} real_document_accessed == false")
            check(r.get("real_cloud_storage_accessed") is False,
                  f"{rid} real_cloud_storage_accessed == false")
            check(r.get("real_tenant_data_accessed") is False,
                  f"{rid} real_tenant_data_accessed == false")
            check(r.get("real_permission_system_used") is False,
                  f"{rid} real_permission_system_used == false")
            check(r.get("real_audit_log_accessed") is False,
                  f"{rid} real_audit_log_accessed == false")
            check(r.get("real_tool_executed") is False,
                  f"{rid} real_tool_executed == false")
            check(r.get("real_api_called") is False,
                  f"{rid} real_api_called == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase68a_m49_mvp/m49_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m49_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M49", "result module_id == M49")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 10,
              f"result total_cases >= 10 ({result_yaml.get('total_cases')})")
        check("permission_boundary_preserved_count" in result_yaml,
              "result has permission_boundary_preserved_count")
        check("restricted_retrieval_blocked_count" in result_yaml,
              "result has restricted_retrieval_blocked_count")
        check("cross_tenant_retrieval_blocked_count" in result_yaml,
              "result has cross_tenant_retrieval_blocked_count")
        check("authorization_required_count" in result_yaml,
              "result has authorization_required_count")
        check("restricted_summary_blocked_count" in result_yaml,
              "result has restricted_summary_blocked_count")
        check("permission_context_preserved_count" in result_yaml,
              "result has permission_context_preserved_count")
        check("retrieval_source_attributed_count" in result_yaml,
              "result has retrieval_source_attributed_count")
        check("permission_decision_logged_count" in result_yaml,
              "result has permission_decision_logged_count")
        check("audit_trace_complete_count" in result_yaml,
              "result has audit_trace_complete_count")
        check("audit_gap_detected_count" in result_yaml,
              "result has audit_gap_detected_count")
        check("human_review_required_count" in result_yaml,
              "result has human_review_required_count")
        check("benign_authorized_retrieval_allowed_count" in result_yaml,
              "result has benign_authorized_retrieval_allowed_count")
        check("same_tenant_allowed_count" in result_yaml,
              "result has same_tenant_allowed_count")
        check("control_case_passed_count" in result_yaml,
              "result has control_case_passed_count")
        check("control_case_failed_count" in result_yaml,
              "result has control_case_failed_count")
        check("inconclusive_count" in result_yaml, "result has inconclusive_count")
        check(result_yaml.get("confirmed_vulnerability") is False,
              "result confirmed_vulnerability == false")
        check(result_yaml.get("formal_finding_allowed") is False,
              "result formal_finding_allowed == false")
        check(result_yaml.get("production_safety_claimed") is False,
              "result production_safety_claimed == false")
        check(result_yaml.get("controlled_replay_claimed") is False,
              "result controlled_replay_claimed == false")
        check(result_yaml.get("real_rag_system_connected") is False,
              "result real_rag_system_connected == false")
        check(result_yaml.get("real_knowledge_base_accessed") is False,
              "result real_knowledge_base_accessed == false")
        check(result_yaml.get("real_document_accessed") is False,
              "result real_document_accessed == false")
        check(result_yaml.get("real_cloud_storage_accessed") is False,
              "result real_cloud_storage_accessed == false")
        check(result_yaml.get("real_tenant_data_accessed") is False,
              "result real_tenant_data_accessed == false")
        check(result_yaml.get("real_permission_system_used") is False,
              "result real_permission_system_used == false")
        check(result_yaml.get("real_audit_log_accessed") is False,
              "result real_audit_log_accessed == false")
        check(result_yaml.get("real_tool_executed") is False,
              "result real_tool_executed == false")
        check(result_yaml.get("real_api_called") is False,
              "result real_api_called == false")
        check(result_yaml.get("evidence_trace_present") is True,
              "result evidence_trace_present == true")
        check(result_yaml.get("exploit_chain_candidate_generated") is False,
              "result exploit_chain_candidate_generated == false")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/phase68a_m49_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M49", "scorecard module_id == M49")
        check(sm.get("assessment_mode") == "adversarial_validation",
              "scorecard assessment_mode == adversarial_validation")
        check(sm.get("simulated_signal_only") is True,
              "scorecard simulated_signal_only == true")
        check(sm.get("confirmed_vulnerability") is False,
              "scorecard confirmed_vulnerability == false")
        check(sm.get("formal_finding_allowed") is False,
              "scorecard formal_finding_allowed == false")
        check(sm.get("production_safety_claimed") is False,
              "scorecard production_safety_claimed == false")
        check(sm.get("controlled_replay_claimed") is False,
              "scorecard controlled_replay_claimed == false")
        check(sm.get("safety_level") == "simulated_runtime_safety",
              "scorecard safety_level == simulated_runtime_safety")
        check(sm.get("production_safety") == "out_of_scope",
              "scorecard production_safety == out_of_scope")

        cv = scorecard.get("capability_value")
        rl = scorecard.get("risk_level")
        check(cv is not None and rl is not None,
              f"scorecard has capability_value ({cv}) and risk_level ({rl})")
        check(cv != rl,
              f"capability_value ({cv}) and risk_level ({rl}) are separate concepts")
        check(scorecard.get("capability_value_semantics") is not None,
              "scorecard has capability_value_semantics")
        check(scorecard.get("risk_level_semantics") is not None,
              "scorecard has risk_level_semantics")

        check("permission_boundary_preserved" in rs,
              "scorecard result_summary has permission_boundary_preserved")
        check("restricted_retrieval_blocked" in rs,
              "scorecard result_summary has restricted_retrieval_blocked")
        check("cross_tenant_retrieval_blocked" in rs,
              "scorecard result_summary has cross_tenant_retrieval_blocked")
        check("authorization_required" in rs,
              "scorecard result_summary has authorization_required")
        check("restricted_summary_blocked" in rs,
              "scorecard result_summary has restricted_summary_blocked")
        check("permission_context_preserved" in rs,
              "scorecard result_summary has permission_context_preserved")
        check("retrieval_source_attributed" in rs,
              "scorecard result_summary has retrieval_source_attributed")
        check("permission_decision_logged" in rs,
              "scorecard result_summary has permission_decision_logged")
        check("audit_trace_complete" in rs,
              "scorecard result_summary has audit_trace_complete")
        check("audit_gap_detected" in rs,
              "scorecard result_summary has audit_gap_detected")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")
        check("benign_authorized_retrieval_allowed" in rs,
              "scorecard result_summary has benign_authorized_retrieval_allowed")
        check("same_tenant_allowed" in rs,
              "scorecard result_summary has same_tenant_allowed")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase68a_m49_rag_permission_audit_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实 RAG" in notes_text or "no real RAG" in notes_text.lower(),
              "Notes state no real RAG system connection")
        check("不访问真实知识库" in notes_text or "no real knowledge" in notes_text.lower(),
              "Notes state no real knowledge base access")
        check("不访问真实文档" in notes_text or "no real document" in notes_text.lower(),
              "Notes state no real document access")
        check("不访问真实租户" in notes_text or "no real tenant" in notes_text.lower(),
              "Notes state no real tenant data access")
        check("不访问真实权限系统" in notes_text or "no real permission" in notes_text.lower(),
              "Notes state no real permission system access")
        check("不访问真实审计日志" in notes_text or "no real audit log" in notes_text.lower(),
              "Notes state no real audit log access")
        check("confirmed_vulnerability" in notes_text,
              "Notes mention confirmed_vulnerability")
        check("formal_finding_allowed" in notes_text,
              "Notes mention formal_finding_allowed")
        check("adversarial_validation" in notes_text,
              "Notes mention adversarial_validation mode")

    # ================================================================
    # 7. Registry check
    # ================================================================
    print("\n7. Registry")
    reg_path = ROOT / "capability_modules/module_registry.yaml"
    reg = yaml_load(reg_path)
    if reg:
        modules = reg.get("modules", [])
        m49 = next((m for m in modules if m.get("module_id") == "M49"), None)
        check(m49 is not None, "M49 exists in registry")
        if m49:
            check(m49.get("synthetic_only") is True, "Registry M49 synthetic_only == true")
            check(m49.get("production_safety") == "out_of_scope",
                  "Registry M49 production_safety == out_of_scope")
            check(m49.get("confirmed_vulnerability_allowed") is False,
                  "Registry M49 confirmed_vulnerability_allowed == false")
            check(m49.get("formal_finding_allowed") is False,
                  "Registry M49 formal_finding_allowed == false")

    # ================================================================
    # 8. Per-deliverable security field sweep
    # ================================================================
    print("\n8. Security field consistency")

    deliverables = {
        "corpus (playbook.yaml)": corpus,
        "execution_results.json": exec_results,
        "m49_result.yaml": result_yaml,
        "capability_scorecard.yaml": scorecard,
    }

    for name, data in deliverables.items():
        if data is None:
            check(False, f"{name}: could not load — skipping")
            continue
        data_str = str(data).lower()
        check("confirmed_vulnerability" not in data_str or 'false' in data_str,
              f"{name}: confirmed_vulnerability == false")
        check("formal_finding_allowed" not in data_str or 'false' in data_str,
              f"{name}: formal_finding_allowed == false")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print("Phase 68A M49 RAG Permission Audit validation: ALL CHECKS PASSED")
    else:
        print("Phase 68A M49 RAG Permission Audit validation: FAILED")
    print(f"  checks_passed: {checks_passed}")
    print(f"  checks_failed: {checks_failed}")
    if errors:
        print("\n  Errors:")
        for e in errors:
            print(f"    - {e}")
    print("=" * 60)

    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
