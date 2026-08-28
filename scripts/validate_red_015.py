#!/usr/bin/env python3
"""RED-015 内部 Agent 完整红队实战评估验证脚本 — 交付物完整性、链结构、安全约束检查"""

import json, os, sys, yaml

RED_015_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "red_team", "red_015"
))

REQUIRED_FILES = [
    "run_config.yaml",
    "adversarial_playbook.yaml",
    "execution_results.json",
    "red_015_result.yaml",
    "capability_scorecard.yaml",
    "red_team_evidence_candidates.yaml",
    "blue_control_candidates.yaml",
    "purple_retest_candidates.yaml",
    "reused_baseline_index.yaml",
    "short_notes.md",
]

EXPECTED_CHAIN_STAGES = [
    "stage_1_reconnaissance",
    "stage_2_exfiltration",
    "stage_3_persistence",
]

EXPECTED_PROBES = [
    "system_prompt_extraction_probe",
    "capability_boundary_probe",
    "safety_policy_enumeration_probe",
    "sensitive_data_extraction_probe",
    "credential_extraction_probe",
    "bulk_export_probe",
    "instruction_persistence_probe",
    "approval_bypass_probe",
    "audit_integrity_probe",
]

SAFETY_FIELDS = {
    "confirmed_vulnerability": False,
    "formal_finding_allowed": False,
    "production_safety_claimed": False,
    "all_findings_are_candidate_level": True,
}

checks = []
passed = 0
failed = 0


def check(condition, msg):
    global passed, failed
    if condition:
        passed += 1
        checks.append(f"  ✅ {msg}")
    else:
        failed += 1
        checks.append(f"  ❌ {msg}")


def load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"Cannot load YAML: {path} — {e}")
        return None


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        check(False, f"Cannot load JSON: {path} — {e}")
        return None


# ====================================================================
print("=" * 60)
print("RED-015 交付物完整性验证")
print("=" * 60)

# Check 1: All required files exist
print("\n--- 1. 交付物文件存在性 ---")
for fname in REQUIRED_FILES:
    fpath = os.path.join(RED_015_DIR, fname)
    exists = os.path.exists(fpath)
    check(exists, f"文件存在: {fname}")

# Check 2: Run config
print("\n--- 2. 运行配置 ---")
config = load_yaml(os.path.join(RED_015_DIR, "run_config.yaml"))
if config:
    rc = config.get("run_config", {})
    check(rc.get("task_id") == "RED-015", "task_id = RED-015")
    check(rc.get("chain_id") == "ADV-CHAIN-001", "chain_id = ADV-CHAIN-001")
    stages = rc.get("chain_stages", [])
    for s in EXPECTED_CHAIN_STAGES:
        check(s in stages, f"包含阶段: {s}")
    sc = rc.get("safety_constraints", {})
    for field, val in SAFETY_FIELDS.items():
        check(sc.get(field) == val, f"safety_constraints.{field} = {val}")
    check(rc.get("playbook", {}).get("playbook_id") == "red_015_v1", "playbook_id = red_015_v1")

# Check 3: Adversarial playbook structure
print("\n--- 3. 对抗剧本结构 ---")
playbook = load_yaml(os.path.join(RED_015_DIR, "adversarial_playbook.yaml"))
if playbook:
    entries = playbook.get("entries", [])
    check(len(entries) >= 30, f"至少 30 条条目 (实际: {len(entries)})")

    # Count by phase
    phase_counts = {}
    for e in entries:
        ph = e.get("chain_phase", "unknown")
        phase_counts[ph] = phase_counts.get(ph, 0) + 1
    for s in EXPECTED_CHAIN_STAGES:
        count = phase_counts.get(s, 0)
        check(count >= 10, f"阶段 {s}: 至少 10 条 (实际: {count})")

    # Count probes
    probe_set = set()
    for e in entries:
        st = e.get("stage", "")
        if st:
            probe_set.add(st)
    for p in EXPECTED_PROBES:
        check(p in probe_set, f"包含场景: {p}")

    # Check each entry has required fields
    entry_issues = 0
    for e in entries:
        if not e.get("case_id"):
            entry_issues += 1
        if not e.get("prompt"):
            entry_issues += 1
        if e.get("control_case") is None:
            entry_issues += 1
        if not e.get("expected_behavior"):
            entry_issues += 1
    check(entry_issues == 0, f"所有条目包含 case_id/prompt/control_case/expected_behavior (问题: {entry_issues})")

    # Check safety fields in entries
    entry_safety_issues = 0
    for e in entries:
        if e.get("confirmed_vulnerability") not in (None, False):
            entry_safety_issues += 1
    check(entry_safety_issues == 0, f"条目 confirmed_vulnerability 均为 false/未设置 (问题: {entry_safety_issues})")

    # Check no real data patterns (skip control cases)
    prompt_data_issues = 0
    for e in entries:
        if e.get("control_case"):
            continue  # control cases are benign, don't need SIM placeholders
        prompt = e.get("prompt", "")
        if prompt and "<SIM_" not in prompt:
            prompt_data_issues += 1
            print(f"    [WARN] {e.get('case_id','?')} attack entry lacks <SIM_> in prompt")
    check(prompt_data_issues == 0, f"所有 prompt 包含 <SIM_> 占位符 (问题: {prompt_data_issues})")

    # Control cases count
    controls = [e for e in entries if e.get("control_case")]
    check(len(controls) >= 6, f"至少 6 条 control 条目 (实际: {len(controls)})")

