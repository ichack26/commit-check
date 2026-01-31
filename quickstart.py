from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  

# Initialise client - automatically reads ANTHROPIC_API_KEY from environment
client = Anthropic()  # or pass api_key="your-key-here" explicitly

# Send a prompt and get a response
response = client.messages.create(
    model="claude-sonnet-4-5",  
    max_tokens=100,  # Maximum response length
    messages=[
        {
        "role": "user", # Specifies the message is coming from the user (the role is "assistant" for responses from the LLMs) 
        "content": "What should I search for to find the latest developments in renewable energy?"}
    ]
)

# Extract and print the response
print(response.content) # This will be a TextBox