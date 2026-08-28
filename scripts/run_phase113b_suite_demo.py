import os
import yaml
import sys
sys.path.insert(0, os.path.abspath('.'))

from src.engine.v2.task_suite import load_task_suite, validate_suite, sample_suite

def main():
    tasks = load_task_suite()
    validate_suite(tasks)
    
    sampled = sample_suite(tasks, sample_size=10)
    
    # Distribution stats
    cat_dist = {}
    lang_dist = {}
    for t in tasks:
        cat_dist[t["category"]] = cat_dist.get(t["category"], 0) + 1
        lang_dist[t["language"]] = lang_dist.get(t["language"], 0) + 1
        
    sampled_cat_dist = {}
    for t in sampled:
        sampled_cat_dist[t["category"]] = sampled_cat_dist.get(t["category"], 0) + 1
        
    report = {
        "full_suite_stats": {
            "total_tasks": len(tasks),
            "category_distribution": cat_dist,
            "language_distribution": lang_dist
        },
        "sampling_demo": {
            "sample_size": len(sampled),
            "sampled_category_distribution": sampled_cat_dist,
            "sampled_tasks": [t["task_id"] for t in sampled]
        }
    }
    
    out_dir = "executions/phase113b_harness017"
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/suite_report.yaml", "w", encoding="utf-8") as f:
        yaml.dump(report, f, sort_keys=False, allow_unicode=True)
        
    print(f"Generated {out_dir}/suite_report.yaml")

if __name__ == "__main__":
    main()
