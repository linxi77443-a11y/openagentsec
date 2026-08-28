#!/usr/bin/env python3
"""
Phase 35I — Capability Sprint Execution
Direct API calls to FastGPT-compatible endpoint (non-standard format).
Reads selected corpus, calls API, saves raw + redacted results.
"""
import json, yaml, httpx, time, os, urllib3
from datetime import datetime, timezone

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = os.environ.get("FASTGPT_TEST_API_KEY", "")
BASE_URL = os.environ.get("FASTGPT_TEST_BASE_URL", "https://example.invalid/api/v1/chat/completions")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
SELECTED_PATH = "capability_modules/corpora/phase35i/selected_execution_corpus.yaml"
OUT_DIR = "executions/phase35i_capability_sprint"

RATE_LIMIT = 28  # stay under 30
WINDOW_SEC = 60

def call_api(prompt_text, cid):
    body = {
        "chatId": f"atlas-p35i-{cid}",
        "stream": False,
        "detail": False,
        "messages": [{"role": "user", "content": prompt_text}],
    }
    start = time.time()
    try:
        r = httpx.post(BASE_URL, headers=HEADERS, json=body, timeout=120, verify=False)
        elapsed = round(time.time() - start, 2)
        if r.status_code == 200:
            data = r.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            usage = data.get('usage', {})
            return {"ok": True, "content": content, "usage": usage, "elapsed": elapsed, "status": 200}
        else:
            return {"ok": False, "content": r.text[:500], "usage": {}, "elapsed": elapsed, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "content": str(e)[:500], "usage": {}, "elapsed": round(time.time() - start, 2), "status": 0}

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(SELECTED_PATH) as f:
        corpus = yaml.safe_load(f)

    all_results = []
    index = 0
    total = sum(len(v) for v in corpus.values() if isinstance(v, list))
    req_count = 0
    window_start = time.time()

    for mid in ['m01', 'm02', 'm03']:
        entries = corpus.get(mid, [])
        for entry in entries:
            index += 1
            prompt = entry.get('prompt_text', '')
            cid = entry.get('corpus_id', f'{mid}-X')
            tech = entry.get('technique_tag', '')

            # Rate limiting
            req_count += 1
            if req_count >= RATE_LIMIT:
                remaining = WINDOW_SEC - (time.time() - window_start)
                if remaining > 0:
                    print(f"  Rate limit: pause {remaining:.0f}s...")
                    time.sleep(remaining)
                req_count = 0
                window_start = time.time()

            print(f"[{index}/{total}] {cid} ({tech})...", end=' ', flush=True)
            result = call_api(prompt, cid)

            all_results.append({
                "corpus_id": cid,
                "module_id": mid,
                "technique_tag": tech,
                "positive_or_control": entry.get('positive_or_control', 'positive'),
                "prompt_text": prompt[:100],
                "api_response": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            status = "OK" if result['ok'] else f"ERR({result['status']})"
            print(f"{status} {result['elapsed']}s")
            time.sleep(1.5)  # polite inter-request delay

    # Save full results
    out_path = f"{OUT_DIR}/execution_results.json"
    with open(out_path, 'w') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n{'='*50}")
    print(f"Saved: {out_path}")
    ok = sum(1 for r in all_results if r['api_response']['ok'])
    fail = sum(1 for r in all_results if not r['api_response']['ok'])
    print(f"OK: {ok}, Failed: {fail}, Total: {len(all_results)}")

    # Save redacted summary
    summary = {
        "phase": "phase35i_capability_sprint",
        "execution_time": datetime.now(timezone.utc).isoformat(),
        "total": len(all_results),
        "ok": ok,
        "failed": fail,
        "modules": {},
    }
    for mid in ['m01', 'm02', 'm03']:
        mod_results = [r for r in all_results if r['module_id'] == mid]
        mod_ok = sum(1 for r in mod_results if r['api_response']['ok'])
        summary['modules'][mid] = {"total": len(mod_results), "ok": mod_ok}

    summary_path = f"{OUT_DIR}/execution_summary.yaml"
    with open(summary_path, 'w') as f:
        f.write("# Phase 35I Execution Summary (redacted)\n")
        f.write(f"# Time: {summary['execution_time']}\n\n")
        f.write(yaml.dump(summary, default_flow_style=False, allow_unicode=True, sort_keys=False))
    print(f"Saved: {summary_path}")

if __name__ == '__main__':
    main()
