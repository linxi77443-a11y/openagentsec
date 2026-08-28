import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from src.engine.v2.html_report import generate_html_report

def main():
    json_path = "executions/phase112b_report008/sample_full_report.json"
    out_path = "executions/phase113a_view013/sample_report.html"
    
    html_content = generate_html_report(json_path)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    main()
