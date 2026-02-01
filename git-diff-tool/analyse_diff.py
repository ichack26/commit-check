#!/usr/bin/env python3
from dotenv import load_dotenv
from anthropic import Anthropic

from analyser import Analyser
from call_graph_builder import CallGraphBuilder
import ast
import sys

in_code_block = False

def colorise_line(line: str) -> str:
    global in_code_block

    RESET  = "\033[0m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"

    stripped = line.strip().lower()

    # Toggle fenced code block
    if stripped.startswith("```"):
        in_code_block = not in_code_block
        return f"{YELLOW}{line}{RESET}"

    # Inside code block → yellow
    if in_code_block:
        return f"{YELLOW}{line}{RESET}"

    # Potential issue → red
    if stripped.startswith("- **potential issue:**") or stripped.startswith("potential issue:"):
        return f"{RED}{line}{RESET}"

    # Questions → green (header + bullets)
    if stripped.startswith("- **questions") or stripped.startswith("- ") or stripped.startswith("questions"):
        return f"{GREEN}{line}{RESET}"

    return line


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

            if not cls:
                # try to match by suffix if func is short
                for k, v in builder.function_to_class.items():
                    if k.endswith(func):
                        cls = v
                        break
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

    template_text = """You are an AI agent acting as a checker for git commit differences. You will be provided with the original code and the modified code. Do not provide follow up questions. You will not be responded to.

Your primary goal is:
Your task is to determine if the changes to the code will change the functionality of the code. If you discover that the code will be meaningfully changed by the commit, please specify what the new code has changed over the old code. If you believe that the code won't be meaningfully changed please just respond with “Looks all good :)”.

## Inputs
You will be provided with:
- The old code
- The new code

The code which you are provided with will be given in the following format.

==== {FILE_NAME} ====
{FUNCTION/CLASS}: {def / class} {name}
	{body}

The old code and the new code will be separated by the following delimiter.
====$NEW CODE$====



## Constraints
- {TIME / RESOURCE / FORMAT LIMITS}
- {TOOLS YOU MAY OR MAY NOT USE}
- {THINGS YOU MUST AVOID}

## Output Requirements
Your output must:
- If there were no physical changes made at all please out “Nothing to review”
- If you believe that the code won't be meaningfully changed please just respond with “Looks all good :)”. Do not output anything else.
- If you believe that the code will be meaningfully changed then please respond by saying what you believe will be changed along with the old and new code.

{NUMBER}. `{NAME}` in `{FILE_NAME}` ({function/class})
- **Old behaviour:** {…}

- **New behaviour:** {…}

-  **Potential issue:** {What changed and why it matters}

- **Questions to think about:**
  - {…}
  - {…}

Output format: terminal text
Do NOT include ANSI escape codes in your output.
Use plain text only.
Rules:
- Use triple backticks for code blocks
- No explanations
- Reset styles after every line
    """

    prompt_text = template_text + "\n\n" + old_text + "\n\n====$NEW CODE$====\n\n" + new_text

    load_dotenv()

    client = Anthropic()

    buffer = ""

    with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": prompt_text
        }
        ]
    ) as stream:

        for event in stream:
            if event.type == "content_block_delta":
                buffer += event.delta.text

                # Flush complete lines only
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    print(colorise_line(line), flush=True)

        # Flush remaining partial line
        if buffer.strip():
            print(colorise_line(buffer), flush=True)

if __name__ == "__main__":
    main()
