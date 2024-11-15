import os
import openai
import dotenv

dotenv.load_dotenv()

endpoint = os.environ.get("OPEN_AI_ENDPOINT")
api_key = os.environ.get("AZURE_OPENAI_API_KEY")
deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID")

client = openai.AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-01",
)

completion = client.chat.completions.create(
    model=deployment,
    messages=[
        {
            "role": "user",
            "content": "Arctic Shield Insulated Jacket?",
        },
    ],
    extra_body={
        "data_sources":[
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": os.environ["AZURE_SEARCH_ENDPOINT"],
                    "index_name": os.environ["AZURE_AI_SEARCH_INDEX"],
                    "authentication": {
                        "type": "api_key",
                        "key": os.environ["AZURE_AI_SEARCH_API_KEY"],
                    }
                }
            }
        ],
    }
)

print(completion.model_dump_json(indent=2))