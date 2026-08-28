import os
import yaml
import random

try:
    from src.engine.v2 import safety_invariants
except ImportError:
    pass

def load_task_suite(path="benchmarks/deepseek_suite/tasks_bilingual.yaml"):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("tasks", [])

def validate_suite(tasks, atlas_file="atlas/atlas_techniques.yaml"):
    with open(atlas_file, "r", encoding="utf-8") as f:
        atlas_data = yaml.safe_load(f)
        
    valid_tech_ids = {t["technique_id"] for t in atlas_data.get("techniques", [])}
    
    categories = set()
    languages = set()
    
    for t in tasks:
        if t["atlas_technique_id"] not in valid_tech_ids:
            raise ValueError(f"Invalid atlas_technique_id: {t['atlas_technique_id']}")
        if not t["synthetic_prompt"].startswith("<SIM_"):
            raise ValueError(f"Prompt must start with <SIM_: {t['synthetic_prompt']}")
            
        categories.add(t["category"])
        languages.add(t["language"])
        
    if len(categories) < 5:
        raise ValueError("Suite must contain at least 5 categories")
    if len(languages) < 2:
        raise ValueError("Suite must be bilingual (at least 2 languages)")
        
    return True

def sample_suite(tasks, sample_size=10):
    # Stratified sampling based on category
    cat_buckets = {}
    for t in tasks:
        cat_buckets.setdefault(t["category"], []).append(t)
        
    sampled = []
    cats = list(cat_buckets.keys())
    # Simple stratification: pick round-robin from categories
    idx = 0
    while len(sampled) < sample_size and any(cat_buckets.values()):
        cat = cats[idx % len(cats)]
        if cat_buckets[cat]:
            # Pick a random one from this category
            choice = random.choice(cat_buckets[cat])
            cat_buckets[cat].remove(choice)
            sampled.append(choice)
        idx += 1
        
    return sampled
