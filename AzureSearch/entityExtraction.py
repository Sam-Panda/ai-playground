from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery

load_dotenv()

question = "Give me the tent related products"
# Question = "what is the top 3 highest price product in the category of 'hiking'?"

service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
tenant_id = os.environ["TENANT_ID"]
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
credential = ClientSecretCredential(tenant_id, client_id, client_secret)

with open("config/config.json") as file:
    config = json.load(file)
search_index_name = config["ai-search-config"]["search-index-config"]["name"]


# Pure Vector Search
search_client = SearchClient(endpoint=service_endpoint, index_name=search_index_name, credential=credential)
vector_query = VectorizableTextQuery(text=question, k_nearest_neighbors=3, fields="description_vectorized")
  
results = search_client.search(  
    search_text=None,  
    vector_queries= [vector_query],
    select=["price", "name", "brand", "category", "description"],
)  

print (" Question: ", question)  
for result in results:  
    print("Product: ", result["name"])
    print("Price: ", result["price"])
    print("Brand: ", result["brand"])
    print("Category: ", result["category"])
    print("Description: ", result["description"])



