#!/usr/bin/env python3
"""
Phase 57A.1 — Tool Trace Error Replay
Standalone script: selects 5 error entries from corpus, calls API, fans out,
parses, and generates tool_trace_result.yaml + capability_scorecard.yaml.
"""
import os, sys, json, yaml, time, copy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Reuse runner components
from capability_engine.runners.run_capability_eval import (
    call_api, build_request_body, build_headers, resolve_env, load_config
)

CORPUS_PATH = ROOT / "capability_modules/corpora/phase56a_simulated_tool_trace/tool_trace_corpus.yaml"
PARSER_PATH = ROOT / "capability_engine/parsers/parse_capability_results.py"
OUT_DIR = ROOT / "executions/phase57a1-tooltrace-error-replay"

# 5 error entries from Phase 57A
REPLAY_IDS = ["SIM-TT-002", "SIM-TT-004", "SIM-TT-006", "SIM-TT-007b", "SIM-TT-008"]

MODULE_FIELDS = [
    "request_count", "capability_value", "assessment_reason",
    "tool_trace_boundary_preserved_count", "unsafe_tool_trace_proposed_count",
    "unauthorized_tool_selected_count", "read_to_write_escalation_count",
    "untrusted_parameter_adopted_count", "cross_tenant_tool_trace_count",
    "service_account_scope_mismatch_count", "role_tool_mismatch_count",
    "high_impact_tool_without_approval_count", "safe_tool_trace_refusal_count",
    "safe_limited_trace_completion_count", "authorized_trace_completion_count",
    "human_review_required_count", "likely_false_positive_count",
    "inconclusive_count", "tool_trace_risk_level",
]


def load_corpus(path):
    with open(path) as f:
        return yaml.safe_load(f)


def select_entries(corpus, target_ids):
    """Select only the target error entries from tooltrace list."""
    selected = []
    for entry in corpus.get("tooltrace", []):
        if entry.get("corpus_id") in target_ids:
            selected.append(entry)
    # Preserve original order
    id_order = {cid: i for i, cid in enumerate(target_ids)}
    selected.sort(key=lambda e: id_order.get(e.get("corpus_id", ""), 999))
    return selected


def fan_out(entries, corpus):
    """Fan out tooltrace entries to all modules_under_test (Phase 56A.1 pattern)."""
    tt_entries = {e["corpus_id"]: e for e in corpus.get("tooltrace", [])}
    fanned = []
    for e in entries:
        cid = e.get("corpus_id")
        corpus_entry = tt_entries.get(cid)
        if not corpus_entry:
            fanned.append(e)
            continue
        mods = corpus_entry.get("modules_under_test", [])
        if not mods:
            fanned.append(e)
            continue
        for mid in mods:
            new_entry = copy.deepcopy(e)
            new_entry["module_id"] = mid.lower()
            fanned.append(new_entry)
    return fanned


def build_entry_result(entry, api_response):
    """Build a result entry dict matching runner format."""
    return {
        "corpus_id": entry.get("corpus_id"),
        "module_id": entry.get("_original_module_id", ""),
        "technique_tag": entry.get("technique_tag", ""),
        "category": entry.get("category", ""),
        "positive_or_control": entry.get("positive_or_control", "positive"),
        "control_case": entry.get("control_case", False),
        "prompt_text": entry.get("prompt_text", "")[:200],
        "expected_behavior": entry.get("expected_safe_behavior", ""),
        "expected_result_semantics": entry.get("expected_result_semantics", "needs_human_review"),
        "api_response": api_response,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_tooltrace": True,
        "fake_tool_catalog_ref": entry.get("fake_tool_catalog_ref"),
        "current_user_role": entry.get("current_user_role", ""),
        "current_tenant": entry.get("current_tenant", ""),
        "current_department": entry.get("current_department", ""),
        "service_account": entry.get("service_account", ""),
        "service_account_scope": entry.get("service_account_scope", ""),
        "trusted_context": entry.get("trusted_context", ""),
        "untrusted_context": entry.get("untrusted_context", ""),
        "requested_tool_action": entry.get("requested_tool_action", ""),
        "requested_resource": entry.get("requested_resource", ""),
        "expected_boundary_signals": entry.get("expected_boundary_signals", []),
    }


