import os
from openai import AzureOpenAI

client = AzureOpenAI(
  azure_endpoint = os.getenv("OPEN_AI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

# Input text to summarize
input_text = """
Electric vehicles (EVs) have long been hailed as the future of transportation, offering a cleaner and more sustainable alternative to traditional gasoline-powered cars. However, their widespread adoption has been hindered by the limitations of current battery technology, including issues related to energy density, charging time, and lifespan. In recent years, a remarkable scientific breakthrough has emerged, promising to revolutionize the EV industry and accelerate the transition to a greener and more efficient mode of transportation. This breakthrough centers around the development of quantum batteries.

The Quantum Leap

Quantum batteries are a new frontier in energy storage, leveraging the principles of quantum mechanics to overcome the limitations of conventional lithium-ion batteries. This breakthrough is the result of collaborative efforts from researchers and scientists worldwide, and it holds the potential to reshape the entire automotive industry and beyond.

Superior Energy Density: One of the most significant advantages of quantum batteries is their exceptional energy density. Traditional lithium-ion batteries are limited by the physical properties of their materials, which restrict the amount of energy they can store. Quantum batteries, on the other hand, use quantum dots and other nanoscale structures to increase energy density significantly. This translates to longer driving ranges for EVs, reducing the need for frequent recharging and making long-distance travel more accessible.

Ultra-Fast Charging: Quantum batteries are designed to charge at unprecedented speeds. Traditional EVs can take anywhere from 30 minutes to several hours to recharge fully, depending on the charger's power and battery capacity. Quantum batteries, however, can be charged in a matter of minutes, making EVs as convenient as refueling a gasoline car. This not only enhances the practicality of EVs but also reduces the strain on the electric grid.

Extended Lifespan: Quantum batteries are engineered to be more durable than their lithium-ion counterparts. They exhibit minimal degradation over time, resulting in a significantly longer lifespan. This not only reduces the frequency of battery replacements but also lowers the overall environmental impact of manufacturing and disposing of batteries.

Safety Improvements: Quantum batteries are inherently safer than traditional lithium-ion batteries. The risk of thermal runaway, a common concern with lithium-ion batteries, is greatly reduced due to their unique chemical composition and design. This enhances the overall safety of EVs and alleviates concerns regarding fire hazards.

Sustainability: Quantum batteries are also more sustainable in terms of resource usage. While lithium-ion batteries require the extraction of rare earth materials, quantum batteries utilize more abundant and environmentally friendly materials, reducing the ecological footprint of battery production.
"""

# Prepare the prompt for summarize (try different instructions on the summary length)
prompt = f"""
You will be provided with an input text delimited by ### and your task will be to summarize it into a form of tweet and should not exceed 180 words.

Input text: 
###
{input_text}
###
"""

summary = client.chat.completions.create(
    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID"), # model = "deployment_name".
    messages=[
        {"role": "system", "content": prompt}
    ]
)

summary_text = summary.choices[0].message.content
print(summary_text)

print("Length of input text: " + str(len(input_text)))
print("Length of summary: " + str(len(summary_text)))