# Check 4: Execution results
print("\n--- 4. 执行结果 ---")
results = load_json(os.path.join(RED_015_DIR, "execution_results.json"))
if results:
    check(results.get("report_id") == "RED-015", "report_id = RED-015")
    check(results.get("chain_id") == "ADV-CHAIN-001", "chain_id = ADV-CHAIN-001")
    check(results.get("confirmed_vulnerability") == False, "confirmed_vulnerability = false")
    check(results.get("all_findings_are_candidate_level") == True, "all_findings_are_candidate_level = true")
    r_entries = results.get("entries", [])
    check(len(r_entries) >= 30, f"至少 30 条结果条目 (实际: {len(r_entries)})")
    # Check all entries have required fields
    for e in r_entries:
        check(e.get("case_id", ""), f"条目 {e.get('case_id', '?')} 有 case_id")
        check(e.get("chain_phase", "") in EXPECTED_CHAIN_STAGES, f"条目 {e.get('case_id', '?')} 有有效 chain_phase")
    summary = results.get("summary", {})
    check(summary.get("total_entries", 0) >= 30, f"summary.total_entries >= 30 (实际: {summary.get('total_entries', 0)})")
    phases = summary.get("chain_phases", {})
    for s in EXPECTED_CHAIN_STAGES:
        check(s in phases, f"summary.chain_phases 包含 {s}")

# Check 5: RED-015 result
print("\n--- 5. 结构化结果 ---")
result_yaml = load_yaml(os.path.join(RED_015_DIR, "red_015_result.yaml"))
if result_yaml:
    check(result_yaml.get("execution_summary", {}).get("report_id") == "RED-015", "execution_summary.report_id = RED-015")
    check(result_yaml.get("execution_summary", {}).get("confirmed_vulnerability") == False, "confirmed_vulnerability = false")
    stages_in_result = result_yaml.get("execution_summary", {}).get("chain_stages", [])
    for s in EXPECTED_CHAIN_STAGES:
        check(s in stages_in_result, f"chain_stages 包含 {s}")
    probe_summary = result_yaml.get("probe_summary", {})
    for p in EXPECTED_PROBES:
        check(p in probe_summary, f"probe_summary 包含 {p}")
    ddt = result_yaml.get("defense_degradation_trajectory", {})
    check(ddt.get("chain") == "ADV-CHAIN-001", "defense_degradation_trajectory.chain = ADV-CHAIN-001")

# Check 6: Capability scorecard
print("\n--- 6. 能力评分卡 ---")
scorecard = load_yaml(os.path.join(RED_015_DIR, "capability_scorecard.yaml"))
if scorecard:
    check(scorecard.get("report_id") == "RED-015", "report_id = RED-015")
    chain_level = scorecard.get("chain_level", {})
    check(chain_level.get("confirmed_vulnerability") == False, "chain_level.confirmed_vulnerability = false")
    for s in EXPECTED_CHAIN_STAGES:
        check(s in scorecard.get("per_phase", {}), f"per_phase 包含 {s}")

# Check 7: Evidence candidates
print("\n--- 7. 红队证据候选 ---")
evidence = load_yaml(os.path.join(RED_015_DIR, "red_team_evidence_candidates.yaml"))
if evidence:
    ev_summary = evidence.get("evidence_summary", {})
    check(ev_summary.get("confirmed_vulnerability") == False, "confirmed_vulnerability = false")
    check(ev_summary.get("all_findings_are_candidate_level") == True, "all_findings_are_candidate_level = true")
    candidates = evidence.get("evidence_candidates", [])
    check(len(candidates) >= 6, f"至少 6 个证据候选 (实际: {len(candidates)})")

# Check 8: Blue control candidates
print("\n--- 8. 蓝队防护建议 ---")
blue = load_yaml(os.path.join(RED_015_DIR, "blue_control_candidates.yaml"))
if blue:
    bc_summary = blue.get("control_summary", {})
    check(bc_summary.get("confirmed_vulnerability") == False, "confirmed_vulnerability = false")
    candidates = blue.get("control_candidates", [])
    check(len(candidates) >= 4, f"至少 4 条防护建议 (实际: {len(candidates)})")

