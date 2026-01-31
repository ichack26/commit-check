#!/usr/bin/env python3
from dotenv import load_dotenv
from anthropic import Anthropic

from analyser import Analyser
from call_graph_builder import CallGraphBuilder
import ast

def get_all_function_code(files, source="STAGED"):
    """
    Collect all reachable functions and classes for the given files.

    source:
        "STAGED" → use the staged file content
        "HEAD" → use the version from git HEAD
    """
    total_graph = {}  # file -> call graph
    total_classes = {}  # file -> classes in file

    # Step 1: Build call graphs and collect class info
    for f in files:
        if source == "HEAD":
            content = Analyser.get_file_at_head(f)
            tree = ast.parse(content, filename=f)
        else:
            tree = Analyser.parse_file_to_ast(f)

        builder = CallGraphBuilder()
        builder.visit(tree)

        # Save call graph
        graph = builder.graph
        total_graph[f] = graph

        # Save class info
        total_classes[f] = builder.classes

    # Step 2: Traverse call graphs to find all reachable functions and touched classes
    all_function_code = {}

    for file_path, graph in total_graph.items():
        # Determine changed functions (use the same line numbers, but old file)
        changed_funcs = Analyser.get_changed_functions(file_path)  # same lines as new diff
        if source == "HEAD":
            # get AST from HEAD version
            content = Analyser.get_file_at_head(file_path)
            tree = ast.parse(content, filename=file_path)
            builder = CallGraphBuilder()
            builder.visit(tree)
            graph = builder.graph
        else:
            # use staged/new file
            tree = Analyser.parse_file_to_ast(file_path)
            builder = CallGraphBuilder()
            builder.visit(tree)
            graph = builder.graph

        # traverse the call graph starting from the changed functions
        reachable_funcs = Analyser.traverse_call_graph(graph, changed_funcs, max_depth=5)

        # Step 2a: Determine which classes are touched
        touched_classes = set()
        # Revisit AST to map functions → classes
        tree = Analyser.parse_file_to_ast(file_path) if source != "HEAD" else ast.parse(Analyser.get_file_at_head(file_path))
        builder = CallGraphBuilder()
        builder.visit(tree)

        for func in reachable_funcs:
            cls = builder.function_to_class.get(func)
            if cls:
                touched_classes.add(cls)

            # Also include classes that are instantiated or accessed in graph
            for callee in graph.get(func, []):
                if callee in builder.classes:
                    touched_classes.add(callee)
                # Include left-most parts for nested classes: Outer.Inner.method
                parts = callee.split(".")
                for i in range(1, len(parts)):
                    candidate_cls = ".".join(parts[:i])
                    if candidate_cls in builder.classes:
                        touched_classes.add(candidate_cls)

        # Step 3: Extract snippets
        # Read file content depending on source
        if source == "HEAD":
            code_lines = Analyser.get_file_at_head(file_path).splitlines(keepends=True)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                code_lines = f.readlines()

        # Extract class snippets
        class_snippets = Analyser.get_class_snippets(code_lines, touched_classes)

        # Extract functions not inside touched classes
        function_snippets = {
            fn: code
            for fn, code in Analyser.get_function_snippets(code_lines, reachable_funcs).items()
            if builder.function_to_class.get(fn) not in touched_classes
        }

        # Merge results: class snippets take precedence
        merged_snippets = {**function_snippets, **class_snippets}
        all_function_code[file_path] = merged_snippets

    return all_function_code

def format_for_llm(all_function_code):
    lines = []
    for file_path, snippets in all_function_code.items():
        lines.append(f"===== FILE: {file_path} =====")
        for name, code in snippets.items():
            kind = "CLASS" if "class " in code.splitlines()[0] else "FUNCTION"
            lines.append(f"{kind}: {name}")
            lines.append(code)
            lines.append("")  # spacing between snippets
    return "\n".join(lines)

def main():
    staged_files = Analyser.get_staged_python_files()

    # Old code (HEAD)
    old_code = get_all_function_code(staged_files, source="HEAD")

    # New code (STAGED)
    new_code = get_all_function_code(staged_files, source="STAGED")

    # Format both for LLM
    old_text = format_for_llm(old_code)
    new_text = format_for_llm(new_code)

    # function_info_text = format_for_llm(all_function_code)

    # template_text = """Review this python code for:
    # - bugs and logical errors
    # - performance issues
    # - security vulnerabilities
    # - code style and best practices

    # """

    # prompt_text = template_text + function_info_text

    # load_dotenv()

    # client = Anthropic()

    # response = client.messages.create(
    # model="claude-sonnet-4-5",  
    # max_tokens=1000,  # Maximum response length
    # messages=[
    #     {
    #     "role": "user", # Specifies the message is coming from the user (the role is "assistant" for responses from the LLMs) 
    #     "content": prompt_text}
    # ]
    # )

    # print("\n\n".join([text_block.text for text_block in response.content]))


if __name__ == "__main__":
    main()
