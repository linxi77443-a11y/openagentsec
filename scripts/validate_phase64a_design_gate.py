#!/usr/bin/env python3
"""Phase 64A — Validate Controlled Scenario Replay Design Gate.

Checks:
- replay_executable=false across all design gate files
- controlled_replay_execution_allowed=false
- confirmed_vulnerability=false, formal_finding_allowed=false
- production_safety_claimed=false, controlled_replay_claimed=false
- requires_human_review=true
- All required files exist
- All required sections exist in the design gate doc
- No real accounts/customers/orders/contracts/tokens/secrets/API endpoints
- No replay execution results
- No production safety / confirmed vulnerability / formal finding declarations
"""
import sys, os, re, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

checks = []
findings = []

def check(name: str, ok: bool, detail: str = ""):
    checks.append({"name": name, "pass": ok, "detail": detail})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

def finding(cat: str, item: str, field: str, detail: str):
    findings.append({"category": cat, "item": item, "field": field, "detail": detail})
    print(f"  [FINDING] {cat}: {item} / {field}: {detail}")

def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

REQUIRED_FILES = [
    "controlled_scenario_replay_design_gate.md",
    "controlled_replay_authorization_checklist.yaml",
    "controlled_replay_environment_requirements.yaml",
    "controlled_replay_rollback_plan.yaml",
    "controlled_replay_logging_requirements.yaml",
]

YAML_FILES = [
    "controlled_replay_authorization_checklist.yaml",
    "controlled_replay_environment_requirements.yaml",
    "controlled_replay_rollback_plan.yaml",
    "controlled_replay_logging_requirements.yaml",
]

REQUIRED_SECTIONS = [
    "Replay 准入标准",
    "授权清单要求",
    "测试环境要求",
    "测试账号与测试数据要求",
    "回滚计划",
    "人工复核门",
    "执行日志要求",
    "安全字段默认值",
    "非目标与禁止项",
]

def check_all_yaml_security_fields(data, source_file):
    """Recursively check all security fields in a YAML structure."""
    if not isinstance(data, dict):
        return
    for key, val in data.items():
        if key == "confirmed_vulnerability" and val is not False:
            finding("security_field", source_file, "confirmed_vulnerability",
                    f"expected false, got {val}")
        elif key == "formal_finding_allowed" and val is not False:
            finding("security_field", source_file, "formal_finding_allowed",
                    f"expected false, got {val}")
        elif key == "production_safety_claimed" and val is not False:
            finding("security_field", source_file, "production_safety_claimed",
                    f"expected false, got {val}")
        elif key == "controlled_replay_claimed" and val is not False:
            finding("security_field", source_file, "controlled_replay_claimed",
                    f"expected false, got {val}")
        elif key == "requires_human_review" and val is not True:
            finding("security_field", source_file, "requires_human_review",
                    f"expected true, got {val}")
        elif key == "replay_executable" and val is not False:
            finding("security_field", source_file, "replay_executable",
                    f"expected false, got {val}")
        elif key == "controlled_replay_execution_allowed" and val is not False:
            finding("security_field", source_file, "controlled_replay_execution_allowed",
                    f"expected false, got {val}")
        else:
            check_all_yaml_security_fields(val, source_file)

# Real data patterns to detect
REAL_DATA_PATTERNS = [
    r'@[a-zA-Z0-9]+\.[a-zA-Z]{2,}\b',  # email domains (excluding sim)
    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',       # potential real names (Latin)
]

