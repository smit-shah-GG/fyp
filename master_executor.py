#!/usr/bin/env python3

#!/usr/bin/env python3

# work/master_executor.py
import argparse
import ast
import concurrent.futures
import time
import subprocess
import sys
from pathlib import Path
import traceback
import logging
import csv
import os
from datetime import datetime

# --- Configuration ---
LOG_FILE = Path(__file__).parent / "master_executor.log"
STATS_FILE = Path(__file__).parent / "execution_stats.csv"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
STATS_FIELDNAMES = [
    "timestamp",
    "script_name",
    "normal_time_s",
    "normal_status",
    "broken_time_s",
    "broken_status",
    "error_message", # Added to capture specific error info
]

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout), # Log to console as well
    ],
)

# --- AST Analysis ---

class CodeSegmenter(ast.NodeVisitor):
    """
    Parses a Python script into imports, functions, and the main execution block.
    Requires parent pointers to be set before visiting.
    """

    def __init__(self):
        self.functions = {}  # dict mapping function name to AST node
        self.main_block_nodes = []
        self.imports = []

    def _is_main_if(self, node):
        """Checks if an If node is the 'if __name__ == "__main__":' block."""
        if not isinstance(node, ast.If):
            return False
        if not hasattr(node, 'parent') or not isinstance(node.parent, ast.Module):
            # Check if parent exists and is Module (top-level)
            return False
        # Check test structure
        if isinstance(node.test, ast.Compare):
            test = node.test
            if isinstance(test.left, ast.Name) and test.left.id == "__name__":
                if len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
                    if len(test.comparators) == 1 and isinstance(
                        test.comparators[0], ast.Constant
                    ):
                        if test.comparators[0].value == "__main__":
                            return True
        return False

    def visit_Import(self, node):
        if hasattr(node, 'parent') and isinstance(node.parent, ast.Module):
            self.imports.append(node)

    def visit_ImportFrom(self, node):
        if hasattr(node, 'parent') and isinstance(node.parent, ast.Module):
            self.imports.append(node)

    def visit_FunctionDef(self, node):
        if hasattr(node, 'parent') and isinstance(node.parent, ast.Module):
            self.functions[node.name] = node
        # Do not visit function bodies for top-level segmentation

    def visit_If(self, node):
        if self._is_main_if(node):
            # logging.debug(f"Found main 'if' block. Adding {len(node.body)} body nodes.")
            for body_node in node.body:
                # Add parent pointers to nodes within the main block if needed later
                if not hasattr(body_node, 'parent'):
                    body_node.parent = node # Assign the 'If' as parent
                self.main_block_nodes.append(body_node)
        elif hasattr(node, 'parent') and isinstance(node.parent, ast.Module):
            # logging.debug(f"Adding other top-level If node: {ast.unparse(node.test)}")
            self.main_block_nodes.append(node)
            self.generic_visit(node) # Visit children of OTHER top-level ifs
        else:
            self.generic_visit(node) # Visit children of nested ifs

    def visit(self, node):
        """Override visit to handle adding nodes that are not caught by specific visit methods."""
        # First, call the specific visitor if it exists
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, None)
        if visitor:
            visitor(node)
        else:
            # If no specific visitor, handle generic top-level additions here
            if hasattr(node, 'parent') and isinstance(node.parent, ast.Module) and not isinstance(
                node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.If)
            ):
                # logging.debug(f"Adding generic top-level node: {type(node).__name__}")
                self.main_block_nodes.append(node)
            # Always call generic_visit to ensure traversal continues
            self.generic_visit(node)

    def generic_visit(self, node):
        # Continue traversal for children
        super().generic_visit(node)


def _add_parents(tree):
    """Recursively add parent pointers to all nodes in the AST."""
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    # Root has no parent, explicitly setting to None might avoid issues if not set
    if hasattr(tree, 'parent'):
        tree.parent = None
    return tree


