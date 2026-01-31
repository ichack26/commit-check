#!/usr/bin/env python3
from anthropic import Anthropic
from dotenv import load_dotenv 

import subprocess

def main():
    # Get staged diff
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True
    )

    diff = result.stdout

    load_dotenv() 
    client = Anthropic()
    
    response = client.messages.create(
        model="claude-sonnet-4-5",  
        max_tokens=100,  # Maximum response length
        messages=[
            {
            "role": "user", # Specifies the message is coming from the user (the role is "assistant" for responses from the LLMs) 
            "content": "Do nothing and just repeat " + diff}
        ]
    )

    print("===== GIT DIFF START =====")
    print(response.content)
    print("===== GIT DIFF END =====")

if __name__ == "__main__":
    main()
