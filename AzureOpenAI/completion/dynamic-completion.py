# import os module & the OpenAI Python library for calling the OpenAI API
# please make sure you have installed required libraries via pip install -r requirements.txt
import os
import dotenv
import openai
from sentence_transformers import SentenceTransformer, util
import numpy as np
from datasets import load_dataset
from sklearn.metrics import classification_report
from torch import cuda
device = 'cuda' if cuda.is_available() else 'cpu'
dotenv.load_dotenv()

dataset = load_dataset("trec", trust_remote_code=True)

label_type = "coarse_label"
text_key = "text"
# create mapping of ids2class and class2id
id2class = dict((i, label) for i, label in enumerate(dataset['train'].features[label_type].names))
class2id = dict((label, i) for i, label in enumerate(dataset['train'].features[label_type].names))
# create a dictionary with classes as key and containing all the training examples within that class
class2TrainDataset = dict((label, []) for label in dataset['train'].features[label_type].names)
for example in dataset['train']:
    label = id2class[example[label_type]]
    class2TrainDataset[label].append(example[text_key])

# a prompt for asking LLM to perform a task
task_prompt = "As a Question Answering agent, your goal is to categorize questions into different semantic classes that impose constraints on potential answers, so that they can be utilized in later stages of the question answering process.\nFollowing are the semantic classes: ["
task_prompt += ", ".join([label for label in class2TrainDataset]) + "]"
# a prompt for asking LLM to generate the output for current task
query_prompt = "\nClassify the following question into one of the above classes. Please answer in a single word.\nquestion: "
answer_prompt = "\noutput: "

# Setting up the deployment name
deployment_name = os.environ['AZURE_OPENAI_DEPLOYMENT_ID']

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

# Text completion using GPT
def trim_text(text):
    return text.strip().strip('\n').strip('\\n')

def generate_using_gpt(prompt, test_key):
    generated_sentence = ""
    try:
        # Create a completion for the provided prompt and parameters
        # To know more about the parameters, checkout this documentation: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference
        response = client.chat.completions.create(
            model=deployment_name,
            messages=prompt, 
            max_tokens=3,
            temperature=0,
            top_p=1,
            stop=None,
            frequency_penalty=0,
            presence_penalty=0.0)
        
        choices = response.choices
        if len(choices) == 0 or not hasattr(choices[0], "message"):
            print("Text not generated properly")
        generated_sentence = response.choices[0].message.content.lstrip('\\n').rstrip('\\n').lstrip('\n\n').rstrip('\n\n').lstrip('\n').rstrip('\n')
        print(f"Test Sentence: {test_key}")
        print(f"Generated Sentence: {generated_sentence}")  


    except openai.APITimeoutError as e:
        # Handle request timeout
        print(f"Request timed out: {e}")
    
    except openai.AuthenticationError as e:
        # Handle Authentication error here, e.g. invalid API key
        print(f"OpenAI API returned an Authentication Error: {e}")

    except openai.APIConnectionError as e:
        # Handle connection error here
        print(f"Failed to connect to OpenAI API: {e}")

    except openai.BadRequestError as e:
        # Handle connection error here
        print(f"Invalid Request Error: {e}")
        
    except openai.RateLimitError as e:
        # Handle rate limit error
        print(f"OpenAI API request exceeded rate limit: {e}")

    except openai.InternalServerError as e:
        # Handle Service Unavailable error
        print(f"Service Unavailable: {e}")

    except openai.APIError as e:
        # Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")

    return generated_sentence

zeroshot_prompt = task_prompt +  query_prompt + dataset['test'][0][text_key] + answer_prompt
print(zeroshot_prompt)

# prompt without any examples from the training dataset
labels = []
predictions = []
for example in dataset['test']:
    zeroshot_prompt = task_prompt +  query_prompt + example[text_key] + answer_prompt
    messages = [
        {"role": "system", "content": zeroshot_prompt}
    ]
                   
    pred = generate_using_gpt(messages, example[text_key] )
    pred=trim_text(pred)
    labels.append(example[label_type])
    if pred not in class2id:
        predictions.append(-1)
    else:
        predictions.append(class2id[pred])
        
report = classification_report(labels, predictions) 
print (report)

# Few shot prompt

# function to selection few examples in each of the classes from the training dataset
def generateFewshotPrompt(class2TrainDataset, N=3):
    fewshot_prompt = "\nFollowing are some examples."
    for label in class2TrainDataset:
        for example in class2TrainDataset[label][:N]:
            fewshot_prompt += "\nquestion: " + example
            fewshot_prompt += "\noutput: " + label
    return fewshot_prompt

fewshot_examples = generateFewshotPrompt(class2TrainDataset, N=1)
fewshot_prompt = task_prompt +  fewshot_examples + query_prompt + dataset['test'][0][text_key] + answer_prompt
print(fewshot_prompt)


labels = []
predictions = []
for example in dataset['test']:
    fewshot_prompt = task_prompt + fewshot_examples + query_prompt + example[text_key] + answer_prompt
    messages = [
        {"role": "system", "content": fewshot_prompt}
    ]
    pred = generate_using_gpt(messages, example[text_key])
    pred=trim_text(pred)
    labels.append(example[label_type])
    if pred not in class2id:
        predictions.append(-1)
    else:
        predictions.append(class2id[pred])
        
report = classification_report(labels, predictions) 