def parse_script(script_path):
    """Parses the script using AST and returns segments."""
    try:
        logging.info(f"Reading script {script_path}...")
        with open(script_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        logging.info(f"Parsing script {script_path}...")
        tree = ast.parse(source_code, filename=str(script_path))
        tree_with_parents = _add_parents(tree)
        segmenter = CodeSegmenter()
        logging.info(f"Visiting AST for {script_path}...")
        segmenter.visit(tree_with_parents)
        logging.info(
            f"Parsing complete. Imports: {len(segmenter.imports)}, Functions: {len(segmenter.functions)}, Main Nodes: {len(segmenter.main_block_nodes)}"
        )
        return (
            segmenter.imports,
            segmenter.functions,
            segmenter.main_block_nodes,
            source_code,
        )
    except Exception as e:
        logging.exception(f"Error parsing script {script_path}: {e}")
        return None, None, None, None


# --- Execution ---

def execute_normally(script_path):
    """Runs the script directly as a subprocess. Returns (time, status, error_msg)."""
    logging.info(f"--- Running Normally: {script_path.name} ---")
    start_time = time.perf_counter()
    status = "Failure"
    error_msg = ""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True, # Raises CalledProcessError on non-zero exit
            encoding="utf-8",
            timeout=300 # Add a timeout (e.g., 5 minutes)
        )
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        logging.info("--- Normal Output ---")
        logging.info(result.stdout)
        if result.stderr:
            logging.warning("--- Normal Error Output ---")
            logging.warning(result.stderr)
        logging.info("---------------------")
        logging.info(f"Normal Execution Time: {exec_time:.4f} seconds")
        status = "Success"
        return exec_time, status, error_msg
    except FileNotFoundError:
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        error_msg = f"Script '{script_path}' not found."
        logging.error(error_msg)
        return exec_time, status, error_msg
    except subprocess.CalledProcessError as e:
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        error_msg = f"Return code {e.returncode}. Stdout: '{e.stdout[:100]}...'. Stderr: '{e.stderr[:100]}...'"
        logging.error(f"Error during normal execution (return code {e.returncode}):")
        logging.error("--- Error Output (stdout) ---")
        logging.error(e.stdout)
        logging.error("--- Error Output (stderr) ---")
        logging.error(e.stderr)
        logging.error("--------------------")
        logging.error(f"Normal Execution Time (Failed): {exec_time:.4f} seconds")
        return exec_time, status, error_msg
    except subprocess.TimeoutExpired:
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        error_msg = "Execution timed out."
        logging.error(error_msg)
        logging.error(f"Normal Execution Time (Timeout): {exec_time:.4f} seconds")
        return exec_time, status, error_msg
    except Exception as e:
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        error_msg = f"Unexpected error: {str(e)}"
        logging.exception(f"An unexpected error occurred during normal execution: {e}")
        logging.error(f"Normal Execution Time (Failed): {exec_time:.4f} seconds")
        return exec_time, status, error_msg


def execute_broken(imports, functions, main_nodes, script_path, source_code):
    """
    Executes the script by defining functions and then running the main block.
    Modifies sys.path temporarily and injects __file__, __name__.
    Returns (time, status, error_msg).
    """
    logging.info(f"--- Running Broken: {script_path.name} ---")
    start_time = time.perf_counter()
    status = "Failure"
    error_msg = ""

    target_script_abs_path = str(script_path.resolve())
    exec_namespace = {
        "__file__": target_script_abs_path,
        "__name__": "__main__",
    }

    workspace_dir = script_path.resolve().parent
    # Use parent of the target script's dir if 'comparison_logic' is sibling to 'targets'
    # workspace_dir = script_path.resolve().parent.parent # Use this if helpers are one level up

    original_sys_path = sys.path[:]
    path_added = False

    try:
        # --- Temporarily modify sys.path ---
        # Add the target script's directory for relative imports within the target
        script_dir_str = str(script_path.resolve().parent)
        if script_dir_str not in sys.path:
            sys.path.insert(0, script_dir_str)
            logging.debug(f"Temporarily added script dir {script_dir_str} to sys.path")
            # We might not need path_added tracking anymore if we always restore

        # Also add workspace dir if needed for comparison_logic etc.
        workspace_dir_str = str(workspace_dir)
        if workspace_dir_str != script_dir_str and workspace_dir_str not in sys.path:
            sys.path.insert(0, workspace_dir_str)
            logging.debug(f"Temporarily added workspace dir {workspace_dir_str} to sys.path")
        # ------------------------------------


        # 1. Execute Imports
        logging.info("Executing imports...")
        if imports:
            import_source = "\n".join([ast.unparse(node) for node in imports])
            # Use filename arg for better tracebacks
            compiled_code = compile(import_source, f"{script_path.name}_imports", "exec")
            exec(compiled_code, exec_namespace)
            logging.info("Imports executed.")
        else:
            logging.info("No imports found.")

        # 2. Define Functions
        logging.info(f"Defining {len(functions)} functions...")
        if functions:
            # Sequentially define to avoid namespace issues
            for name, node in functions.items():
                try:
                    func_source = ast.unparse(node)
                    compiled_func = compile(func_source, f"{script_path.name}_{name}", "exec")
                    exec(compiled_func, exec_namespace)
                except Exception as e:
                    logging.exception(f"Error defining function {name}: {e}")
                    raise # Re-raise to be caught by the outer handler
            logging.info("Functions defined.")
        else:
            logging.info("No functions to define.")

        # 3. Execute Main Block
        logging.info("Executing main block logic...")
        if main_nodes:
            valid_main_nodes = [node for node in main_nodes if node is not None]
            if valid_main_nodes:
                main_source = "\n".join(
                    [ast.unparse(node) for node in valid_main_nodes]
                )
                # logging.debug("--- Main Block Source ---")
                # logging.debug(main_source)
                # logging.debug("-----------------------")
                if main_source.strip():
                    compiled_main = compile(main_source, f"{script_path.name}_main", "exec")
                    exec(compiled_main, exec_namespace)
                    logging.info("Main block executed.")
                else:
                    logging.info("Main block source is empty after unparsing.")
            else:
                logging.info("No valid main block nodes found.")
        else:
            logging.info("No main block nodes identified by parser.")

        end_time = time.perf_counter()
        exec_time = end_time - start_time
        status = "Success"
        logging.info("---------------------")
        logging.info(f"Broken Execution Time: {exec_time:.4f} seconds")
        logging.info("(Note: Main block logic executed sequentially by master)")
        return exec_time, status, error_msg

    except Exception as e:
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        error_msg = f"Broken exec error: {type(e).__name__}: {str(e)}"
        logging.exception(f"Error during broken execution: {e}")
        logging.error("--------------------")
        logging.error(f"Broken Execution Time (Failed): {exec_time:.4f} seconds")
        return exec_time, status, error_msg # Return failure status
    finally:
        # --- Restore original sys.path ---
        sys.path[:] = original_sys_path # Restore in place
        logging.debug(f"Restored original sys.path")
        # ---------------------------------


