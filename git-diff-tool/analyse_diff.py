#!/usr/bin/env python3
from anthropic import Anthropic
from dotenv import load_dotenv 

import subprocess

load_dotenv() 

import subprocess

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

def main():
    # Get staged diff
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True
    )

    graph = build_graph_for_staged_files()
    print("Function call graph:")
    for k, v in graph.items():
        print(f"{k} -> {v}")
    
    changed_functions = list(graph.keys())  # or detect functions in the diff
    all_related = traverse_graph(graph, changed_functions)
    print("All affected functions:", all_related)

    # load_dotenv() 
    # client = Anthropic()
    
    # response = client.messages.create(
    #     model="claude-sonnet-4-5",  
    #     max_tokens=100,  # Maximum response length
    #     messages=[
    #         {
    #         "role": "user", # Specifies the message is coming from the user (the role is "assistant" for responses from the LLMs) 
    #         "content": "Do nothing and just repeat " + diff}
    #     ]
    # )

    # print("===== GIT DIFF START =====")
    # print(response.content)
    # print("===== GIT DIFF END =====")

    files = get_staged_files()
    snippets = get_diff_for_functions(all_related, files)

    for f, codes in snippets.items():
        print(f"File: {f}")
        for c in codes:
            print(c)
            print("-" * 40)

if __name__ == "__main__":
    main()
