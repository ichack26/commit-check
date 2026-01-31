#!/usr/bin/env python3

import subprocess

def main():
    # Get staged diff
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True
    )

    diff = result.stdout

    print("===== GIT DIFF START =====")
    print(diff)
    print("===== GIT DIFF END =====")

if __name__ == "__main__":
    main()
