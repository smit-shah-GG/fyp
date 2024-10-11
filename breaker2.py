import ast

class CodeSnippetVisitor(ast.NodeVisitor):
    def __init__(self):
        self.snippets = []  # List to hold each code snippet
        self.current_snippet = []  # Temporarily hold nodes belonging to the current snippet

    def add_snippet(self):
        if self.current_snippet:
            self.snippets.append(self.current_snippet)
            self.current_snippet = []  # Reset for the next snippet

    def visit_FunctionDef(self, node):
        # Treat each function definition as a new snippet
        self.add_snippet()
        self.current_snippet.append(node)
        self.add_snippet()
        self.generic_visit(node)

    def visit_If(self, node):
        # Treat each if statement as a new snippet
        self.add_snippet()
        self.current_snippet.append(node)
        self.add_snippet()
        self.generic_visit(node)

    def visit_For(self, node):
        # Treat each for loop as a new snippet
        self.add_snippet()
        self.current_snippet.append(node)
        self.add_snippet()
        self.generic_visit(node)

    def visit_While(self, node):
        # Treat each while loop as a new snippet
        self.add_snippet()
        self.current_snippet.append(node)
        self.add_snippet()
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Treat assignments as snippets, but allow them to be grouped together
        self.current_snippet.append(node)

    def visit_Expr(self, node):
        # Capture expressions like function calls, which can be individual snippets
        self.current_snippet.append(node)

    def visit_Import(self, node):
        # Treat import statements as separate snippets
        self.add_snippet()
        self.current_snippet.append(node)
        self.add_snippet()

    def visit_ImportFrom(self, node):
        # Treat import-from statements as separate snippets
        self.add_snippet()
        self.current_snippet.append(node)
        self.add_snippet()

# Example Python code
code = """
import numpy as np

x = 10
y = x + 5

def foo(a):
    if a > 10:
        return a * 2
    else:
        return a + 1

for i in range(5):
    print(i)
"""

# Parse the code into an AST
tree = ast.parse(code)

# Use the custom visitor
visitor = CodeSnippetVisitor()
visitor.visit(tree)

# Add the final snippet
visitor.add_snippet()

# Output results
print("\nExtracted Snippets:")
for i, snippet in enumerate(visitor.snippets):
    print(f"Snippet {i+1}:\n{ast.unparse(snippet)}\n{'-'*40}")
