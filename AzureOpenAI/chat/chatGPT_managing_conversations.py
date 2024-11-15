import os
from openai import AzureOpenAI

client = AzureOpenAI(
  azure_endpoint = os.getenv("OPEN_AI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

response = client.chat.completions.create(
    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID"), # model = "deployment_name".
    messages=[
        {"role": "system", "content":'''You are a helpful assistant. 
         Instructions: 
          - Answer the user's questions about Azure OpenAI and Azure AI services.
          - If you're unsure of an answer, you can say "I don't know" or "I'm not sure" and recommend users go to the IRS website for more information.'''},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "what was the cricket score in the last world cup final?"}
    ]
)

print(response.choices[0].message.content)