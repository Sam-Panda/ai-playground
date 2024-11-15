import os
from openai import AzureOpenAI

import tiktoken

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version = "2024-02-01",
  azure_endpoint = os.getenv("OPEN_AI_ENDPOINT")  # Your Azure OpenAI resource's endpoint value.
)

conversation=[{"role": "system", "content": "You are a helpful assistant."}]
conversation_content = ""
    
while True:
    user_input = input("Q:")  
    if(user_input.lower == "exit"):
        break

    conversation.append({"role": "user", "content": user_input})
    # add the content of the user_input to the conversation
    for c in conversation:
        conversation_content += c["content"] + " "

    print("Tokens: " + str(num_tokens_from_string(conversation_content, "o200k_base")))
    print( "\n" + "Conversation: " + str(conversation)+ "\n" )
    response = client.chat.completions.create(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID"), # model = "deployment_name".
        messages=conversation
    )

    conversation.append({"role": "assistant", "content": response.choices[0].message.content})
    print("\n" + response.choices[0].message.content + "\n")