#!/usr/bin/env python3
from anthropic import Anthropic
from dotenv import load_dotenv 

import subprocess

load_dotenv() 

import subprocess
import re

from collections import defaultdict
import ast

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

def parse_file_to_ast(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return ast.parse(content, filename=filepath)

def get_staged_files():
    """Return list of staged Python files"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    files = result.stdout.strip().split("\n")
    # Only Python files
    return [f for f in files if f.endswith(".py") and f]

def build_graph_for_staged_files():
    files = get_staged_files()
    builder = CallGraphBuilder()
    for f in files:
        tree = parse_file_to_ast(f)
        builder.visit(tree)
    return builder.graph

def traverse_graph(graph, start_nodes):
    """Return all functions reachable from start_nodes"""
    visited = set()
    stack = list(start_nodes)
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            stack.extend(graph.get(node, []))
    return visited

def get_diff_for_functions(functions, files):
    """Return a mapping of {filename: code snippet} for given functions"""
    snippets = {}
    for f in files:
        with open(f, "r") as fh:
            code = fh.read()
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in functions:
                start, end = node.lineno-1, node.end_lineno
                snippets.setdefault(f, []).append("\n".join(code.splitlines()[start:end]))
    return snippets

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
    diff = get_staged_diff_for_file(file_path)
    changed_lines = get_changed_lines_from_diff(diff)
    functions = get_functions_in_file(file_path)

    affected_functions = []
    for func in functions:
        # If any changed line falls within the function's range, mark it
        if changed_lines.intersection(range(func["start"], func["end"] + 1)):
            affected_functions.append(func["name"])
    return affected_functions

def build_call_graph_for_changed_functions(file_path, affected_functions):
    tree = parse_file_to_ast(file_path)
    builder = CallGraphBuilder()

    builder.visit(tree)
    
    # Filter graph to only include affected functions + their calls
    filtered_graph = {k: v for k, v in builder.graph.items() if k in affected_functions}
    return filtered_graph

def main():
    # Get staged diff
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True
    )

    staged_files = get_staged_python_files()
    total_graph = {}

    for f in staged_files:
        changed_funcs = get_changed_functions(f)
        print(changed_funcs)
        if not changed_funcs:
            continue
        graph = build_call_graph_for_changed_functions(f, changed_funcs)
        total_graph[f] = graph

    for f, g in total_graph.items():
        print(f"File: {f}")
        for func, calls in g.items():
            print(f"  {func} -> {calls}")

    # graph = build_graph_for_staged_files()
    # print("Function call graph:")
    # for k, v in graph.items():
    #     print(f"{k} -> {v}")
    
    # changed_functions = list(graph.keys())  # or detect functions in the diff
    # all_related = traverse_graph(graph, changed_functions)
    # print("All affected functions:", all_related)

    # # load_dotenv() 
    # # client = Anthropic()
    
    # # response = client.messages.create(
    # #     model="claude-sonnet-4-5",  
    # #     max_tokens=100,  # Maximum response length
    # #     messages=[
    # #         {
    # #         "role": "user", # Specifies the message is coming from the user (the role is "assistant" for responses from the LLMs) 
    # #         "content": "Do nothing and just repeat " + diff}
    # #     ]
    # # )

    # # print("===== GIT DIFF START =====")
    # # print(response.content)
    # # print("===== GIT DIFF END =====")

    # files = get_staged_files()
    # snippets = get_diff_for_functions(all_related, files)

    # for f, codes in snippets.items():
    #     print(f"File: {f}")
    #     for c in codes:
    #         print(c)
    #         print("-" * 40)

if __name__ == "__main__":
    main()
