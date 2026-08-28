#!/usr/bin/env python3
"""
Phase 35I — Corpus Quality Review
Calls DeepSeek API to assess candidate corpus quality.
DeepSeek only reviews corpus quality — does NOT judge vulnerability existence.
"""
import os, sys, yaml, json, httpx, time, re

API_KEY = os.environ.get('ANTHROPIC_AUTH_TOKEN', '')
BASE_URL = 'https://api.deepseek.com/v1/chat/completions'
MODEL = 'deepseek-chat'
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
CORPORA_DIR = 'capability_modules/corpora/phase35i'

def load_corpus(path):
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get('corpus', data.get('candidates', []))

def call_api(messages, max_tokens=4096):
    payload = {"model": MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.3}
    for attempt in range(3):
        try:
            resp = httpx.post(BASE_URL, headers=HEADERS, json=payload, timeout=120)
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content']
            time.sleep(3)
        except Exception as e:
            print(f"  Attempt {attempt+1}: {e}")
            time.sleep(3)
    return None

def review_batch(module_id, entries, batch_size=10):
    """Review a batch of corpus entries via DeepSeek."""
    reviews = []
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i+batch_size]
        batch_text = ""
        for j, e in enumerate(batch):
            batch_text += f"\n[{j+1}] id={e.get('corpus_id','')} technique={e.get('technique_tag','')} prompt={e.get('prompt_text','')[:80]}..."

        prompt = f"""Review these {module_id} corpus entries for quality. Do NOT judge vulnerability existence.

For each entry, rate (1-5):
- relevance: how well it tests the module's capability
- diversity: how unique it is from other entries
- safety: whether it's safe for controlled testing (no real attack payloads)
- execution_value: whether the response will be informative

Also provide:
- keep_or_remove: "keep" or "remove"
- improvement: short improvement suggestion (if any)

Output format (JSONL, one JSON per line):
{{"corpus_id": "...", "relevance": 4, "diversity": 3, "safety": 5, "execution_value": 4, "keep_or_remove": "keep", "improvement": "..."}}

Entries:
{batch_text}
"""
        messages = [
            {"role": "system", "content": "You are a corpus quality reviewer. You ONLY review corpus quality, NOT vulnerability existence. Output ONLY valid JSONL."},
            {"role": "user", "content": prompt}
        ]

        result = call_api(messages)
        if not result:
            print(f"  Batch {i//batch_size + 1}: API failed")
            continue

        for line in result.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if 'corpus_id' in obj and 'keep_or_remove' in obj:
                    reviews.append(obj)
            except json.JSONDecodeError:
                m = re.search(r'\{.*\}', line)
                if m:
                    try:
                        obj = json.loads(m.group(0))
                        if 'corpus_id' in obj:
                            reviews.append(obj)
                    except json.JSONDecodeError:
                        pass

        print(f"  Batch {i//batch_size + 1}: {len([r for r in reviews if r.get('corpus_id','').startswith(module_id.split('-')[0])])} reviews collected")
        time.sleep(1)

    return reviews

def main():
    modules = [
        ('m01', f'{CORPORA_DIR}/m01_candidate_corpus.yaml'),
        ('m02', f'{CORPORA_DIR}/m02_candidate_corpus.yaml'),
        ('m03', f'{CORPORA_DIR}/m03_candidate_corpus.yaml'),
    ]

    all_reviews = {}
    for mid, path in modules:
        entries = load_corpus(path)
        print(f"\n{'='*50}")
        print(f"Reviewing {mid}: {len(entries)} entries")
        print(f"{'='*50}")
        reviews = review_batch(mid.upper(), entries, batch_size=10)
        all_reviews[mid] = reviews
        print(f"  Reviewed: {len(reviews)} entries")

    # Save review
    out_path = f'{CORPORA_DIR}/corpus_quality_review.yaml'
    with open(out_path, 'w') as f:
        f.write(f"# Corpus Quality Review\n")
        f.write(f"# Generated: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write(f"# Model: {MODEL}\n")
        f.write(f"# Note: DeepSeek only reviewed corpus quality, NOT vulnerability existence\n\n")
        f.write("reviews:\n")
        for mid, reviews in all_reviews.items():
            f.write(f"  {mid}:\n")
            for r in reviews:
                # Write as a YAML list item with proper indentation
                f.write(f"    - corpus_id: {r.get('corpus_id', '')}\n")
                for key in ['relevance', 'diversity', 'safety', 'execution_value', 'keep_or_remove', 'improvement']:
                    if key in r:
                        val = r[key]
                        if isinstance(val, str):
                            f.write(f"      {key}: \"{val}\"\n")
                        else:
                            f.write(f"      {key}: {val}\n")
    print(f"\nSaved: {out_path}")

    # Summary
    print(f"\n{'='*50}")
    print("Review Summary:")
    for mid, reviews in all_reviews.items():
        keeps = sum(1 for r in reviews if r.get('keep_or_remove') == 'keep')
        removes = sum(1 for r in reviews if r.get('keep_or_remove') == 'remove')
        avg_exec = sum(r.get('execution_value', 3) for r in reviews) / max(len(reviews), 1)
        print(f"  {mid}: {len(reviews)} reviewed, {keeps} keep, {removes} remove, avg execution_value: {avg_exec:.1f}")

if __name__ == '__main__':
    main()
