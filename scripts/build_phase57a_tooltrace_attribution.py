#!/usr/bin/env python3
"""
Phase 57A — Tool Trace Full Corpus Fan-out Attribution
Post-process script: reads Phase 57A execution_results.json, fans out each
tool trace entry to all modules_under_test, re-runs Phase 56A.2 calibrated parser.
No API re-call.
"""
import json, yaml, sys, os, copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PARSER_PATH = ROOT / "capability_engine/parsers/parse_capability_results.py"
CORPUS_PATH = ROOT / "capability_modules/corpora/phase56a_simulated_tool_trace/tool_trace_corpus.yaml"
SRC_EXEC_DIR = ROOT / "executions/phase57a-simulated-tool-trace-full"
CONFIG_PATH = ROOT / "capability_engine/configs/phase57a_simulated_tool_trace_full_run.yaml"

def main():
    # 1. Read execution results
    src_path = SRC_EXEC_DIR / "execution_results.json"
    if not src_path.exists():
        print(f"[ERROR] Source not found: {src_path}")
        return False
    with open(src_path) as f:
        original_results = json.load(f)

    # 2. Read corpus for modules_under_test mapping
    if not CORPUS_PATH.exists():
        print(f"[ERROR] Corpus not found: {CORPUS_PATH}")
        return False
    with open(CORPUS_PATH) as f:
        corpus = yaml.safe_load(f)
    tt_entries = {e["corpus_id"]: e for e in corpus.get("tooltrace", [])}

    # 3. Fan out
    fanned_results = []
    fan_out_log = []
    for r in original_results:
        cid = r["corpus_id"]
        corpus_entry = tt_entries.get(cid)
        if not corpus_entry or not r.get("is_tooltrace", False):
            fanned_results.append(r)
            continue
        mods = corpus_entry.get("modules_under_test", [])
        if not mods:
            fanned_results.append(r)
            continue
        first = True
        for mid in mods:
            mid_lower = mid.lower()
            new_entry = copy.deepcopy(r)
            new_entry["module_id"] = mid_lower
            fan_out_log.append(f"  {cid}: {r['module_id']} -> {mid_lower}")
            fanned_results.append(new_entry)

    # 4. Save fanned-out results to dedicated file (never overwrite raw 16)
    out_results_path = SRC_EXEC_DIR / "execution_results_fanout_36.json"
    with open(out_results_path, "w") as f:
        json.dump(fanned_results, f, ensure_ascii=False, indent=2)

    print(f"Fan-out complete:")
    print(f"  Original entries: {len(original_results)}")
    print(f"  Fanned-out entries: {len(fanned_results)}")
    for line in fan_out_log:
        print(line)

    # 5. Re-run parser
    import importlib.util
    spec = importlib.util.spec_from_file_location("parse_module", PARSER_PATH)
    if not spec or not spec.loader:
        print(f"[ERROR] Parser not found: {PARSER_PATH}")
        return False
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)

    run_config = None
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            run_config = yaml.safe_load(f)

    modules, scorecard = parser.parse(str(out_results_path), str(SRC_EXEC_DIR), run_config)

    # 6. Build consolidated tool_trace_result.yaml
    tt_summary = {
        "phase": "phase57a",
        "description": "Tool Trace Full Corpus — fanned-out per-module results"
    }
    for mid in sorted(modules.keys()):
        m = modules[mid]
        tt_summary[mid] = {
            "request_count": m["request_count"],
            "capability_value": m["capability_value"],
            "assessment_reason": m.get("assessment_reason", ""),
            "tool_trace_boundary_preserved_count": m.get("tool_trace_boundary_preserved_count", 0),
            "unsafe_tool_trace_proposed_count": m.get("unsafe_tool_trace_proposed_count", 0),
            "unauthorized_tool_selected_count": m.get("unauthorized_tool_selected_count", 0),
            "read_to_write_escalation_count": m.get("read_to_write_escalation_count", 0),
            "untrusted_parameter_adopted_count": m.get("untrusted_parameter_adopted_count", 0),
            "cross_tenant_tool_trace_count": m.get("cross_tenant_tool_trace_count", 0),
            "service_account_scope_mismatch_count": m.get("service_account_scope_mismatch_count", 0),
            "role_tool_mismatch_count": m.get("role_tool_mismatch_count", 0),
            "high_impact_tool_without_approval_count": m.get("high_impact_tool_without_approval_count", 0),
            "safe_tool_trace_refusal_count": m.get("safe_tool_trace_refusal_count", 0),
            "safe_limited_trace_completion_count": m.get("safe_limited_trace_completion_count", 0),
            "authorized_trace_completion_count": m.get("authorized_trace_completion_count", 0),
            "human_review_required_count": m.get("human_review_required_count", 0),
            "likely_false_positive_count": m.get("likely_false_positive_count", 0),
            "inconclusive_count": m.get("inconclusive_count", 0),
            "tool_trace_risk_level": m.get("tool_trace_risk_level", "unknown"),
        }

    tt_path = SRC_EXEC_DIR / "tool_trace_result.yaml"
    with open(tt_path, "w") as f:
        yaml.dump(tt_summary, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\nConsolidated tool_trace_result.yaml saved: {tt_path}")
    print(f"Modules in scorecard: {sorted(modules.keys())}")
    print(f"Phase 57A fan-out complete")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
