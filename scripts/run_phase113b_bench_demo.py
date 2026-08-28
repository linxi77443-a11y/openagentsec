import os
import yaml
import sys
sys.path.insert(0, os.path.abspath('.'))

from src.engine.v2.leaderboard import validate_leaderboard_entry, render_leaderboard_table

def main():
    with open("benchmarks/preset_leaderboard/sample_entries.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    entries = data.get("entries", [])
    valid_entries = []
    
    for entry in entries:
        try:
            validate_leaderboard_entry(entry)
            valid_entries.append(entry)
        except Exception as e:
            print(f"Validation failed for entry: {e}")
            
    markdown_content = render_leaderboard_table(valid_entries)
    
    out_dir = "executions/phase113b_bench016"
    os.makedirs(out_dir, exist_ok=True)
    
    with open(f"{out_dir}/leaderboard_preview.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    print(f"Generated {out_dir}/leaderboard_preview.md")

if __name__ == "__main__":
    main()
