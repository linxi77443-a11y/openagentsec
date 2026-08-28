#!/usr/bin/env python3
"""
Phase 35I — Select Execution Corpus
Combines quality reviews with candidate corpus to select the best entries.
Selects ~15-20 per module for execution.
"""
import os, sys, yaml

CORPORA_DIR = 'capability_modules/corpora/phase35i'

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

def load_reviews():
    data = load_yaml(f'{CORPORA_DIR}/corpus_quality_review.yaml')
    reviews = {}
    for mid in ['m01', 'm02', 'm03']:
        entries = data.get('reviews', {}).get(mid, [])
        for e in entries:
            reviews[e.get('corpus_id', '')] = e
    return reviews

def select_for_module(mid, candidates, reviews, max_select=18, max_controls=5):
    """Select best entries for execution. Prioritize positives with diversity."""
    scored = []
    for c in candidates:
        cid = c.get('corpus_id', '')
        review = reviews.get(cid, {})
        keep = review.get('keep_or_remove', 'keep')
        exec_val = review.get('execution_value', 3)
        relevance = review.get('relevance', 3)

        technique = c.get('technique_tag', 'unknown')
        is_control = c.get('positive_or_control', 'positive') == 'control'

        # Score: prefer kept, high execution_value, diverse techniques
        score = (5 if keep == 'keep' else 0) + exec_val + relevance
        if keep != 'keep':
            score -= 10  # Strong penalty for entries marked remove

        scored.append((score, c, technique, is_control))

    scored.sort(key=lambda x: -x[0])

    # Separate controls and positives
    controls = [(s, c, t) for s, c, t, is_c in scored if is_c]
    positives = [(s, c, t) for s, c, t, is_c in scored if not is_c]

    selected = []
    techniques_used = set()

    # Step 1: Take up to max_controls controls (best scored)
    for score, c, technique in controls[:max_controls]:
        selected.append(c)

    # Step 2: Take positives with technique diversity
    for score, c, technique in positives:
        if len(selected) >= max_select:
            break
        if technique not in techniques_used:
            selected.append(c)
            techniques_used.add(technique)

    # Step 3: If room left, add 2nd positives from strongest techniques
    for score, c, technique in positives:
        if len(selected) >= max_select:
            break
        if technique in techniques_used:
            # Count how many already selected from this technique
            current_count = sum(1 for s in selected if s.get('technique_tag') == technique)
            if current_count < 2:  # Allow max 2 per technique
                selected.append(c)

    final = selected[:max_select]

    pos = sum(1 for c in final if c.get('positive_or_control') == 'positive')
    ctrl = sum(1 for c in final if c.get('positive_or_control') == 'control')
    tags = set(c.get('technique_tag', '') for c in final)

    return final, pos, ctrl, tags

def main():
    reviews = load_reviews()
    print(f"Loaded {len(reviews)} quality reviews")

    all_selected = {}

    for mid in ['m01', 'm02', 'm03']:
        candidates = load_yaml(f'{CORPORA_DIR}/{mid}_candidate_corpus.yaml').get('corpus', [])
        print(f"\n{'='*50}")
        print(f"Selecting {mid}: {len(candidates)} candidates available")

        selected, pos, ctrl, tags = select_for_module(mid, candidates, reviews, max_select=18)
        all_selected[mid] = selected

        print(f"  Selected: {len(selected)} ({pos} positive, {ctrl} control)")
        print(f"  Techniques: {sorted(tags)}")
        print(f"  Technique counts:")
        for tag in sorted(tags):
            count = sum(1 for c in selected if c.get('technique_tag') == tag)
            print(f"    {tag}: {count}")

    # Save selected corpus — write clean YAML line by line
    out_path = f'{CORPORA_DIR}/selected_execution_corpus.yaml'
    with open(out_path, 'w') as f:
        f.write(f"# Selected Execution Corpus\n")
        f.write(f"# Generated: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write(f"# Total: {sum(len(v) for v in all_selected.values())}\n\n")
        for mid, entries in all_selected.items():
            f.write(f"# === {mid} ({len(entries)} entries) ===\n")
            f.write(f"{mid}:\n")
            for e in entries:
                f.write(f"  - corpus_id: \"{e.get('corpus_id', '')}\"\n")
                for key, val in e.items():
                    if key == 'corpus_id':
                        continue
                    if isinstance(val, str):
                        f.write(f"    {key}: \"{val}\"\n")
                    else:
                        f.write(f"    {key}: {val}\n")
            f.write("\n")

    total = sum(len(v) for v in all_selected.values())
    print(f"\n{'='*50}")
    print(f"Total selected: {total} entries")
    print(f"Saved: {out_path}")

if __name__ == '__main__':
    main()
