import ast

class CodeSnippetVisitor(ast.NodeVisitor):
    def __init__(self):
        self.snippets = []  # List to hold each code snippet
        self.current_snippet = []  # Temporarily hold nodes belonging to the current snippet
        self.inside_snippet = False  # To track if we're inside a larger construct
        self.import_snippet = []  # Temporarily hold all import-related nodes

    def add_snippet(self):
        if self.current_snippet:
            self.snippets.append(self.current_snippet)
            self.current_snippet = []

    def finalize_import_snippet(self):
        if self.import_snippet:
            # Add all grouped import statements as one snippet
            self.snippets.append(self.import_snippet)
            self.import_snippet = []

    def visit_FunctionDef(self, node):
        self.finalize_import_snippet()  # Finalize import snippet if any before new block
        if not self.inside_snippet:
            self.add_snippet()
            self.current_snippet.append(node)
            self.add_snippet()  # Finalize this function as a snippet
            self.inside_snippet = True  # Entering a snippet
            self.generic_visit(node)  # Visit function body
            self.inside_snippet = False  # Exiting snippet after visit

    def visit_If(self, node):
        self.finalize_import_snippet()  # Finalize import snippet if any before new block
        if not self.inside_snippet:
            self.add_snippet()
            self.current_snippet.append(node)
            self.add_snippet()
            self.inside_snippet = True
            self.generic_visit(node)
            self.inside_snippet = False

    def visit_For(self, node):
        self.finalize_import_snippet()  # Finalize import snippet if any before new block
        if not self.inside_snippet:
            self.add_snippet()
            self.current_snippet.append(node)
            self.add_snippet()
            self.inside_snippet = True
            self.generic_visit(node)
            self.inside_snippet = False

    def visit_While(self, node):
        self.finalize_import_snippet()  # Finalize import snippet if any before new block
        if not self.inside_snippet:
            self.add_snippet()
            self.current_snippet.append(node)
            self.add_snippet()
            self.inside_snippet = True
            self.generic_visit(node)
            self.inside_snippet = False

    def visit_Assign(self, node):
        if not self.inside_snippet:
            self.current_snippet.append(node)

    def visit_Expr(self, node):
        if not self.inside_snippet:
            self.current_snippet.append(node)

    def visit_Import(self, node):
        # Group import statements together
        self.import_snippet.append(node)

    def visit_ImportFrom(self, node):
        # Group import-from statements together with normal imports
        self.import_snippet.append(node)

# Function to read a Python file and extract snippets
def extract_snippets_from_file(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    # Parse the code into an AST
    tree = ast.parse(code)

    # Use the custom visitor
    visitor = CodeSnippetVisitor()
    visitor.visit(tree)

    # Finalize any remaining snippets
    visitor.add_snippet()
    visitor.finalize_import_snippet()

    # Output results
    print("\nExtracted Snippets:")
    for i, snippet in enumerate(visitor.snippets):
        print(f"Snippet {i+1}:\n{ast.unparse(snippet)}\n{'-'*40}")

# Example usage
file_path = "demo3.py" # Replace with your actual Python file path
extract_snippets_from_file(file_path)
