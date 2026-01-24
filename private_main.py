import os
import time
import base64
import argparse
from pathlib import Path
from typing import Dict, Any
from PIL import Image
import subprocess
import yaml
import sys
import json

from tqdm import tqdm
from dotenv import load_dotenv
from openai import AzureOpenAI

from private_prompts import PROMPT_MAP, SYSTEM_PROMPT


# =============================
# Configuration
# =============================
IMAGE_DIR = Path("OmniDocBench/private_images")
BASE_OUTPUT_DIR = Path("private_output")

SKIP_EXISTING = True  # Skip inference if .md already exists

# Cost
PRICE_PER_1K_INPUT = 0.0002 
PRICE_PER_1K_OUTPUT = 0.0008

# =============================
# Utilities
# =============================
def load_image_base64(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_metadata(image_path: Path):
    with Image.open(image_path) as img:
        width, height = img.size
    return image_path.stem, width, height


# =============================
# Azure OpenAI Setup
# =============================
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, DEPLOYMENT_NAME, API_VERSION]):
    raise RuntimeError("Missing Azure OpenAI environment variables.")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

BASE_OUTPUT_DIR.mkdir(exist_ok=True)


# =============================
# GPT Inference
# =============================
def infer_page(image_path: Path, mode: str) -> str:
    image_b64 = load_image_base64(image_path)
    page_id, width, height = get_image_metadata(image_path)

    prompt_func = PROMPT_MAP.get(mode, PROMPT_MAP["sr"])
    user_prompt = prompt_func(page_id, width, height)

    start_time = time.time()

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    }
                ]
            }
        ],
        temperature=0,
    )

    elapsed = time.time() - start_time
    content = response.choices[0].message.content.strip()
    
    # Extract token usage
    usage = response.usage
    cost = (usage.prompt_tokens / 1000 * PRICE_PER_1K_INPUT) + \
           (usage.completion_tokens / 1000 * PRICE_PER_1K_OUTPUT)
    
    return content, elapsed, cost


# =============================
# Inference Pipeline
# =============================
def run_inference(mode: str, max_pages: int = None):
    output_dir = BASE_OUTPUT_DIR / mode
    output_dir.mkdir(parents=True, exist_ok=True)

    stats_path = output_dir / "all.json"
    
    # Load existing stats if they exist, otherwise start from zero
    if stats_path.exists():
        with open(stats_path, "r") as f:
            prev_stats = json.load(f)
            total_time = prev_stats.get("total_time", 0)
            total_cost = prev_stats.get("total_cost", 0)
            count = prev_stats.get("completed_count", 0)
    else:
        total_time = 0
        total_cost = 0
        count = 0

    image_files = sorted(
        p for p in IMAGE_DIR.iterdir()
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    )

    if max_pages:
        image_files = image_files[:max_pages]

    pbar = tqdm(image_files, desc=f"Inference ({mode})", unit="img")

    for image_path in pbar:
        out_path = output_dir / f"{image_path.stem}.md"

        if SKIP_EXISTING and out_path.exists():
            continue

        md_text, elapsed, cost = infer_page(image_path, mode)
        
        # Update running totals
        total_time += elapsed
        total_cost += cost
        count += 1

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md_text)
    
        # Save updated stats after every image (prevents data loss if crashed)
        with open(stats_path, "w") as f:
            json.dump({
                "avg_inference_time": total_time / count if count > 0 else 0,
                "avg_cost": total_cost / count if count > 0 else 0,
                "total_time": total_time,
                "total_cost": total_cost,
                "completed_count": count
            }, f, indent=2)

def run_evaluation(mode: str, base_config: str = "configs/private.yaml"):
    """
    Modifies the config on the fly to point to output/{mode} and runs evaluation.
    """
    # 1. Load the template config
    with open(base_config, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # 2. Update the prediction path to the specific mode's output
    # This aligns with the 'private_output/{mode}' directory created in run_inference
    config_data['end2end_eval']['dataset']['prediction']['data_path'] = f"./private_output/{mode}"
    
    # 3. Save a temporary config for this specific mode
    temp_config_path = f"configs/tmp_eval_{mode}.yaml"
    with open(temp_config_path, 'w') as f:
        yaml.dump(config_data, f)
    
    print(f"\n>>> Starting Evaluation Stage for Mode: {mode}")
    try:
        # Call the validation script
        subprocess.run(
            [sys.executable, "private_pdf_validation.py", "--config", temp_config_path],
            check=True
        )
    finally:
        # Cleanup temporary file
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)

def run_summary(mode: str):
    """
    Triggers generate_result.py to create the final summary.json in result/{mode}.
    """
    print(f"\n>>> Stage 3: Generating Summary for Mode: {mode}")
    try:
        subprocess.run([sys.executable, "private_generate_result.py", "--mode", mode], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Summary generation failed for {mode}: {e}")

# =============================
# Entry Point
# =============================
def main():
    parser = argparse.ArgumentParser(description="OmniDocBench Inference & Evaluation")
    parser.add_argument(
        "--mode",
        type=str,
        default="sr",
        choices=list(PROMPT_MAP.keys()) + ["all"],
        help="Prompting mode"
    )
    parser.add_argument(
        "--max_pages",
        type=int,
        default=None,
        help="Limit number of images"
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        default=True,  # Set to True by default to automate the two-stage process
        help="Automatically run evaluation after inference"
    )
    args = parser.parse_args()

    modes = list(PROMPT_MAP.keys()) if args.mode == "all" else [args.mode]

    modes = list(PROMPT_MAP.keys()) if args.mode == "all" else [args.mode]

    for mode in modes:
        # Stage 1: Inference (Produces .md files in output/{mode})
        run_inference(mode, args.max_pages)
        
        # Stage 2: Evaluation (Reads from output/{mode}, writes to result/{mode})
        run_evaluation(mode)

        # 3. Summary Stage
        run_summary(mode)

    print("\n[✓] Full pipeline execution complete.")


if __name__ == "__main__":
    main()


'''How to run:
python3 private_main.py --mode all --max_pages 10
python3 private_main.py --mode all
'''