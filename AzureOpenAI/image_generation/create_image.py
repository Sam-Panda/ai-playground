import json
import os
import openai
import requests

# Setting up the deployment name
image_deployment_name = os.environ['AZURE_OPENAI_IMAGE_DEPLOYMENT_ID']
# The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
# This is the value of the endpoint for your Azure OpenAI resource
azure_endpoint = os.environ['OPEN_AI_ENDPOINT']
# The API key for your Azure OpenAI resource.
api_key = os.environ['AZURE_OPENAI_API_KEY']
# Currently OPENAI API have the following versions available: https://learn.microsoft.com/azure/ai-services/openai/reference
api_version = os.environ['AZURE_OPENAI_VERSION']
client = openai.AzureOpenAI(
  api_key=api_key,  
  azure_endpoint=azure_endpoint,
  api_version=api_version
)

library_response=client.images.generate(
    prompt='''A mom is concerned about her child’s nutrition and wants to make sure they’re eating well. 
    She wonders what new meals she could prepare to encourage a healthy appetite and 
    provide balanced nourishment. She thinks about cooking…''',
    size="1024x1024",
    n=1,
    model=image_deployment_name
)

image_url = library_response.data[0].url
print(image_url)