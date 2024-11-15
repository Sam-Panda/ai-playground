import tiktoken
import os
from openai import AzureOpenAI
import json

client = AzureOpenAI(
  azure_endpoint = os.getenv("OPEN_AI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

chat_messages = []

def process_chat_request(prompt):
    """Make a request to the OpenAI API"""
    chat_messages.append({"role": "user","content": prompt})
    
    response = client.chat.completions.create(
    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID"), # model = "deployment_name".
    messages = chat_messages,
    temperature=0.7
    )
    # Append the response to messages
    chat_messages.append({"role": "assistant","content": response.choices[0].message.content})
     
    print(json.dumps(chat_messages, indent=2))
    # Extract the generated labels from the API response
    return response.choices[0].message.content


    
print("Hello and welcome to the Good Advice Chatbot! How can I help you?")
system_message = "You are a helpful assistant that speaks like a pirate"
chat_messages = [{"role": "system", "content": system_message}]

while True:  
    print("------------------------\nUser: ")
    user_prompt = input()
    response = process_chat_request(user_prompt)
    print("Chatbot: " + response)
    
    if user_prompt.lower() in ["bye", "exit", "quit"]:
            break