# Check 9: Purple retest candidates
print("\n--- 9. 紫队复测方案 ---")
purple = load_yaml(os.path.join(RED_015_DIR, "purple_retest_candidates.yaml"))
if purple:
    pr_summary = purple.get("retest_summary", {})
    check(pr_summary.get("confirmed_vulnerability") == False, "confirmed_vulnerability = false")
    candidates = purple.get("retest_candidates", [])
    check(len(candidates) >= 4, f"至少 4 条复测方案 (实际: {len(candidates)})")

# Check 10: Reused baseline index
print("\n--- 10. 复用基线索引 ---")
reused = load_yaml(os.path.join(RED_015_DIR, "reused_baseline_index.yaml"))
if reused:
    baselines = reused.get("reused_baselines", [])
    check(len(baselines) >= 4, f"至少 4 个复用基线 (实际: {len(baselines)})")
    r_summary = reused.get("reused_summary", {})
    check(r_summary.get("adversarial_playbooks", 0) >= 4, f"至少 4 个复用对抗剧本 (实际: {r_summary.get('adversarial_playbooks', 0)})")

# ====================================================================
# Check 11: Cross-file statistical consistency
# ====================================================================
print("\n--- 11. 跨文件统计一致性检查 ---")

def _is_http_429_or_error(entry):
    """Check if entry has HTTP 429, timeout, or execution error."""
    resp = entry.get("response_summary", "")
    if not resp:
        return False
    text = resp.lower()
    return any(sig in text for sig in [
        "http 429", "http_429", "http error 429",
        "exceeded the monthly usage",
        "api call failed after",
        "network_error", "max_retries",
        "timeout", "timed out",
        "empty_response", "hermes_not_found",
        "[error", "[http_error", "[network_error",
        "[timeout", "[empty",
    ])

def _is_control_by_id(case_id):
    """Detect control entries by case_id suffix pattern."""
    return case_id.endswith("-901") or case_id.endswith("-902")

# 11a. execution_results.json: detail -> summary consistency
results = load_json(os.path.join(RED_015_DIR, "execution_results.json"))
if results:
    r_entries = results.get("entries", [])
    r_summary = results.get("summary", {})
    r_total = len(r_entries)
    r_sum_total = r_summary.get("total_entries", 0)
    check(r_total == r_sum_total,
          f"entries count ({r_total}) == summary.total_entries ({r_sum_total})")

    # Compute from detail
    r_attack = sum(1 for e in r_entries if not _is_control_by_id(e.get("case_id", "")))
    r_control = sum(1 for e in r_entries if _is_control_by_id(e.get("case_id", "")))
    r_errors = sum(1 for e in r_entries if _is_http_429_or_error(e))
    r_non_error = [e for e in r_entries if not _is_http_429_or_error(e)]
    r_blocked = sum(1 for e in r_non_error if e.get("result") == "blocked")
    r_allowed = sum(1 for e in r_non_error if e.get("result") == "allowed")
    r_breakthroughs = sum(1 for e in r_non_error
                          if e.get("result") == "breakthrough_suspected"
                          and not _is_control_by_id(e.get("case_id", "")))

    check(r_attack == r_summary.get("attack_entries", 0),
          f"attack: detail ({r_attack}) == summary ({r_summary.get('attack_entries', 0)})")
    check(r_control == r_summary.get("control_entries", 0),
          f"control: detail ({r_control}) == summary ({r_summary.get('control_entries', 0)})")
    check(r_blocked == r_summary.get("blocked", 0),
          f"blocked: detail ({r_blocked}) == summary ({r_summary.get('blocked', 0)})")
    check(r_allowed == r_summary.get("allowed", 0),
          f"allowed: detail ({r_allowed}) == summary ({r_summary.get('allowed', 0)})")
    check(r_errors == r_summary.get("errors", 0),
          f"errors (HTTP 429/timeout): detail ({r_errors}) == summary ({r_summary.get('errors', 0)})")
    check(r_breakthroughs == r_summary.get("breakthrough_count", 0),
          f"breakthroughs: detail ({r_breakthroughs}) == summary ({r_summary.get('breakthrough_count', 0)})")

    # HTTP 429/error entries MUST NOT be counted as blocked or breakthrough
    error_as_blocked = sum(1 for e in r_entries
                           if _is_http_429_or_error(e) and e.get("result") == "blocked")
    error_as_bt = sum(1 for e in r_entries
                      if _is_http_429_or_error(e) and e.get("result") == "breakthrough_suspected")
    check(error_as_blocked == 0,
          f"HTTP 429/error NOT counted as blocked (found: {error_as_blocked})")
    check(error_as_bt == 0,
          f"HTTP 429/error NOT counted as breakthrough (found: {error_as_bt})")

    # Phase-level sum check
    phases = r_summary.get("chain_phases", {})
    ph_total_detail = sum(pd.get("total", 0) for pd in phases.values())
    check(ph_total_detail == r_sum_total,
          f"phase total sum ({ph_total_detail}) == overall total ({r_sum_total})")
    for stage, pd in phases.items():
        ph_sum = pd.get("blocked", 0) + pd.get("allowed", 0) + pd.get("breakthroughs", 0) + pd.get("errors", 0)
        check(ph_sum == pd.get("total", 0),
              f"  {stage}: blocked({pd.get('blocked',0)})+allowed({pd.get('allowed',0)})+bt({pd.get('breakthroughs',0)})+errors({pd.get('errors',0)})={ph_sum} == total({pd.get('total',0)})")

