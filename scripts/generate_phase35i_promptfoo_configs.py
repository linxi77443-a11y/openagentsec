#!/usr/bin/env python3
"""
Phase 35I — Generate promptfoo configs for M01/M02/M03 capability sprint.
Reads selected_execution_corpus.yaml and generates per-module promptfoo configs.
Configs use env vars for API credentials — no hardcoded keys.
"""
import os, sys, yaml

CORPORA_DIR = 'capability_modules/corpora/phase35i'
CONFIG_DIR = 'tool_integrations/promptfoo/capability_sprint'

ENV_PROVIDER_TEMPLATE = """id: "env:AUTHORIZED_TEST_API_BASE_URL"
config:
  apiKey: "env:AUTHORIZED_TEST_API_KEY"
  model: "env:AUTHORIZED_TEST_API_MODEL"
"""

def make_provider():
    return yaml.safe_load(ENV_PROVIDER_TEMPLATE)

def detect_module_signals(module_id, technique_tag):
    """Map technique_tag to expected signals/assertions."""
    base_assertions = [
        {"type": "is-json"},  # Basic response is parseable
    ]

    m01_signals = {
        'multilingual_bypass': ['prompt_injection', 'multilingual_injection'],
        'encoding_bypass': ['prompt_injection', 'encoded_injection'],
        'format_morphing': ['prompt_injection', 'format_embedding'],
        'role_induction': ['jailbreak', 'role_induction'],
        'rule_ignore_induction': ['prompt_injection', 'rule_override'],
        'step_by_step': ['prompt_injection', 'step_by_step'],
        'output_format_manipulation': ['format_manipulation', 'restricted_output'],
        'normal_control': [],
    }

    m02_signals = {
        'system_prompt_leak': ['system_prompt_leak_attempt'],
        'developer_instruction_leak': ['developer_instruction_leak_attempt'],
        'internal_policy_leak': ['internal_policy_leak_attempt'],
        'encoding_induction': ['encoded_prompt_leak_attempt'],
        'step_by_step_extraction': ['step_by_step_leak_attempt'],
        'format_output_induction': ['format_output_leak_attempt'],
        'refusal_control': [],
        'normal_control': [],
    }

    m03_signals = {
        'raw_kb_request': ['raw_kb_content_exposure_attempt'],
        'source_chunk_exposure': ['source_chunk_exposure_attempt'],
        'full_document_induction': ['full_document_exposure_attempt'],
        'retrieval_metadata_induction': ['retrieval_metadata_exposure_attempt'],
        'summary_control': [],
        'sensitive_data_probing': ['sensitive_data_probing'],
        'normal_rag_control': [],
    }

    signal_map = {'m01': m01_signals, 'm02': m02_signals, 'm03': m03_signals}
    return base_assertions + signal_map.get(module_id, {}).get(technique_tag, [])


def generate_config(module_id, entries):
    """Generate a promptfoo config for one module."""
    provider = make_provider()

    # Build test cases
    tests = []
    for e in entries:
        test = {
            "description": f"{e.get('corpus_id','')} - {e.get('technique_tag','')}",
            "vars": {
                "prompt": e.get('prompt_text', ''),
                "corpus_id": e.get('corpus_id', ''),
                "technique_tag": e.get('technique_tag', ''),
                "positive_or_control": e.get('positive_or_control', 'positive'),
                "expected_result_semantics": e.get('expected_result_semantics', 'needs_human_review'),
            },
            "assert": [],
            "metadata": {
                "module_id": module_id,
                "corpus_id": e.get('corpus_id', ''),
                "technique_tag": e.get('technique_tag', ''),
                "positive_or_control": e.get('positive_or_control', ''),
                "phase": "phase35i_capability_sprint",
            }
        }
        tests.append(test)

    config = {
        "description": f"Phase 35I Capability Sprint — {module_id.upper()}",
        "providers": [provider],
        "prompts": ["{{prompt}}"],
        "tests": tests,
        "redteam": {
            "purpose": f"测试 {module_id.upper()} 能力：安全边界检测",
            "policies": [
                "不生成 formal finding",
                "不连接生产环境",
                "不保存完整敏感响应",
            ]
        },
        "nofail": True,
        "env": {
            "PROMPTFOO_REMOTE_API_BASE_URL": "env:AUTHORIZED_TEST_API_BASE_URL",
        }
    }

    return config


def main():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Load selected corpus
    with open(f'{CORPORA_DIR}/selected_execution_corpus.yaml') as f:
        corpus = yaml.safe_load(f)

    modules = ['m01', 'm02', 'm03']
    total_tests = 0

    for mid in modules:
        entries = corpus.get(mid, [])
        if not entries:
            print(f"  {mid}: no entries found in selected corpus")
            continue

        config = generate_config(mid, entries)
        out_path = f'{CONFIG_DIR}/promptfoo.{mid}.yaml'
        with open(out_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"  {mid}: {len(entries)} tests -> {out_path}")
        total_tests += len(entries)

    print(f"\nTotal: {total_tests} tests across {len(modules)} modules")

    # Also generate a combined runner config
    runner = {
        "description": "Phase 35I Capability Sprint — All Modules",
        "command": "promptfoo eval",
        "configs": [f'promptfoo.{mid}.yaml' for mid in modules],
    }
    runner_path = f'{CONFIG_DIR}/promptfoo.sprint.yaml'
    with open(runner_path, 'w') as f:
        yaml.dump(runner, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Runner config -> {runner_path}")


if __name__ == '__main__':
    main()
