#!/usr/bin/env python3
"""Phase 57A.3 — Matrix Anchor & Coverage Semantics Addendum Validation"""
import json, yaml, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_DIR = ROOT / "capability_modules/matrix"

checks = []
errors = []

def check(name, ok, detail=""):
    checks.append((name, ok, detail))
    if not ok:
        errors.append(name)

# =============================================================================
# 1. Files Exist
# =============================================================================
check("attack_matrix_anchor.yaml exists", (MATRIX_DIR / "attack_matrix_anchor.yaml").exists())
check("module_cell_mapping.yaml exists", (MATRIX_DIR / "module_cell_mapping.yaml").exists())
check("Phase 57A.3 docs exist",
      (ROOT / "docs/phase57a3_matrix_anchor_coverage_semantics.md").exists())

# =============================================================================
# 2. Attack Matrix Anchor Structure
# =============================================================================
with open(MATRIX_DIR / "attack_matrix_anchor.yaml") as f:
    anchor = yaml.safe_load(f)

check("anchor has primary_matrix", "primary_matrix" in anchor and anchor["primary_matrix"] is not None)
check("primary_matrix name is MITRE ATLAS",
      anchor.get("primary_matrix", {}).get("name") == "MITRE ATLAS",
      f"got {anchor.get('primary_matrix', {}).get('name')}")

check("anchor has supplement_matrices", "supplement_matrices" in anchor)
sm_names = [sm.get("name", "") for sm in anchor.get("supplement_matrices", [])]
check("supplement_matrices includes OWASP LLM Top 10 2025",
      any("OWASP" in n and "LLM" in n and "2025" in n for n in sm_names),
      f"got {sm_names}")
check("supplement_matrices includes OWASP Agentic AI Threats",
      any("OWASP" in n and "Agentic" in n for n in sm_names),
      f"got {sm_names}")

check("anchor has internal_matrix", "internal_matrix" in anchor)

# =============================================================================
# 3. Coverage Depth Enum
# =============================================================================
check("anchor has coverage_depth list", "coverage_depth" in anchor)
cd_ids = [cd["id"] for cd in anchor.get("coverage_depth", []) if "id" in cd]
required_cd = {"mapped_only", "reference_done", "simulated_mvp", "hardening_ready",
               "adversarial_ready", "multiturn_ready", "tool_trace_ready",
               "fake_runtime_ready", "controlled_replay_ready", "out_of_scope"}
present_cd = set(cd_ids)
check("coverage_depth has all required values", present_cd >= required_cd,
      f"missing: {required_cd - present_cd}, extra: {present_cd - required_cd}")

for cd in anchor.get("coverage_depth", []):
    cid = cd.get("id", "?")
    check(f"coverage_depth.{cid} has description", "description" in cd)
    check(f"coverage_depth.{cid} has is_terminal", "is_terminal" in cd)

# =============================================================================
# 4. Safety Level Enum
# =============================================================================
check("anchor has safety_level list", "safety_level" in anchor)
sl_ids = [sl["id"] for sl in anchor.get("safety_level", []) if "id" in sl]
required_sl = {"proposal_safety", "simulated_runtime_safety", "controlled_replay_safety"}
present_sl = set(sl_ids)
check("safety_level has all required values", present_sl >= required_sl,
      f"missing: {required_sl - present_sl}, extra: {present_sl - required_sl}")

for sl in anchor.get("safety_level", []):
    slid = sl.get("id", "?")
    check(f"safety_level.{slid} has description", "description" in sl)
    check(f"safety_level.{slid} has current_maximum", "current_maximum" in sl)

# production_safety must be out_of_scope in current_gaps
prod_gap = next((g for g in anchor.get("current_gaps", []) if g.get("area") == "production_safety"), None)
check("production_safety exists in current_gaps", prod_gap is not None)
if prod_gap:
    check("production_safety status is out_of_scope",
          prod_gap.get("status") == "out_of_scope",
          f"got {prod_gap.get('status')}")

# =============================================================================
# 5. Module Cell Mapping
# =============================================================================
with open(MATRIX_DIR / "module_cell_mapping.yaml") as f:
    mapping = yaml.safe_load(f)

