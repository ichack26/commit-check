# Diffence

Spot unintended code behaviour instantly and reliably. 

## Inspiration

With the rise of vibe-coding less developer time is spent writing new code and more is spent debugging and adapting code. We wanted to streamline the development process by helping developers understand what they have written and prevent unintended behaviour with a minimal and intuitive tool.

## What it does

Diffence is a lightweight pre‑commit git hook that uses AI to review changes in your codebase, without the overhead of inputting your entire repository. By analyzing only the git diff (the code you're actually changing), Diffence uses an intelligent AI agent to identify how the function changes, highlighting any potentially unintended behaviour.

## Why not use ChatGPT/Claude/Cursor?
Whilst direct LLM usage requires careful prompting for a concise response, Diffence provides a zero click solution by automatically running on `git commit`.

Providing an LLM with an entire repository can fill its context window, degrading the accuracy and speed of responses. However, manually searching through the code base for relevant functions can be time-consuming. Diffence automatically sends required information to AI models, only processing what is necessary to understand a change.

## How we built it

To make Diffence as simple as possible to integrate into workflows, we decided to make it into a Git hook. By creating a Git hook, Diffence is called by Git whenever the developer runs `git commit`. Diffence runs in pre-commit, allowing the developer to change their code if necessary before committing.

By outputting through the command line, Diffence is both non-intrusive and compatible with every development environment.

Diffence uses an abstract syntax trees (AST) to analyse a repository and the code snippet contained in a Git diff (the code to be committed). Referenced functions can be found by traversing the AST with a depth first search, producing a list of functions and definitions to be fed to the LLM. We then created an AI agent with Claude to provide a concise analysis of what has changed, highlighting potential unintentional behaviour. 

## Challenges we ran into

We knew we wanted to make a quality of life tool for developers but struggled to identify what professionals actually wanted, having limited professional experience ourselves. To get to the root of the problems developers face, we decided to directly consult with industry professionals present at ICHack.

Additionally, we initially only included the code snippet from the Git diff in our prompt to Claude. We found that information we provided in the Git diff was insufficient context for the LLM to understand exactly what each function did and how they worked. To solve this, we implemented the method for traversing a codebase described above.

## Accomplishments that we're proud of

We're proud of making a tool which we would use ourselves.

## What we learned

We learned that the complexity of a solution is not proportional to the efficacy of the solution, the only way to solve a problem it to find its root cause.

## What's next for Diffence

In future, Diffence could be improved by adding further support for more languages, taking into account language specific features when constructing the abstract syntax trees as well as including better library support. 
