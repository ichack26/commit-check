import ast
from collections import defaultdict

class CallGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.graph = defaultdict(set)
        self.current_function = None
        self.class_stack = []  # track nesting of classes

    def visit_ClassDef(self, node):
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        prev_func = self.current_function

        if self.class_stack:
            full_name = ".".join(self.class_stack + [node.name])
        else:
            full_name = node.name

        self.current_function = full_name
        self.generic_visit(node)
        self.current_function = prev_func

    def visit_Call(self, node):
        if not self.current_function:
            return

        # f()
        if isinstance(node.func, ast.Name):
            self.graph[self.current_function].add(node.func.id)

        # Foo.bar() or Outer.Inner.foo()
        elif isinstance(node.func, ast.Attribute):
            # If value is a Name (e.g., Foo.bar)
            if isinstance(node.func.value, ast.Name):
                cls = node.func.value.id
                method = node.func.attr
                self.graph[self.current_function].add(f"{cls}.{method}")
            else:
                # fallback
                self.graph[self.current_function].add(node.func.attr)

        self.generic_visit(node)
