import json
import requests
import openai
from openai import AzureOpenAI
import os


# Initialize the Azure OpenAI client
client = AzureOpenAI(
  azure_endpoint = os.getenv("OPEN_AI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

# Define the deployment you want to use for your chat completions API calls

deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID")

def get_weather(location):
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + location  + "&appid=" + os.getenv("WEATHER_API_KEY")
    response=requests.get(url)
    get_response=response.json()
    latitude=get_response['coord']['lat']
    longitude = get_response['coord']['lon']
    print(f"latitude: {latitude}")
    print(f"longitude: {longitude}")

    url_final ="https://api.openweathermap.org/data/2.5/weather?lat="+ str(latitude) + "&lon=" + str(longitude) + "&appid=" + os.getenv("WEATHER_API_KEY")
    final_response = requests.get(url_final)
    final_response_json = final_response.json()
    print(final_response_json)
    weather=final_response_json['weather'][0]['description']
    print(f"weather condition: {weather}")

functions=[
    {
        "name":"getWeather",
        "description":"Retrieve real-time weather information/data about a particular location/place",
        "parameters":{
            "type":"object",
            "properties":{
                "location":{
                    "type":"string",
                    "description":"the exact location whose real-time weather is to be determined",
                },
                
            },
            "required":["location"]
        },
    }
] 

initial_response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "you are an assistant that helps people retrieve real-time weather data/info"},
        {"role": "user", "content": "How is the weather in kolkata?"}
    ],
    functions=functions
)

function_argument = json.loads(initial_response.choices[0].message.function_call.arguments)
location= function_argument['location']
if(location):
    print(f"city: {location}")
    get_weather(location)