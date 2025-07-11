#!/usr/bin/env python3
"""
main.py

Command-line entry point for the RAG Literature Review pipeline.
Usage:
    python main.py /path/to/pdf/folder [--output output.json]
"""

import os
import sys
from dotenv import load_dotenv

# Ensure we can import the Django settings (if needed) or pip-installed rag_app
# If you install this project in editable mode (pip install -e .), rag_app will be on PYTHONPATH.
# Otherwise adjust sys.path so the project root is importable.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is not set!"

import argparse
import json
import time
from rag_app.utils.rag_pipeline import run_rag_litreview

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the Retrieval-Augmented-Generation literature review pipeline."
    )
    parser.add_argument(
        "folder",
        help="Path to the folder containing PDF papers."
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to save the JSON result (default: ./results/review_output.json).",
        default="results/review_output.json"
    )
    return parser.parse_args()

def main():
    starttime = time.time()
    args = parse_args()

    folder_path = args.folder
    if not os.path.isdir(folder_path):
        print(f"Error: folder not found at '{folder_path}'", file=sys.stderr)
        sys.exit(1)

    print(f"Ingesting PDFs from: {folder_path}")
    result = run_rag_litreview(folder_path)

    output_path = args.output
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Review completed. Results saved to: {output_path}")
    print(f"Total time taken: {time.time() - starttime:.2f} seconds")

if __name__ == "__main__":
    main()
