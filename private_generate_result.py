import json
from pathlib import Path
import argparse
import numpy as np


MATCH_NAME = "quick_match"


def safe_get(d, *keys, default=None):
    for k in keys:
        if d is None:
            return default
        d = d.get(k)
    return d if d is not None else default


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_overall(metric_json):
    out = {}

    specs = [
        ("text_block", "Edit_dist"),
        ("display_formula", "Edit_dist"),
        ("table", "Edit_dist"),
        ("reading_order", "Edit_dist"),
        ("circuit_diagram", "Edit_dist"),
    ]

    
            
    for category, metric in specs:
        if metric in ("CDM", "TEDS", "TEDS_structure_only"):
            val = safe_get(metric_json, category, "page", metric, "ALL", default=0.0)
            out[f"{category}_{metric}"] = val * 100
        else:
            val = safe_get(metric_json, category, "all", metric, "ALL_page_avg", default=0.0)
            out[f"{category}_{metric}"] = val

    # Same formula as notebook
    out["overall_score"] = (
        out["text_block_Edit_dist"]
        # + out["display_formula_Edit_dist"] 
        + out["table_Edit_dist"]
        + out["reading_order_Edit_dist"]
        + out["circuit_diagram_Edit_dist"]
    ) / 4.0

    return out


def run(mode: str):
    result_dir = Path("result") / mode
    output_dir = Path("private_output") / mode # Where all.json lives

    metric_file = result_dir / f"{mode}_{MATCH_NAME}_metric_result.json"
    text_block_file = result_dir / f"{mode}_{MATCH_NAME}_text_block_result.json"
    table_file = result_dir / f"{mode}_{MATCH_NAME}_table_result.json"
    reading_order_file = result_dir / f"{mode}_{MATCH_NAME}_reading_order_result.json"
    display_formula_file = result_dir / f"{mode}_{MATCH_NAME}_display_formula_result.json"
    circuit_diagram_file = result_dir / f"{mode}_{MATCH_NAME}_circuit_diagram_result.json"

    metric_json = load_json(metric_file)

    # Load Inference Stats
    stats_file = output_dir / "all.json"
    perf_data = load_json(stats_file) if stats_file.exists() else {}

    summary = {
        "overall": compute_overall(metric_json),
        "performance_metrics": {
            "average_time_seconds": perf_data.get("avg_inference_time"),
            "average_cost_usd": perf_data.get("avg_cost"),
            "total_session_cost": perf_data.get("total_cost"),
            "images_processed": perf_data.get("completed_count")
        },
        "text_block": load_json(text_block_file) if text_block_file.exists() else {},
        "table": load_json(table_file) if table_file.exists() else {},
        "reading_order": load_json(reading_order_file) if reading_order_file.exists() else {},
        "display_formula": load_json(display_formula_file) if display_formula_file.exists() else {},
        "circuit_diagram": load_json(circuit_diagram_file) if circuit_diagram_file.exists() else {}
    }

    out_path = result_dir / "summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[✓] Summary written to {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, help="e.g. sr, end2end")
    args = parser.parse_args()

    run(args.mode)


if __name__ == "__main__":
    main()