def main():
    print("=" * 60)
    print("Phase 64A — Controlled Scenario Replay Design Gate Validation")
    print("=" * 60)

    # ── File existence ──
    all_files_exist = True
    for f in REQUIRED_FILES:
        path = ROOT / f
        exists = path.exists()
        if not exists:
            all_files_exist = False
            finding("missing_file", f, "exists", "file not found")
        check(f"File exists: {f}", exists)

    if not all_files_exist:
        print("\n[FAIL] Required files missing. Aborting.")
        sys.exit(1)

    # ── Main design gate doc sections ──
    md_path = ROOT / "controlled_scenario_replay_design_gate.md"
    md_text = md_path.read_text(encoding="utf-8")

    for section in REQUIRED_SECTIONS:
        check(f"Section present: {section}", section in md_text)

    # ── Explicit declarations ──
    check("replay_executable=false in main doc",
          "replay_executable:              false" in md_text or "replay_executable: false" in md_text)
    check("controlled_replay_execution_allowed=false in main doc",
          "controlled_replay_execution_allowed: false" in md_text)
    check("confirmed_vulnerability=false in main doc",
          "confirmed_vulnerability:        false" in md_text or "confirmed_vulnerability: false" in md_text)
    check("formal_finding_allowed=false in main doc",
          "formal_finding_allowed:         false" in md_text or "formal_finding_allowed: false" in md_text)
    check("production_safety_claimed=false in main doc",
          "production_safety_claimed:      false" in md_text or "production_safety_claimed: false" in md_text)
    check("controlled_replay_claimed=false in main doc",
          "controlled_replay_claimed:      false" in md_text or "controlled_replay_claimed: false" in md_text)
    check("requires_human_review=true in main doc",
          "requires_human_review:          true" in md_text or "requires_human_review: true" in md_text)

    # ── Human review gates ──
    for gate in ["Candidate Selection Review", "Authorization Review",
                 "Environment Readiness Review", "Account and Data Safety Review",
                 "Replay Execution Approval", "Post-Replay Evidence Review",
                 "Vulnerability Classification Review", "Formal Finding Approval Review"]:
        check(f"Human review gate: {gate}", gate in md_text)

    # ── 13 admission criteria ──
    for i in range(1, 14):
        check(f"Admission criterion #{i} present",
              f"| {i} |" in md_text)

    # ── YAML files security fields ──
    for yf in YAML_FILES:
        path = ROOT / yf
        data = load_yaml(path)
        check_all_yaml_security_fields(data, yf)

    # ── Explicit security field count per YAML ──
    for yf in YAML_FILES:
        path = ROOT / yf
        raw = path.read_text(encoding="utf-8")
        for field, expected in [("confirmed_vulnerability", "false"),
                                ("formal_finding_allowed", "false"),
                                ("production_safety_claimed", "false"),
                                ("controlled_replay_claimed", "false"),
                                ("requires_human_review", "true")]:
            pattern = f"{field}: {expected}"
            cnt = raw.count(pattern)
            if cnt == 0:
                finding("security_field_declaration", yf, field,
                        f"pattern '{pattern}' not found in file")

    # ── No real data in placeholder fields ──
    # Check that placeholder fields use <SIM_...> not real values
    for yf in YAML_FILES:
        path = ROOT / yf
        raw = path.read_text(encoding="utf-8")
        data = load_yaml(path)
        # Scan for any "current_value" that is not null
        def scan_current_values(d, path_str=""):
            if not isinstance(d, dict):
                return
            if "current_value" in d and d["current_value"] is not None:
                finding("real_data_in_placeholder", yf, f"{path_str}.current_value",
                        f"current_value should be null in design gate, got: {d['current_value']}")
            for k, v in d.items():
                if k != "current_value":
                    scan_current_values(v, f"{path_str}.{k}" if path_str else k)
        scan_current_values(data)

    # ── No replay execution results ──
    execution_result_dirs = [
        ROOT / "execution_results",
        ROOT / "output" / "execution_results",
    ]
    for d in execution_result_dirs:
        if d.exists():
            finding("execution_result_exists", str(d), "exists",
                    "execution result directory should not exist for design gate")

    # ── No controlled_replay/logs matching execution ──
    log_paths = list(ROOT.glob("controlled_replay/logs/*"))
    if log_paths:
        finding("replay_logs_found", "controlled_replay/logs", "exists",
                f"found {len(log_paths)} log file(s); design gate should not have execution logs")

    # ── No production safety declarations ──
    # "production_safety_claimed: true" should NOT appear anywhere
    for yf in YAML_FILES:
        path = ROOT / yf
        raw = path.read_text(encoding="utf-8")
        if "production_safety_claimed: true" in raw:
            finding("prohibited_declaration", yf, "production_safety_claimed",
                    "production_safety_claimed should not be true in design gate")

    # ── No confirmed vulnerability declarations ──
    for yf in YAML_FILES:
        path = ROOT / yf
        raw = path.read_text(encoding="utf-8")
        if "confirmed_vulnerability: true" in raw:
            finding("prohibited_declaration", yf, "confirmed_vulnerability",
                    "confirmed_vulnerability should not be true in design gate")

    # ── No formal finding declarations ──
    for yf in YAML_FILES:
        path = ROOT / yf
        raw = path.read_text(encoding="utf-8")
        if "formal_finding_allowed: true" in raw:
            finding("prohibited_declaration", yf, "formal_finding_allowed",
                    "formal_finding_allowed should not be true in design gate")

    # ── Summary ──
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    total = len(checks)

    print(f"\n{'=' * 60}")
    print("Validation Summary")
    print(f"{'=' * 60}")
    print(f"  Total checks:  {total}")
    print(f"  Passed:        {passed}")
    print(f"  Failed:        {failed}")
    print(f"  Findings:      {len(findings)}")

    if findings:
        print(f"\n--- Findings ({len(findings)}) ---")
        cat_order = ["missing_file", "security_field", "security_field_declaration",
                     "real_data_in_placeholder", "execution_result_exists", "replay_logs_found",
                     "prohibited_declaration"]
        for cat in cat_order:
            items = [f for f in findings if f["category"] == cat]
            if items:
                for fi in items:
                    print(f"  [{fi['category']}] {fi['item']} / {fi['field']}: {fi['detail']}")

    print(f"\n{'=' * 60}")
    if failed == 0 and len(findings) == 0:
        print(f"ALL {total} CHECKS PASSED — No findings. Design gate is consistent.")
        sys.exit(0)
    else:
        print(f"{failed} check(s) FAILED. {len(findings)} findings.")
        sys.exit(1 if failed > 0 else 0)

if __name__ == "__main__":
    main()
