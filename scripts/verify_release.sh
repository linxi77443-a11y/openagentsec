#!/usr/bin/env bash
# OpenAgentSec Release Verification Script (PRD v4.0.2 Phase 7.6.4)
set -euo pipefail

echo "========================================="
echo " Verifying OpenAgentSec Release Artifacts"
echo "========================================="

# 1. Version and Core Files
echo "[1/4] Checking release metadata files..."
test -f VERSION
test -f CHANGELOG.md
test -f CITATION.cff
test -f CONTRIBUTING.md
test -f README.md
echo "-> Metadata files verified: OK"

# 2. Research and Release Docs
echo "[2/4] Checking research and release documentation..."
test -f docs/research/openagentsec_technical_report.md
test -f docs/research/threat_model.md
test -f docs/research/evaluation_methodology.md
test -f docs/research/benchmark_specification.md
test -f docs/research/limitations_and_future_work.md
test -f docs/research/citation.md
test -f docs/release/quick_start.md
test -f docs/release/demo_workflow.md
test -f docs/release/benchmark_results.md
test -f docs/release/contribution_guide.md
test -f docs/release/release_checklist.md
test -f docs/release/user_journey_validation.md
echo "-> Documentation verified: OK"

# 3. Artifact Manifest and JSON Exports
echo "[3/4] Checking research artifact JSON files..."
test -f artifact/MANIFEST.json
test -f artifact/benchmark/benchmark_v1.0.0.json
test -f artifact/benchmark/scenarios.json
test -f artifact/benchmark/metrics.json
test -f artifact/benchmark/targets.json
test -f artifact/benchmark/adaptive_scenarios.json
test -f artifact/experiments/reproduction_matrix.json
test -f artifact/experiments/benchmark_results.json
test -f artifact/schemas/target_profile.schema.json
test -f artifact/schemas/evidence.schema.json
test -f artifact/schemas/result.schema.json
test -f artifact/schemas/mutation.schema.json
echo "-> Artifact JSON files verified: OK"

# 4. Integration and Validation Tests
echo "[4/4] Executing test suite..."
pytest tests/integration/planner/ tests/integration/external_validation/ tests/integration/release_validation/ -v

echo "========================================="
echo " All release criteria verified: SUCCESS!"
echo "========================================="
