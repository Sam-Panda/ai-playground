from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
import os, json
from dotenv import load_dotenv
import pandas as pd

load_dotenv()



def get_credential_local_machine():
    try:
        credential = DefaultAzureCredential()
        # Check if given credential can get token successfully.
        credential.get_token("https://management.azure.com/.default")
    except Exception as ex:
        # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential not work
        # This will open a browser page for
        credential = InteractiveBrowserCredential()
    return credential

def get_credential_SPN(
        client_id: str,
        client_secret: str,
        tenant_id: str
):
    from azure.identity import ClientSecretCredential
    return ClientSecretCredential(tenant_id, client_id, client_secret)



# read the config.json file from (AzureSearch\config\config.json)


with open("config/config.json") as file:
    config = json.load(file)



# Set the Cosmos DB endpoint, key and database name in the .env file. The key and endpoint can be found in the resource created in the portal.
# and set the values in the .env file
# The .env file should be in the root directory of the project
# The .env file should not be uploaded to the repository
# The .env file should be added to the .gitignore file



COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]


DATABASE_NAME = config["cosmos-config"]["cosmos_db_name"]
CONTAINER_NAME = config["cosmos-config"]["cosmos_db_container_name"]
COSMOS_DB_PARTITION_KEY = config["cosmos-config"]["cosmos_db_partition_key"]

# for the service principal credential

TENANT_ID = os.environ["TENANT_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]



client = CosmosClient(COSMOS_ENDPOINT, credential=get_credential_SPN(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, tenant_id=TENANT_ID))


db = client.create_database_if_not_exists(id=DATABASE_NAME)
# setup container for this sample
container = db.create_container_if_not_exists(id=CONTAINER_NAME,
                                                partition_key=PartitionKey(path=f'/{COSMOS_DB_PARTITION_KEY}', kind='Hash'))

# read the products.csv file from (AzureSearch\data\products.csv), remove spaces and new lines from the column values
# convert the id column from int to string before uploading to Cosmos DB

products_df = pd.read_csv("data/products.csv")
products_df["id"] = products_df["id"].astype(str)
products_df = products_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
products_dict = products_df.to_dict(orient="records")

# get the schema and data types of the products_dict

for product in products_dict:
    container.upsert_item(body=product)
    print(f"Product {product['id']} uploaded to Cosmos DB")