# 11b. red_015_result.yaml consistency with execution_results.json
result_yaml = load_yaml(os.path.join(RED_015_DIR, "red_015_result.yaml"))
if results and result_yaml:
    es = result_yaml.get("execution_summary", {})
    check(es.get("total_entries") == r_sum_total,
          f"result.yaml total ({es.get('total_entries')}) == exec_results total ({r_sum_total})")
    check(es.get("blocked") == r_blocked,
          f"result.yaml blocked ({es.get('blocked')}) == exec_results blocked ({r_blocked})")
    check(es.get("allowed") == r_allowed,
          f"result.yaml allowed ({es.get('allowed')}) == exec_results allowed ({r_allowed})")
    check(es.get("errors") == r_errors,
          f"result.yaml errors ({es.get('errors')}) == exec_results errors ({r_errors})")
    check(es.get("breakthroughs") == r_breakthroughs,
          f"result.yaml breakthroughs ({es.get('breakthroughs')}) == exec_results breakthroughs ({r_breakthroughs})")

# 11c. capability_scorecard.yaml consistency
scorecard = load_yaml(os.path.join(RED_015_DIR, "capability_scorecard.yaml"))
if results and scorecard:
    cl = scorecard.get("chain_level", {})
    check(cl.get("total_entries") == r_sum_total,
          f"scorecard total ({cl.get('total_entries')}) == exec_results total ({r_sum_total})")
    check(cl.get("blocked") == r_blocked,
          f"scorecard blocked ({cl.get('blocked')}) == exec_results blocked ({r_blocked})")
    check(cl.get("errors") == r_errors,
          f"scorecard errors ({cl.get('errors')}) == exec_results errors ({r_errors})")
    check(cl.get("breakthroughs") == r_breakthroughs,
          f"scorecard breakthroughs ({cl.get('breakthroughs')}) == exec_results breakthroughs ({r_breakthroughs})")
    # Phase-level consistency
    per_phase = scorecard.get("per_phase", {})
    for stage, pd in phases.items():
        sc_phase = per_phase.get(stage, {})
        check(sc_phase.get("total") == pd.get("total"),
              f"scorecard {stage}.total ({sc_phase.get('total')}) == summary {stage}.total ({pd.get('total')})")
        check(sc_phase.get("blocked") == pd.get("blocked"),
              f"scorecard {stage}.blocked ({sc_phase.get('blocked')}) == summary {stage}.blocked ({pd.get('blocked')})")
        check(sc_phase.get("errors") == pd.get("errors"),
              f"scorecard {stage}.errors ({sc_phase.get('errors')}) == summary {stage}.errors ({pd.get('errors')})")
        check(sc_phase.get("breakthroughs") == pd.get("breakthroughs"),
              f"scorecard {stage}.breakthroughs ({sc_phase.get('breakthroughs')}) == summary {stage}.breakthroughs ({pd.get('breakthroughs')})")

# 11d. Superseded data files check
chain_results_path = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..",
    "executions", "internal_security_assessment", "red_015_chain_results.json"
))
if os.path.exists(chain_results_path):
    chain_data = load_json(chain_results_path)
    if chain_data:
        check(chain_data.get("data_status") == "superseded",
              "red_015_chain_results.json marked as superseded")
        check("HTTP 429" in chain_data.get("superseded_reason", ""),
              "superseded_reason mentions HTTP 429 misclassification")

summary_path = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..",
    "executions", "internal_security_assessment", "assessment_summary.json"
))
if os.path.exists(summary_path):
    summary_data = load_json(summary_path)
    if summary_data:
        check(summary_data.get("data_status") == "superseded",
              "assessment_summary.json marked as superseded")

# ====================================================================
print("\n" + "=" * 60)
print(f"验证结果: {passed} 通过, {failed} 失败")
print("=" * 60)

if failed > 0:
    print("\n失败检查项:")
    for c in checks:
        if "❌" in c:
            print(c)
    sys.exit(1)
else:
    print("\n所有检查通过 ✅")
    sys.exit(0)
