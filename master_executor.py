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
        # REMOVED: self._in_main_if flag is no longer needed with this approach

    def _is_main_if(self, node):
        """Checks if an If node is the 'if __name__ == "__main__":' block."""
        # (Keep this function as is)
        if not isinstance(node, ast.If):
            return False
        # Check parent is Module (top-level)
        if not isinstance(node.parent, ast.Module):
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
        if isinstance(node.parent, ast.Module):
            self.imports.append(node)
        # No generic_visit needed here if we only care about top-level

    def visit_ImportFrom(self, node):
        if isinstance(node.parent, ast.Module):
            self.imports.append(node)
        # No generic_visit needed here

    def visit_FunctionDef(self, node):
        if isinstance(node.parent, ast.Module):
            self.functions[node.name] = node
        # Do not visit function bodies for top-level segmentation
        # self.generic_visit(node)

    def visit_If(self, node):
        # --- Handle the main execution block ---
        if self._is_main_if(node):
            # Add all statements directly from the main block's body
            # print(f"DEBUG: Found main 'if' block. Adding {len(node.body)} body nodes.")
            for body_node in node.body:
                self.main_block_nodes.append(body_node)
            # DO NOT traverse deeper into the main block body from here for segmentation.
            # The goal was just to capture these top-level statements inside it.
        # --- Handle other top-level statements (including other 'if's) ---
        elif isinstance(node.parent, ast.Module):
            # print(f"DEBUG: Adding other top-level If node: {ast.unparse(node.test)}")
            self.main_block_nodes.append(node)
            # Visit children of OTHER top-level ifs if necessary for their structure
            self.generic_visit(node)
        else:
            # This 'if' is nested inside a function or another block, ignore for top-level main block.
            # Still need to visit its children in case they contain something relevant later?
            # Depending on exact goals, might skip this too. For now, keep it.
            self.generic_visit(node)

    def generic_visit(self, node):
        # Only add top-level statements that are NOT imports, functions, or the main 'if' block itself
        is_top_level_other = isinstance(node.parent, ast.Module) and not isinstance(
            node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.If)  # Check If too
        )

        if is_top_level_other:
            # print(f"DEBUG: Adding generic top-level node: {type(node).__name__}")
            self.main_block_nodes.append(node)

        # Continue traversal for children - needed to find nested structures if the visitor logic expands later
        super().generic_visit(node)


def _add_parents(tree):
    """Recursively add parent pointers to all nodes in the AST."""
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    tree.parent = None  # Root has no parent
    return tree


