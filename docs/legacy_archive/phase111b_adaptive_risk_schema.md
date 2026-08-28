# Phase-111B Adaptive Risk Schema Draft

**Status:** `candidate`
**Requires Human Review:** `true`

## Overview
This document outlines the schema for reporting adaptive attack residual risk, paralleling the static approach.

## Schema Definition
```yaml
adaptive_attack_residual_risk: acknowledged
assessment_type: adaptive
baseline_comparison:
  static_success_rate: float
  adaptive_success_rate: float
  degradation_factor: float
findings:
  - id: string
    scenario: string
    static_result: blocked | allowed
    adaptive_result: blocked | allowed
    adaptation_path: string
```

## Parallel Results MVP
| Scenario | Static Result | Adaptive Result | Defense Resilience |
|---|---|---|---|
| adapt_001 | Blocked | Allowed | Failed |
| adapt_002 | Blocked | Allowed | Failed |
| adapt_003 | Allowed | Allowed | N/A |
| adapt_004 | Blocked | Allowed | Failed |
| adapt_005 | Blocked | Blocked | Passed |
| adapt_006 | Blocked | Blocked | Passed |
| adapt_007 | Allowed | Allowed | N/A |
| adapt_008 | Blocked | Allowed | Failed |
| adapt_009 | Blocked | Blocked | Passed |
| adapt_010 | Blocked | Allowed | Failed |

Adaptive is strictly an enhancement of defense measurement (understanding how block evasion degrades defense efficacy), NOT an attack capability in itself.

