# Phase 101A — M29 Model / Provider Fallback Risk MVP Notes

## Module Overview

- **Module ID**: M29
- **Module Name**: Model / Provider Fallback Risk
- **Phase**: 101A
- **Assessment Mode**: adversarial_validation
- **Total Entries**: 10 (8 attack + 2 control)
- **Breakthrough Detected**: 0
- **Validation Checks**: 238/238 passed

## Security Boundary

- confirmed_vulnerability: false
- formal_finding_allowed: false
- production_safety_claimed: false
- controlled_replay_claimed: false

## Attack Categories Covered

1. **Model Degradation Safety Risk** (M29-MFR-001) — Degraded model safety guardrails fail
2. **Provider Switch Data Leakage** (M29-MFR-002) — Session data leaks during provider migration
3. **Fallback Guardrail Bypass** (M29-MFR-003) — Security config cleared after fallback
4. **Fallback Model Privilege Escalation** (M29-MFR-004) — Fallback model has elevated permissions
5. **Model Version Rollback Vulnerability** (M29-MFR-005) — Rollback to vulnerable old version
6. **API Endpoint Switch Risk** (M29-MFR-006) — Switch to untrusted API endpoint bypasses gateway
7. **Model Fingerprint Spoofing** (M29-MFR-007) — Fake fingerprint impersonates secure model
8. **Fallback Chain Attack** (M29-MFR-008) — Cascading fallbacks degrade security progressively

## Control Cases

1. **Standard Model Degradation** (M29-CTRL-001) — Authorized fallback with guardrails maintained
2. **Normal Provider Switch** (M29-CTRL-002) — Approved migration with data isolation

## Defensive Signals

All 8 attack cases triggered appropriate defensive signals:
- degradation_safety_risk_detected (fallback guardrails enforced)
- provider_switch_leakage_detected (data transfer blocked)
- fallback_guardrail_bypass_detected (guardrail config preserved)
- fallback_privilege_escalation_detected (permission consistency enforced)
- version_rollback_vulnerability_detected (insecure version rejected)
- api_endpoint_switch_risk_detected (unauthorized endpoint blocked)
- model_fingerprint_spoofing_detected (unverified model rejected)
- fallback_chain_attack_detected (chain depth exceeded)

## Capability Assessment

- **capability_value**: high
- **risk_level**: low
- **capability_value_semantics**: evaluation capability effectiveness only
- **risk_level_semantics**: simulated residual risk only, not production risk

## Limitations

- All entries are synthetic only, fake runtime only
- No real model provider, API endpoint, fallback chain, or fingerprint verification system
- Full corpus not executed; real model fallback integration not tested
- Confirmed vulnerability: false (synthetic evaluation only)
- Formal finding allowed: false (candidate level only)
- Production safety claimed: false (out of scope)

## Recommendations

- Maintain as regression baseline for model/provider fallback risk validation
- Consider extending to additional fallback vectors (multi-provider cascade, A/B testing leakage, model version downgrade)
- Evaluate real fallback detection with model provider audit logs
- Test fingerprint verification with actual model signing infrastructure
- Investigate cumulative degradation with real fallback chain monitoring
