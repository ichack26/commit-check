~~I'll help you create a strong Devpost structure for Diffense based on the hackpack guidelines and your project materials.~~

# Diffense

Spot unintended side effects instantly and reliably. 

## Inspiration

If you've ever had the issue of making a change which you thought full well would make the codebase better and thought, god if only there was a ~~vibecoded~~tool that could help me analyse my slop, then i suppose this would be a useful project for you. 

## What it does

Diffense is a git hook that snipes commits to help developers actually use their brain about their changes before they become pull requests. By analyzing only the git diff (the code you're actually changing), Diffense uses ~~Claude~~ an intelligent AI agent to identiy the function changes. 

## How we built it

I think one of the coolest things about it is that we needed to figure out how to give all the necessary information, and only the necessary information, to optimize our call to the agent, and we found out getting information about a codebase is actually quite hard. We decided to use a graph to store information about all nested functions, so we'd only explore functions that were called in the new changed piece of code, which was quite neat. 

## Challenges we ran into

The major challenge was trying to make sure the output wasn't bloated, otherwise it completely defeats the purpose. This was solved by extensive ~~prompt engineering~~ tuning of the AI to meet our vision. Visionaries I say. 

## Achievments and learning

We're proud of actually fully building a tool that works. A viable small MVP is actually really nice to test and play around with. I think the takeaway is to ensure you REALLY understand the problem you're trying to solve, before coding it, as it ultimately led us to making something that was, actually something we'd use ourselves as developers. 

## What's next for Diffense

Building on our reference traversal foundation, we'd also like to explore detecting security vulnerabilities and suggesting refactoring opportunities at commit time. Understandably though, there's the small issue of trynig to use a non-deterministic AI agent to make conclusive confidence deterministic statements about security. We'll think about that later though. 

## Built With
- Snakes
- Command Line Interface Tools (CLI Tools)
- Caffeine
- More Caffeie
- A little bit more Caffeine
- Vibes
- Coding

**Demo Video:** [Link to 2-3 minute video showing Diffense catching a real side effect]

i really hope the other judges don't see this, I hope this is only seen for whimsy otherwise embarassinggggg. 
