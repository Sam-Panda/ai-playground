# Run an empty query (returns selected fields, all documents)
from azure.search.documents import SearchClient
from azure.identity import ClientSecretCredential
import os
from dotenv import load_dotenv

load_dotenv()

service_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
tenant_id = os.environ["TENANT_ID"]
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
credential = ClientSecretCredential(tenant_id, client_id, client_secret)

search_client = SearchClient(endpoint=service_endpoint,
                      index_name="contoso-product-index",
                      credential=credential)

results =  search_client.search(query_type='simple',
    search_text="shoe" ,
    select='Name,Description',
    include_total_count=True)

print ('Total Documents Matching Query:', results.get_count())

for result in results:
    print(result["@search.score"])
    print(result["Name"])
    print(f"Description: {result['Description']}")