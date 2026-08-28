#!/usr/bin/env bash
# OpenAgentSec Benchmark Runner Script (PRD v4.0.2 Phase 7.6.4)
set -euo pipefail

echo "========================================="
echo " Running OpenAgentSec Benchmark Suite"
echo "========================================="

pytest tests/integration/planner/ tests/integration/external_validation/ tests/integration/release_validation/ -v

echo "========================================="
echo " Benchmark run complete!"
echo "========================================="