def parse_script(script_path):
    """Parses the script using AST and returns segments."""
    try:
        print(f"DEBUG: Reading script {script_path}...")
        with open(script_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        print(f"DEBUG: Parsing script {script_path}...")
        tree = ast.parse(source_code, filename=str(script_path))
        tree_with_parents = _add_parents(tree)
        segmenter = CodeSegmenter()
        print(f"DEBUG: Visiting AST for {script_path}...")
        segmenter.visit(tree_with_parents)
        print(
            f"DEBUG: Parsing complete. Imports: {len(segmenter.imports)}, Functions: {len(segmenter.functions)}, Main Nodes: {len(segmenter.main_block_nodes)}"
        )
        return (
            segmenter.imports,
            segmenter.functions,
            segmenter.main_block_nodes,
            source_code,
        )
    except Exception as e:
        print(f"Error parsing script {script_path}: {e}")
        traceback.print_exc()
        return None, None, None, None


# --- Execution ---


def execute_normally(script_path):
    """Runs the script directly as a subprocess."""
    print(f"\n--- Running Normally: {script_path.name} ---")
    start_time = time.perf_counter()
    try:
        # Using subprocess ensures a clean environment like running from terminal
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        end_time = time.perf_counter()
        print("--- Normal Output ---")
        print(result.stdout)
        if result.stderr:
            print("--- Normal Error Output ---")
            print(result.stderr)
        print("---------------------")
        print(f"Normal Execution Time: {end_time - start_time:.4f} seconds")
    except FileNotFoundError:
        end_time = time.perf_counter()
        print(f"Error: Script '{script_path}' not found.")
    except subprocess.CalledProcessError as e:
        end_time = time.perf_counter()
        print(f"Error during normal execution (return code {e.returncode}):")
        print("--- Error Output (stdout) ---")
        print(e.stdout)
        print("--- Error Output (stderr) ---")
        print(e.stderr)
        print("--------------------")
        print(f"Normal Execution Time (Failed): {end_time - start_time:.4f} seconds")
    except Exception as e:
        end_time = time.perf_counter()
        print(f"An unexpected error occurred during normal execution: {e}")
        traceback.print_exc()
        print(f"Normal Execution Time (Failed): {end_time - start_time:.4f} seconds")


def execute_broken(imports, functions, main_nodes, script_path, source_code):
    """
    Executes the script by defining functions and then running the main block.
    Modifies sys.path temporarily and injects __file__, __name__.
    """
    print(f"\n--- Running Broken: {script_path.name} ---")
    start_time = time.perf_counter()

    # Get the absolute path of the target script
    target_script_abs_path = str(script_path.resolve())

    # Prepare execution context (namespace)
    # Initialize with __file__ and __name__
    exec_namespace = {
        "__file__": target_script_abs_path,
        "__name__": "__main__",  # Crucial for 'if __name__ == "__main__"' blocks
    }

    # Get the workspace directory (parent of the target script's directory)
    workspace_dir = script_path.resolve().parent.parent
    original_sys_path = sys.path[:]  # Save original path
    path_added = False  # Track if we modified sys.path

    try:
        # --- Temporarily modify sys.path ---
        if str(workspace_dir) not in sys.path:
            sys.path.insert(0, str(workspace_dir))
            path_added = True
            print(f"DEBUG: Temporarily added {workspace_dir} to sys.path")
        # ------------------------------------

        # 1. Execute Imports
        print("Executing imports...")
        if imports:
            import_source = "\n".join([ast.unparse(node) for node in imports])
            exec(
                compile(import_source, f"{script_path.name}_imports", "exec"),
                exec_namespace,
            )
            print("Imports executed.")
        else:
            print("No imports found.")

        # 2. Define Functions (Concurrently - for structure, not significant speedup)
        print(f"Defining {len(functions)} functions...")
        if functions:
            # Use a single thread for definitions as they share the namespace;
            # true parallel definition isn't safe without locks or separate namespaces.
            # The overhead of threads might outweigh benefits here anyway.
            for name, node in functions.items():
                try:
                    func_source = ast.unparse(node)
                    exec(
                        compile(func_source, f"{script_path.name}_{name}", "exec"),
                        exec_namespace,
                    )
                except Exception as e:
                    print(f"Error defining function {name}: {e}")
                    raise
            # The concurrent version, if needed (use with caution due to namespace sharing):
            # with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(functions))) as executor:
            #     futures = {}
            #     for name, node in functions.items():
            #         func_source = ast.unparse(node)
            #         future = executor.submit(exec, compile(func_source, f"{script_path.name}_{name}", 'exec'), exec_namespace)
            #         futures[future] = name
            #     for future in concurrent.futures.as_completed(futures):
            #         try:
            #             future.result()
            #         except Exception as e:
            #             print(f"Error defining function {futures[future]}: {e}")
            #             raise
            print("Functions defined.")
        else:
            print("No functions to define.")

        # 3. Execute Main Block (Sequentially)
        #    True concurrency here requires complex dependency analysis.
        print("Executing main block logic...")
        if main_nodes:
            # Filter out None nodes just in case segmenter added some accidentally
            valid_main_nodes = [node for node in main_nodes if node is not None]
            if valid_main_nodes:
                main_source = "\n".join(
                    [ast.unparse(node) for node in valid_main_nodes]
                )
                # print("--- Main Block Source ---")
                # print(main_source)
                # print("-----------------------")
                if main_source.strip():
                    exec(
                        compile(main_source, f"{script_path.name}_main", "exec"),
                        exec_namespace,
                    )
                    print("Main block executed.")
                else:
                    print("Main block source is empty after unparsing.")
            else:
                print("No valid main block nodes found.")
        else:
            print("No main block nodes identified by parser.")

        end_time = time.perf_counter()
        print("---------------------")
        print(f"Broken Execution Time: {end_time - start_time:.4f} seconds")
        print("(Note: Main block logic executed sequentially by master)")

    except Exception as e:
        end_time = time.perf_counter()
        print(f"\nError during broken execution: {e}")
        traceback.print_exc()
        print("--------------------")
        print(f"Broken Execution Time (Failed): {end_time - start_time:.4f} seconds")
    finally:
        # --- Restore original sys.path ---
        sys.path = original_sys_path
        if path_added:
            print(f"DEBUG: Restored original sys.path")
        # ---------------------------------


# --- Main Script Logic ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute a Python script normally and in a 'broken' fashion for comparison."
    )
    parser.add_argument("script_path", help="Path to the Python script to execute.")
    args = parser.parse_args()

    target_script = Path(args.script_path)

    if not target_script.is_file():
        print(f"Error: File not found: {target_script}")
        sys.exit(1)

    # Ensure setup has run and data exists potentially
    setup_script = Path(__file__).parent / "comparison_logic" / "setup_helpers.py"
    if setup_script.exists():
        print("DEBUG: Ensuring setup has run...")
        try:
            subprocess.run(
                [sys.executable, str(setup_script)], check=True, capture_output=True
            )
        except Exception as e:
            print(f"Warning: Failed to run setup script automatically: {e}")
    else:
        print(f"Warning: Setup script not found at {setup_script}. Ensure data exists.")

    print(f"\nAnalyzing script: {target_script}")
    imports, functions, main_nodes, source_code = parse_script(target_script)

    if source_code is None:
        print("Exiting due to parsing error.")
        sys.exit(1)

    # Run 1: Normal Execution
    execute_normally(target_script)

    # Run 2: Broken Execution
    execute_broken(imports, functions, main_nodes, target_script, source_code)
