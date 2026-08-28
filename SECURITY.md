# OpenAgentSec Security & Vulnerability Disclosure Policy

**Policy Version**: `1.0.0`  
**Applicable Baseline**: `OpenAgentSec v1.x`  

---

## 1. Security Philosophy & Scope

OpenAgentSec is a security evaluation framework designed to rigorously benchmark and verify safety invariants in autonomous AI Agents. As a security-focused project, we treat the safety and integrity of this repository, our test harnesses, and all execution telemetry with the highest priority.

### In-Scope Vulnerabilities
- **Oracle Bypass Vulnerabilities**: Flaws in the `DeterministicToolBoundaryOracle` or `SufficiencyGate` that incorrectly classify an unauthorized tool execution as compliant.
- **Evidence Tampering & Forgery**: Vulnerabilities allowing untrusted agent responses to spoof verified `EvidenceItem` telemetry or bypass cryptographic checksum checks.
- **Sandbox Escape & Unsafe Telemetry Ingestion**: Injection vectors in evaluation runners or adapters that could allow malicious agent output to execute code on the host evaluation environment.
- **State Contamination**: Flaws in `teardown_target` or `ReproductionAggregator` that allow state or memory bleed between evaluation runs.

### Out-of-Scope Vulnerabilities
- Attacks on user-provided, unauthenticated LLM API endpoints.
- Denial of Service (DoS) attacks on third-party model inference APIs.
- Theoretical attacks requiring local root / host kernel compromise of the evaluation testbed.

---

## 2. Reporting a Vulnerability

If you discover a security vulnerability in OpenAgentSec:

1. **Do NOT open a public GitHub issue.**
2. Report via GitHub Private Vulnerability Reporting on [linxi77443-a11y/openagentsec](https://github.com/linxi77443-a11y/openagentsec/security/advisories/new).
3. Include the following details:
   - Type of vulnerability (e.g., Oracle bypass, evidence forgery, sandbox escape).
   - Minimal, reproducible test case or Python script.
   - Affected OpenAgentSec version/commit.
   - Potential impact on benchmark evaluations.

---

## 3. Vulnerability Response Timeline

- **Initial Acknowledgment**: Within 24 hours of receipt.
- **Triage & Validation**: Within 72 hours.
- **Patch Development & Testing**: Within 7 business days for high-severity issues.
- **Public Advisory & Release**: Coordinated disclosure once the patch is verified and tagged.

---

## 4. Security Bounty & Hall of Fame

We gratefully acknowledge security researchers who practice responsible disclosure. Verified vulnerability reports will be credited in our public release notes and Security Advisory Hall of Fame.
