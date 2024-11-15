import os
from openai import AzureOpenAI

client = AzureOpenAI(
  azure_endpoint = os.getenv("OPEN_AI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

# feedback messages

feedback_messages =  [
    "I absolutely love the product! It's even better than I hoped for.",
    "The shipping took longer than expected, but the product arrived in perfect condition.",
    "I'm really pleased with my purchase. It's high-quality and exactly what I wanted.",
    "I had a horrible experience. The item I received looks nothing like the description.",
    "The customer support team went above and beyond to help me with my problem.",
    "The product is fantastic! It exceeded my expectations by a mile.",
    "The packaging was a bit damaged, but the product inside was flawless.",
    "I'm happy with my purchase. The quality is top-notch.",
    "I'm extremely disappointed. The product doesn't match what was advertised.",
    "Kudos to the customer service team for their prompt assistance in resolving my issue."
]

# Prepare the prompt for summarize (try different instructions on the summary length)
prompt = f"""
You will be provided with list of feedback messages and your task will be to classify them into positive, negative or neutral sentiment.

Feedbacks::: 
"""
for feedback in feedback_messages:
    prompt += f"""
    {feedback}
    """

classifications = client.chat.completions.create(
    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID"), # model = "deployment_name".
    messages=[
        {"role": "system", "content": prompt}
    ]
)

classification_text = classifications.choices[0].message.content
print(classification_text)

