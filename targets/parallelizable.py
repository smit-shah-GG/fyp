#!/usr/bin/env python3

import time
from pathlib import Path
import sys
import os

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

try:
    from comparison_logic.setup_helpers import BASE_DIR, simple_math_task
except ImportError:
    print("Warning: Could not import from setup_helpers. Defining locally.")
    BASE_DIR = Path("../comparison_logic_data")  # Adjust if needed

    def simple_math_task(n=10**6):
        s = sum(i * i for i in range(n))
        return s


FILE_1 = BASE_DIR / "data_source_1.txt"
FILE_2 = BASE_DIR / "data_source_2.txt"


def task1_find_max(filepath):
    """Reads a file and finds the maximum integer value."""
    print(f"(Target) Starting Task 1: Finding max in {filepath.name}...")
    max_val = -1
    try:
        with open(filepath, "r") as f:
            for line in f:
                try:
                    num = int(line.strip())
                    if num > max_val:
                        max_val = num
                except ValueError:
                    pass
        print(f"(Target) Finished Task 1. Max = {max_val}")
        return max_val
    except FileNotFoundError:
        print(f"(Target) Error Task 1: File not found {filepath}")
        return -1


def task2_calculate_sum(filepath):
    """Reads a file and calculates the sum of integers."""
    print(f"(Target) Starting Task 2: Calculating sum in {filepath.name}...")
    total_sum = 0
    try:
        with open(filepath, "r") as f:
            for line in f:
                try:
                    total_sum += int(line.strip())
                except ValueError:
                    pass
        print(f"(Target) Finished Task 2. Sum = {total_sum}")
        return total_sum
    except FileNotFoundError:
        print(f"(Target) Error Task 2: File not found {filepath}")
        return 0


def task3_independent_cpu():
    """Independent CPU-bound task."""
    print("(Target) Starting Task 3: Independent CPU calculation...")
    result = simple_math_task(8 * 10**5)
    print("(Target) Finished Task 3.")
    return result


def combine_results(res1, res2, res3_ignored):
    """Combine results from parallel tasks."""
    print(f"(Target) Combining Task1_Max={res1}, Task2_Sum={res2}...")
    final = res1 + res2
    print(f"(Target) Finished combining. Final Value = {final}")
    return final


if __name__ == "__main__":
    print("\n--- Target Parallelizable Script Running ---")
    local_start_time = time.perf_counter()

    # These would run sequentially here
    res1 = task1_find_max(FILE_1)
    res2 = task2_calculate_sum(FILE_2)
    res3 = task3_independent_cpu()
    final_result = combine_results(res1, res2, res3)

    local_end_time = time.perf_counter()
    print(f"(Target) Final Combined Result: {final_result}")
    print(f"(Target) Direct Run Time: {local_end_time - local_start_time:.4f} seconds")
    print("--- Target Parallelizable Script End ---")
