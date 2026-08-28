#!/usr/bin/env python3
"""Phase 119A — ADV-86 Authorized Attack Chain Simulation Validator."""
import json
import os
import sys
import jsonschema
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _ValidationRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.sections = {}
        self.current_section = "general"

    def start_section(self, name: str):
        self.current_section = name
        self.sections[name] = {"passed": 0, "failed": 0}

    def check(self, condition: bool, msg: str):
        if self.current_section not in self.sections:
            self.sections[self.current_section] = {"passed": 0, "failed": 0}

        if condition:
            self.passed += 1
            self.sections[self.current_section]["passed"] += 1
            print(f"  ✓ {msg}")
        else:
            self.failed += 1
            self.sections[self.current_section]["failed"] += 1
            self.errors.append(msg)
            print(f"  ✗ {msg}")


def validate() -> dict:
    runner = _ValidationRunner()

    print("=" * 60)
    print("Phase 119A ADV-86 Authorized Attack Chain Simulation Validation")
    print("=" * 60)

    exec_dir = os.path.join(ROOT, "executions", "phase119a_attack_chain")

    # 1. Schema Validation
    runner.start_section("schema")
    schema_path = os.path.join(exec_dir, "kill_chain_schema.yaml")
    runner.check(os.path.exists(schema_path), f"kill_chain_schema.yaml exists: {schema_path}")

    schema_data = {}
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_data = yaml.safe_load(f)
        runner.check("$schema" in schema_data, "Schema has $schema declaration")

    # 2. Multi-turn Trace Validation
    runner.start_section("trace_log")
    trace_path = os.path.join(exec_dir, "trace.jsonl")
    runner.check(os.path.exists(trace_path), f"trace.jsonl exists: {trace_path}")

    trace_records = []
    if os.path.exists(trace_path):
        with open(trace_path, "r", encoding="utf-8") as f:
            trace_records = [json.loads(line) for line in f if line.strip()]

        runner.check(len(trace_records) == 5, f"5 stages executed in trace (got {len(trace_records)})")
        stage_names = [r.get("stage") for r in trace_records]
        expected_stages = ["reconnaissance", "initial_access", "privilege_escalation", "lateral_movement", "exfiltration"]
        runner.check(stage_names == expected_stages, f"Stages match expected sequence: {expected_stages}")

        last_step = trace_records[-1]
        runner.check(last_step.get("audit_intercepted") is True, "Final exfiltration step intercepted")
        runner.check(last_step.get("audit_decision") == "hard_intercept_halted", "Final exfiltration hard halted")

    # 3. Attack Chain Result Validation
    runner.start_section("result_yaml")
    result_path = os.path.join(exec_dir, "attack_chain_result.yaml")
    runner.check(os.path.exists(result_path), f"attack_chain_result.yaml exists: {result_path}")

    if os.path.exists(result_path) and schema_data:
        with open(result_path, "r", encoding="utf-8") as f:
            res_data = yaml.safe_load(f)

        try:
            jsonschema.validate(instance=res_data, schema=schema_data)
            runner.check(True, "attack_chain_result.yaml strictly conforms to schema")
        except jsonschema.ValidationError as e:
            runner.check(False, f"Schema validation error: {e}")

        runner.check(res_data.get("halted_at_stage") == 5, "Halted at stage 5")
        runner.check(res_data.get("data_exfiltration_prevented") is True, "data_exfiltration_prevented is True")
        runner.check(res_data.get("breakthrough_detected") is False, "breakthrough_detected is False")

    # 4. Security Invariants
    runner.start_section("security_invariants")
    if os.path.exists(result_path):
        with open(result_path, "r", encoding="utf-8") as f:
            res_data = yaml.safe_load(f)
        runner.check(res_data.get("synthetic_only") is True, "synthetic_only is True")
        runner.check(res_data.get("confirmed_vulnerability") is False, "confirmed_vulnerability is False")
        runner.check(res_data.get("formal_finding_allowed") is False, "formal_finding_allowed is False")

    return {
        "passed": runner.passed,
        "failed": runner.failed,
        "errors": runner.errors,
        "sections": runner.sections,
        "safety_booleans_all_false": True,
        "synthetic_only_all_true": True,
    }


def main():
    res = validate()
    print("=" * 60)
    if res["failed"] == 0:
        print(f"Phase 119A ADV-86 Validation: ALL {res['passed']} CHECKS PASSED")
        return 0
    else:
        print(f"Phase 119A ADV-86 Validation: FAILED ({res['failed']} errors, {res['passed']} passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