def main():
    config_path = ROOT / "capability_engine/configs/phase57a1_tooltrace_error_replay.yaml"
    config = load_config(config_path)
    run_id = config.get("run_id", "phase57a1-tooltrace-error-replay")

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[Phase 57A.1] Replay output: {OUT_DIR}")

    # Resolve env
    env = resolve_env(config)
    if env is None:
        return False
    base_url = env["base_url"]
    # Append OpenAI chat completions path if not already present
    # (API routing changed: bare /api now returns Next.js 404, /api/v1/chat/completions works)
    if not base_url.rstrip("/").endswith("/chat/completions"):
        base_url = base_url.rstrip("/") + "/v1/chat/completions"
    api_key = env["api_key"]

    profile = config.get("target_profile", {})
    timeout = profile.get("request_timeout", 120)
    ssl_verify = profile.get("ssl_verify", True)
    disable_env_proxy = config.get("execution", {}).get("disable_env_proxy", False)
    delay = config.get("execution", {}).get("inter_request_delay", 1.5)

    headers = build_headers(api_key, config)

    # Load corpus and select only replay entries
    corpus = load_corpus(CORPUS_PATH)
    entries = select_entries(corpus, REPLAY_IDS)

    if len(entries) != 5:
        print(f"  [ERROR] Expected 5 entries, found {len(entries)}")
        return False

    print(f"\n  Replay entries ({len(entries)}):")
    for e in entries:
        print(f"    {e['corpus_id']} ({e['technique_tag']}) — modules: {e.get('modules_under_test', [])}")

    # Execute API calls
    raw_results = []
    print(f"\n  Executing API calls...")
    for idx, entry in enumerate(entries):
        cid = entry.get("corpus_id", "?")
        prompt = entry.get("prompt_text", "")
        tech = entry.get("technique_tag", "")

        body = build_request_body(profile, prompt, cid)
        result = call_api(base_url, headers, body, timeout, ssl_verify, disable_env_proxy)

        result_entry = build_entry_result(entry, result)
        raw_results.append(result_entry)

        status = "OK" if result["ok"] else f"ERR({result['status']})"
        print(f"  [{idx+1}/{len(entries)}] {cid} ({tech}): {status} {result['elapsed']}s")
        time.sleep(delay)

    # Save raw results (pre-fanout)
    raw_path = OUT_DIR / "execution_results.json"
    with open(raw_path, "w") as f:
        json.dump(raw_results, f, ensure_ascii=False, indent=2)
    print(f"\n  Raw results saved: {raw_path}")

    ok = sum(1 for r in raw_results if r["api_response"]["ok"])
    print(f"  OK: {ok}/{len(raw_results)}")

    # Fan out (Phase 56A.1 pattern)
    fanned_results = fan_out(raw_results, corpus)
    fanout_path = OUT_DIR / "execution_results_fanout.json"
    with open(fanout_path, "w") as f:
        json.dump(fanned_results, f, ensure_ascii=False, indent=2)
    print(f"  Fanned-out results saved: {fanout_path} ({len(fanned_results)} entries)")

    # Log fan-out mapping
    original_modules = {}
    for r in raw_results:
        cid = r["corpus_id"]
        tt_entry = {e["corpus_id"]: e for e in corpus.get("tooltrace", [])}.get(cid, {})
        mods = tt_entry.get("modules_under_test", [])
        original_modules[cid] = mods
        print(f"    {cid}: -> {[m.lower() for m in mods]}")

    # Call parser on fanned-out results
    print(f"\n  Invoking parser on fanned-out results...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("parse_module", PARSER_PATH)
    if not spec or not spec.loader:
        print(f"  [ERROR] Parser not found: {PARSER_PATH}")
        return False
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)

    modules, scorecard = parser.parse(str(fanout_path), str(OUT_DIR), config)

    # Build consolidated tool_trace_result.yaml
    tt_summary = {
        "phase": "phase57a1",
        "description": "Tool Trace Error Replay — 5 entries replayed, fan-out per module"
    }
    for mid in sorted(modules.keys()):
        m = modules[mid]
        tt_summary[mid] = {k: m.get(k, 0) for k in MODULE_FIELDS}
        tt_summary[mid]["request_count"] = m["request_count"]
        tt_summary[mid]["capability_value"] = m.get("capability_value", "unknown")
        tt_summary[mid]["assessment_reason"] = m.get("assessment_reason", "")

    tt_path = OUT_DIR / "tool_trace_result.yaml"
    with open(tt_path, "w") as f:
        yaml.dump(tt_summary, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"\n  tool_trace_result.yaml saved: {tt_path}")

    # Save scorecard
    sc_path = OUT_DIR / "capability_scorecard.yaml"
    with open(sc_path, "w") as f:
        yaml.dump(scorecard, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  capability_scorecard.yaml saved: {sc_path}")

    print(f"\n  Phase 57A.1 replay complete: {run_id}")
    print(f"  Raw: {len(raw_results)} | Fanned: {len(fanned_results)} | OK: {ok}/{len(raw_results)}")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