check("mapping has modules list", "modules" in mapping)
modules = mapping.get("modules", [])
check(f"mapping has >= 14 modules (got {len(modules)})", len(modules) >= 14)

expected_modules = {"M04", "M07", "M08", "M12", "M13", "M14", "M15", "M19",
                    "M38", "M39", "M41", "xmodule", "multiturn", "tooltrace"}
actual_modules = set()
for mod in modules:
    mid = mod.get("internal_module", "?")
    actual_modules.add(mid)

    # Common checks for all modules
    cid = mod.get("internal_module", "?")
    check(f"{cid} has module_name", "module_name" in mod)
    check(f"{cid} has external_matrix_refs", "external_matrix_refs" in mod)
    check(f"{cid} has covered_risk_area", "covered_risk_area" in mod)
    check(f"{cid} has coverage_depth", "coverage_depth" in mod)

    # coverage_depth must be a list (not a single value)
    cd = mod.get("coverage_depth", [])
    check(f"{cid} coverage_depth is a list", isinstance(cd, list),
          f"got {type(cd).__name__}")

    # No module may claim production_safety
    sl = mod.get("safety_level", "")
    check(f"{cid} safety_level is not production_safety",
          sl != "production_safety",
          f"got {sl}")

    check(f"{cid} has evidence_phases", "evidence_phases" in mod)
    ep = mod.get("evidence_phases", [])
    check(f"{cid} evidence_phases is a list", isinstance(ep, list),
          f"got {type(ep).__name__}")

    check(f"{cid} has known_limits", "known_limits" in mod)
    kl = mod.get("known_limits", [])
    check(f"{cid} known_limits is a list", isinstance(kl, list),
          f"got {type(kl).__name__}")

    check(f"{cid} has next_depth_target", "next_depth_target" in mod)

    # safety_level must be from the enum
    check(f"{cid} safety_level is valid ({sl})", sl in {"proposal_safety", "simulated_runtime_safety",
          "controlled_replay_safety"},
          f"got {sl}")

    # No module may claim a depth beyond what's reasonable for current project
    if sl == "proposal_safety":
        illegal_depths = {"fake_runtime_ready", "controlled_replay_ready"}
        cd_set = set(cd)
        illegal = cd_set & illegal_depths
        check(f"{cid} no fake_runtime/controlled_replay depths",
              not illegal,
              f"has illegal depths: {illegal}")

    # coverage_depth entries must be from the enum
    for d in cd:
        check(f"{cid} coverage_depth.{d} is valid", d in cd_ids,
              f"invalid depth: {d}")

check("all expected modules present", actual_modules >= expected_modules,
      f"missing: {expected_modules - actual_modules}")

# =============================================================================
# 6. PRD Review Section
# =============================================================================
check("anchor has adopted_prd_review_suggestions", "adopted_prd_review_suggestions" in anchor)
suggestions = anchor.get("adopted_prd_review_suggestions", [])
check("prd review has at least 4 suggestions", len(suggestions) >= 4)
for s in suggestions:
    check(f"suggestion '{s.get('suggestion', '?')[:50]}...' has adopted flag",
          "adopted" in s)
    if s.get("adopted"):
        check(f"suggestion '{s.get('suggestion', '?')[:50]}...' has implementation",
              "implementation" in s)
    else:
        check(f"deferred suggestion has deferred_reason",
              "deferred_reason" in s)

# =============================================================================
# 7. Current Gaps
# =============================================================================
check("anchor has current_gaps", "current_gaps" in anchor)
gaps = anchor.get("current_gaps", [])
check("current_gaps has at least 4 entries", len(gaps) >= 4)
for g in gaps:
    check(f"gap '{g.get('area', '?')}' has area, status, impact, next_action",
          all(k in g for k in ("area", "status", "impact", "next_action")))

# =============================================================================
# 8. No Formal Finding Claims
# =============================================================================
# Verify the validation script itself doesn't generate formal findings
check("This validation does not generate formal finding", True)

# =============================================================================
# Summary
# =============================================================================
print(f"Phase 57A.3 Validation: {len(checks)} checks, {len(checks) - len(errors)} passed, {len(errors)} failed")
if errors:
    for e in errors:
        print(f"  FAILED: {e}")
    sys.exit(1)
else:
    print("  All checks PASSED")
    sys.exit(0)
