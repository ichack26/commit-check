import ast
from collections import defaultdict

class CallGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.graph = defaultdict(set)  # function -> called functions
        self.current_function = None
        self.class_stack = []
        self.classes = {}  # class_name -> (start_lineno, end_lineno)
        self.function_to_class = {}  # method -> enclosing class

    def visit_ClassDef(self, node):
        self.class_stack.append(node.name)
        full_name = ".".join(self.class_stack)
        self.classes[full_name] = (node.lineno, node.end_lineno)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        prev_func = self.current_function

        if self.class_stack:
            # fully qualified name for the method
            full_name = ".".join(self.class_stack + [node.name])
            self.function_to_class[full_name] = ".".join(self.class_stack)
            # also map just the method name for easier lookup later
            self.function_to_class[node.name] = ".".join(self.class_stack)
        else:
            full_name = node.name

        self.current_function = full_name
        self.generic_visit(node)
        self.current_function = prev_func


    def visit_Call(self, node):
        if not self.current_function:
            return

        # f() → simple function
        if isinstance(node.func, ast.Name):
            self.graph[self.current_function].add(node.func.id)

        # attribute calls → class method or property
        elif isinstance(node.func, ast.Attribute):
            # detect instantiation or class method
            parts = []
            val = node.func
            while isinstance(val, ast.Attribute):
                parts.append(val.attr)
                val = val.value
            if isinstance(val, ast.Name):
                parts.append(val.id)
            full = ".".join(reversed(parts))
            self.graph[self.current_function].add(full)

        self.generic_visit(node)

    def visit_Attribute(self, node):
        # Optional: capture property access like obj.prop
        # Could be used to mark class as touched
        self.generic_visit(node)
