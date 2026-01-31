#!/usr/bin/env python3
from anthropic import Anthropic
from dotenv import load_dotenv 

from analyser import Analyser

load_dotenv() 


def main():
    staged_files = Analyser.get_staged_python_files()
    total_graph = {}

    for f in staged_files:
        changed_funcs = Analyser.get_changed_functions(f)
        if not changed_funcs:
            continue
        graph = Analyser.build_call_graph_for_changed_functions(f, changed_funcs)
        total_graph[f] = graph

    for f, g in total_graph.items():
        print(f"File: {f}")
        for func, calls in g.items():
            print(f"  {func} -> {calls}")
    print("\n\n\n")
    all_function_code = {}

    for file_path, graph in total_graph.items():
        changed_funcs = list(graph.keys())
        all_funcs = Analyser.traverse_graph_for_snippets(graph, changed_funcs)
        snippets = Analyser.get_function_snippets(file_path, all_funcs)
        all_function_code[file_path] = snippets

    # Example printout
    for f, funcs in all_function_code.items():
        print(f"File: {f}")
        for func_name, code in funcs.items():
            print(f"Function: {func_name}")
            print(code)
            print("-" * 40)

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

if __name__ == "__main__":
    main()
