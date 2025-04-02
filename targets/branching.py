#!/usr/bin/env python3

# work/targets/target_branching.py
import time
import random
from pathlib import Path
import sys

# --- Robust Path Calculation ---
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = SCRIPT_DIR.parent
HELPERS_DIR = WORKSPACE_DIR / "comparison_logic"
DATA_DIR = WORKSPACE_DIR / "comparison_logic_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- Add helpers dir to path ---
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

# --- Import Helpers ---
try:
    from comparison_logic.setup_helpers import simple_math_task
except ImportError as e:
    print(
        f"Warning: Could not import from comparison_logic.setup_helpers ({e}). Defining locally."
    )

    def simple_math_task(n=10**6):
        s = sum(i * i for i in range(int(n)))
        return s


# Use the robust DATA_DIR path
BASE_DIR = DATA_DIR
LOG_FILE = BASE_DIR / "branching_log.txt"


def process_heavy_branch():
    print("(Target) Starting heavy branch processing (CPU)...")
    start_t = time.perf_counter()
    _ = simple_math_task(12 * 10**5)
    proc_time = time.perf_counter() - start_t
    print(f"(Target) Finished heavy branch in {proc_time:.4f}s.")
    return "Heavy Result"


def process_light_branch():
    print("(Target) Starting light branch processing (CPU + I/O)...")
    start_t = time.perf_counter()
    _ = simple_math_task(2 * 10**5)
    log_time = 0
    try:
        log_start = time.perf_counter()
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.time()}: Light branch executed (Target).\n")
        log_time = time.perf_counter() - log_start
        print(f"(Target) Finished light branch log write in {log_time:.4f}s.")
        status = "Light Result"
    except Exception as e:
        print(f"(Target) Error writing log: {e}")
        status = "Light Result (Log Error)"
    proc_time = time.perf_counter() - start_t
    print(f"(Target) Finished light branch total in {proc_time:.4f}s.")
    return status


def analyze_results(result_tag):
    """Common step after branching."""
    print(f"(Target) Analyzing results for {result_tag}...")
    start_t = time.perf_counter()
    _ = sum(i for i in range(5 * 10**4))  # Simulate quick analysis
    proc_time = time.perf_counter() - start_t
    print(f"(Target) Finished analysis in {proc_time:.4f}s.")


if __name__ == "__main__":
    print("\n--- Target Branching Script Running ---")
    local_start_time = time.perf_counter()

    condition = random.choice([True, False])
    print(f"(Target) Condition is: {condition}")

    branch_result_tag = None
    if condition:
        branch_result_tag = process_heavy_branch()
    else:
        branch_result_tag = process_light_branch()

    analyze_results(branch_result_tag)

    local_end_time = time.perf_counter()
    print(f"(Target) Final Result Tag: {branch_result_tag}")
    print(
        f"(Target) Direct Run Total Time: {local_end_time - local_start_time} seconds"
    )
    print("--- Target Branching Script End ---")
