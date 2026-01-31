from call_graph_builder import CallGraphBuilder

import ast
import re
import subprocess

class Analyser:
    def parse_file_to_ast(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return ast.parse(content, filename=filepath)

    def get_staged_python_files():
        """Return a list of staged Python files."""
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f.endswith(".py") and f]

    def get_staged_diff_for_file(file_path):
        """Return the staged diff as a string for a given file."""
        result = subprocess.run(
            ["git", "diff", "--cached", "-U0", file_path],  # -U0 = zero context, only changed lines
            capture_output=True,
            text=True
        )
        return result.stdout

    def get_changed_lines_from_diff(diff_text):
        """
        Parse git diff text and return a set of added/modified line numbers.
        """
        changed_lines = set()
        hunk_pattern = re.compile(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@')
        for line in diff_text.splitlines():
            match = hunk_pattern.match(line)
            if match:
                start_line = int(match.group(1))
                line_count = int(match.group(2) or 1)
                changed_lines.update(range(start_line, start_line + line_count))
        return changed_lines

    def get_functions_in_file(file_path):
        """
        Return a list of functions in the file:
        [{'name': 'f', 'start': 10, 'end': 15}, ...]
        """
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "start": node.lineno,
                    "end": node.end_lineno
                })
        return functions

    def get_changed_functions(file_path):
        diff = Analyser.get_staged_diff_for_file(file_path)
        changed_lines = Analyser.get_changed_lines_from_diff(diff)
        functions = Analyser.get_functions_in_file(file_path)

        affected_functions = []
        for func in functions:
            # If any changed line falls within the function's range, mark it
            if changed_lines.intersection(range(func["start"], func["end"] + 1)):
                affected_functions.append(func["name"])
        return affected_functions

    def traverse_call_graph(graph, start_nodes):
        """
        Return all functions reachable from start_nodes in the call graph.
        
        graph: {func_name: set(called_funcs)}
        start_nodes: list or set of functions
        """
        visited = set()
        stack = list(start_nodes)
        while stack:
            func = stack.pop()
            if func not in visited:
                visited.add(func)
                # Add any functions this function calls
                stack.extend(graph.get(func, []))
        return visited

    def build_call_graph_for_changed_functions(file_path, affected_functions):
        tree = Analyser.parse_file_to_ast(file_path)
        builder = CallGraphBuilder()
        builder.visit(tree)

        # Get all functions reachable from affected_functions
        all_relevant_functions = Analyser.traverse_call_graph(builder.graph, affected_functions)

        # Filter the builder graph to only include relevant functions
        filtered_graph = {k: v for k, v in builder.graph.items() if k in all_relevant_functions}
        return filtered_graph

    def get_function_snippets(file_path, function_names):
        """
        Return a dict {function_name: code_string} for specified function_names
        """
        with open(file_path, "r", encoding="utf-8") as f:
            code_lines = f.readlines()

        tree = ast.parse("".join(code_lines))
        snippets = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in function_names:
                start, end = node.lineno - 1, node.end_lineno  # lineno is 1-indexed
                func_code = "".join(code_lines[start:end])
                snippets[node.name] = func_code

        return snippets

    def traverse_graph_for_snippets(graph, start_functions):
        """
        graph: {func: set(called_funcs)}
        start_functions: list of functions changed
        returns: set of all reachable function names
        """
        visited = set()
        stack = list(start_functions)
        while stack:
            func = stack.pop()
            if func not in visited:
                visited.add(func)
                stack.extend(graph.get(func, []))
        return visited
    
    def topological_sort(graph):
        visited = set()
        order = []

        def dfs(node):
            if node not in visited:
                visited.add(node)
                for neighbor in graph.get(node, []):
                    dfs(neighbor)
                order.append(node)

        for node in graph:
            dfs(node)
        return order[::-1]  # reverse to get correct order
