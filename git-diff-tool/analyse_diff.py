#!/usr/bin/env python3
from dotenv import load_dotenv
from analyser import Analyser

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


load_dotenv()


def main():
    staged_files = Analyser.get_staged_python_files()
    total_graph = {}  # file -> call graph
    total_classes = {}  # file -> classes in file

    # Step 1: Build call graphs and collect class info
    for f in staged_files:
        changed_funcs = Analyser.get_changed_functions(f)
        if not changed_funcs:
            continue

        tree = Analyser.parse_file_to_ast(f)
        from call_graph_builder import CallGraphBuilder
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
        # Start traversal from changed functions
        changed_funcs = Analyser.get_changed_functions(file_path)
        reachable_funcs = Analyser.traverse_call_graph(graph, changed_funcs, max_depth=5)

        # Determine which classes are touched
        touched_classes = set()
        for func in reachable_funcs:
            # If the function belongs to a class, mark the class as touched
            tree = Analyser.parse_file_to_ast(file_path)
            from call_graph_builder import CallGraphBuilder
            builder = CallGraphBuilder()
            builder.visit(tree)
            cls = builder.function_to_class.get(func)
            if cls:
                touched_classes.add(cls)
            # Also, if a class is instantiated or method/property accessed in graph, include it
            for callee in graph.get(func, []):
                if callee in builder.classes:
                    touched_classes.add(callee)
                # also include left-most class parts if it's like Outer.Inner.method
                parts = callee.split(".")
                for i in range(1, len(parts)):
                    candidate_cls = ".".join(parts[:i])
                    if candidate_cls in builder.classes:
                        touched_classes.add(candidate_cls)

        # Step 3: Extract snippets
        class_snippets = Analyser.get_class_snippets(file_path, touched_classes)
        function_snippets = Analyser.get_function_snippets(file_path, reachable_funcs)

        # Merge results: class snippets take precedence
        merged_snippets = {**function_snippets, **class_snippets}
        all_function_code[file_path] = merged_snippets

    prompt_text = format_for_llm(all_function_code)

    print(prompt_text)


if __name__ == "__main__":
    main()
