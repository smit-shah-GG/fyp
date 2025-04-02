# work/targets/target_simple.py
import time
from pathlib import Path
import sys

# --- Robust Path Calculation ---
# Get the directory containing *this* script file when run
SCRIPT_DIR = Path(__file__).resolve().parent
# Assume 'comparison_logic' and 'targets' are siblings under the main 'work' dir
WORKSPACE_DIR = SCRIPT_DIR.parent
# Define the expected path for comparison_logic helpers
HELPERS_DIR = WORKSPACE_DIR / "comparison_logic"
# Define the data directory relative to the workspace
DATA_DIR = WORKSPACE_DIR / "comparison_logic_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # Ensure data dir exists

# --- Add helpers dir to path ---
# Allows finding 'comparison_logic' module
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

# --- Import Helpers (with fallback for safety) ---
try:
    from comparison_logic.setup_helpers import simple_math_task
except ImportError as e:
    print(
        f"Warning: Could not import from comparison_logic.setup_helpers ({e}). Defining locally."
    )

    # Define locally as the final fallback
    def simple_math_task(n=10**6):
        s = sum(i * i for i in range(int(n)))
        return s


# Use the robust DATA_DIR path
BASE_DIR = DATA_DIR
DATA_FILE_A = BASE_DIR / "data_a.txt"


def task_a_read_file(filepath):
    """Simulates reading data."""
    print(
        f"(Target) Starting Task A: Reading {filepath.name} from {filepath.parent}..."
    )
    start_t = time.perf_counter()
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
        read_time = time.perf_counter() - start_t
        print(f"(Target) Finished Task A: Read {len(lines)} lines in {read_time:.4f}s.")
        return len(lines)
    except FileNotFoundError:
        print(f"(Target) Error: File not found {filepath}")
        return 0
    except Exception as e:
        print(f"(Target) Error reading file {filepath}: {e}")
        return 0


def task_b_process_data(line_count):
    """Simulates CPU processing based on prior task."""
    print(f"(Target) Starting Task B: Processing based on {line_count} lines...")
    start_t = time.perf_counter()
    # Make calculation dependent on input, ensure it's not trivially zero
    n_calc = max(1000, line_count * 1000)  # Avoid range(0)
    result = simple_math_task(n_calc)
    proc_time = time.perf_counter() - start_t
    print(f"(Target) Finished Task B in {proc_time:.4f}s.")
    return result  # Return the actual result for potential use


# Main execution block
if __name__ == "__main__":
    print("\n--- Target Simple Script Running ---")
    local_start_time = time.perf_counter()

    res_a = task_a_read_file(DATA_FILE_A)
    res_b = task_b_process_data(res_a)  # Depends on A

    local_end_time = time.perf_counter()
    # Avoid printing potentially huge result from simple_math_task
    print(f"(Target) Results: A_lines={res_a}, B_result=LengthyNum")
    print(
        f"(Target) Direct Run Total Time: {local_end_time - local_start_time} seconds"
    )
    print("--- Target Simple Script End ---")
