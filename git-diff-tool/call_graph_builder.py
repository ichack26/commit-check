import ast
from collections import defaultdict

class CallGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        # {function_name: set(called_function_names)}
        self.graph = defaultdict(set)
        self.current_function = None

    def visit_FunctionDef(self, node):
        previous = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = previous

    def visit_ClassDef(self, node):
        # Visit methods
        self.generic_visit(node)

    def visit_Call(self, node):
        if self.current_function:
            if isinstance(node.func, ast.Name):
                # Simple call: g()
                self.graph[self.current_function].add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                # Method call: obj.method()
                self.graph[self.current_function].add(node.func.attr)
        self.generic_visit(node)