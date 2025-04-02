#!/usr/bin/env python3

import time
from pathlib import Path
import sys
import os

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

try:
    from comparison_logic.setup_helpers import BASE_DIR
except ImportError:
    print("Warning: Could not import from setup_helpers. Defining locally.")
    BASE_DIR = Path("../comparison_logic_data")  # Adjust if needed

NUM_ITEMS = 5


def process_item(item_id):
    """Simulates reading a file and doing minor processing per item."""
    filepath = BASE_DIR / f"item_{item_id}.txt"
    print(f"  (Target) Processing item {item_id} (Reading {filepath.name})...")
    try:
        count = 0
        total_sum = 0
        with open(filepath, "r") as f:
            for line in f:
                try:
                    total_sum += int(line.strip())
                    count += 1
                except ValueError:
                    pass
        avg = total_sum / count if count > 0 else 0
        print(f"  (Target) Finished item {item_id}. Avg: {avg:.2f}")
        return (item_id, avg)
    except FileNotFoundError:
        print(f"  (Target) Error: File not found for item {item_id}")
        return (item_id, None)
    except Exception as e:
        print(f"  (Target) Error processing item {item_id}: {e}")
        return (item_id, None)


if __name__ == "__main__":
    print("\n--- Target Looping Script Running ---")
    local_start_time = time.perf_counter()
    items_to_process = range(NUM_ITEMS)
    results = []

    print("(Target) Starting sequential loop...")
    for item_id in items_to_process:
        result = process_item(item_id)
        results.append(result)
    print("(Target) Finished sequential loop.")

    local_end_time = time.perf_counter()
    print(f"(Target) Results: {results}")
    print(f"(Target) Direct Run Time: {local_end_time - local_start_time:.4f} seconds")
    print("--- Target Looping Script End ---")