# --- Statistics Saving ---

def save_stats_to_csv(stats_dict, filename):
    """Appends a dictionary of stats to a CSV file."""
    file_exists = filename.exists()
    try:
        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=STATS_FIELDNAMES)
            if not file_exists or os.path.getsize(filename) == 0:
                writer.writeheader() # Write header only if file is new/empty
            writer.writerow(stats_dict)
        logging.info(f"Statistics saved to {filename}")
    except IOError as e:
        logging.error(f"Failed to save statistics to {filename}: {e}")
    except Exception as e:
        logging.exception(f"Unexpected error saving statistics: {e}")


# --- Main Script Logic ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute a Python script normally and in a 'broken' fashion for comparison."
    )
    parser.add_argument("script_path", help="Path to the Python script to execute.")
    args = parser.parse_args()

    target_script = Path(args.script_path)

    logging.info(f"--- Master Executor Started for {target_script.name} ---")

    stats = {
        "timestamp": datetime.now().isoformat(),
        "script_name": target_script.name,
        "normal_time_s": None,
        "normal_status": "Not Run",
        "broken_time_s": None,
        "broken_status": "Not Run",
        "error_message": ""
    }

    if not target_script.is_file():
        error_msg = f"File not found: {target_script}"
        logging.error(error_msg)
        stats["normal_status"] = "Failure"
        stats["broken_status"] = "Failure"
        stats["error_message"] = error_msg
        save_stats_to_csv(stats, STATS_FILE)
        sys.exit(1)

    # Ensure setup has run (optional, based on target script needs)
    setup_script = Path(__file__).parent / "comparison_logic" / "setup_helpers.py"
    if setup_script.exists():
        logging.debug("Ensuring setup has run...")
        try:
            # Run setup silently unless it fails
            subprocess.run(
                [sys.executable, str(setup_script)], check=True, capture_output=True
            )
            logging.debug("Setup script completed successfully.")
        except Exception as e:
            logging.warning(f"Failed to run setup script automatically: {e}")
    else:
        logging.warning(f"Setup script not found at {setup_script}. Ensure data exists if needed by target.")

    logging.info(f"Analyzing script: {target_script}")
    imports, functions, main_nodes, source_code = parse_script(target_script)

    if source_code is None:
        logging.error("Exiting due to parsing error.")
        stats["normal_status"] = "Failure"
        stats["broken_status"] = "Failure"
        stats["error_message"] = "Parsing failed"
        save_stats_to_csv(stats, STATS_FILE)
        sys.exit(1)

    # Run 1: Normal Execution
    norm_time, norm_status, norm_err = execute_normally(target_script)
    stats["normal_time_s"] = f"{norm_time:.4f}" if norm_time is not None else None
    stats["normal_status"] = norm_status
    if norm_err and not stats["error_message"]: # Prioritize error message
        stats["error_message"] = f"Normal: {norm_err}"

    # Run 2: Broken Execution
    # Only run broken if parsing succeeded
    if source_code is not None:
        brok_time, brok_status, brok_err = execute_broken(
            imports, functions, main_nodes, target_script, source_code
        )
        stats["broken_time_s"] = f"{brok_time:.4f}" if brok_time is not None else None
        stats["broken_status"] = brok_status
        if brok_err:
            if stats["error_message"]:
                stats["error_message"] += f" | Broken: {brok_err}"
            else:
                stats["error_message"] = f"Broken: {brok_err}"

    # Save combined statistics
    save_stats_to_csv(stats, STATS_FILE)

    logging.info(f"--- Master Executor Finished for {target_script.name} ---")
