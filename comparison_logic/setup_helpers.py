#!/usr/bin/env python3

import os
import random
from pathlib import Path

# Define the base directory for data relative to this script's parent dir
_current_dir = Path(__file__).resolve().parent
BASE_DIR = _current_dir.parent / "comparison_logic_data"
BASE_DIR.mkdir(parents=True, exist_ok=True)


def create_dummy_file(filename, num_lines=1000, max_val=10000):
    """Creates a file with random numbers, one per line."""
    filepath = BASE_DIR / filename
    try:
        with open(filepath, "w") as f:
            for _ in range(num_lines):
                f.write(f"{random.randint(0, max_val)}\n")
        print(f"Created/Updated dummy file: {filepath}")
    except IOError as e:
        print(f"Error creating file {filepath}: {e}")
    return filepath


def simple_math_task(n=10**6):
    """A simple CPU-bound task."""
    # print(f"  Running math task (summing to {n})...")
    s = sum(i * i for i in range(int(n)))  # Ensure n is int
    # print(f"  Math task done.")
    return s


# --- Create/Update files needed for examples ---
if __name__ == "__main__":
    print("--- Setting up dummy data ---")
    create_dummy_file("data_a.txt", 500)
    create_dummy_file("data_source_1.txt", 2000)
    create_dummy_file("data_source_2.txt", 2500)
    create_dummy_file("branching_log.txt", 0)  # Create empty log file
    for i in range(5):
        create_dummy_file(f"item_{i}.txt", random.randint(300, 700))
    print(f"--- Setup complete. Data in: {BASE_DIR} ---")
