import os
import yaml
import sys

def main():
    checks = [
        "benchmarks/preset_leaderboard/dataset.yaml",
        "benchmarks/preset_leaderboard/leaderboard_schema.yaml",
        "src/engine/v2/leaderboard.py",
        "benchmarks/preset_leaderboard/sample_entries.yaml",
        "executions/phase113b_bench016/leaderboard_preview.md"
    ]
    
    for f in checks:
        if not os.path.exists(f):
            print(f"Missing {f}")
            sys.exit(1)
            
    with open("benchmarks/preset_leaderboard/dataset.yaml", "r") as f:
        ds = yaml.safe_load(f)
        if len(ds.get("entries", [])) < 75:
            print("dataset.yaml must have >=75 entries")
            sys.exit(1)
            
    sys.exit(0)

if __name__ == "__main__":
    main()
