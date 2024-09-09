from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient
import os, json
from dotenv import load_dotenv
import pandas as pd
import argparse
from typing import List, Dict , Union

def get_secret_from_keyvault(
    key_vault_url: str, 
    credential: Union[DefaultAzureCredential, ClientSecretCredential], 
    key: str
    ):
        secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
        secret = secret_client.get_secret(key)
        return secret.value




if __name__ == "__main__":
    
    ## if we have .env file, load the environment variables from the .env file
    load_dotenv()  

    COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]
    tenant_id = os.environ["TENANT_ID"]
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]

    # print(f"Key Vault Name: {key_vault_name}")

    ## If we are reading the environment details from the keyvault. We need to pass an keyvault name as the arguement
    ## If we want to do authentication using the service principal, we need to pass the client_id, client_secret and tenant_id int the arguments


    parser = argparse.ArgumentParser()

    ## uncomment below if we are calling the python using the arguments

    # parser.add_argument("--keyVaultName", type=str, help="The name of the key vault")
    # parser.add_argument("--clientId", type=str, nargs='?', const='', help="The client id of the service principal")
    # parser.add_argument("--clientSecret", type=str,  nargs='?', const='',  help="The client secret of the service principal")
    # parser.add_argument("--tenantId", type=str, nargs='?', const='',  help="The tenant id of the service principal")



    # args = parser.parse_args()

    #=======================================================================================================
    # Uncomment below if we are reading the environment variables from keyvault and using the service principal for authentication
    #========================================================================================================
    # try:
    #     key_vault_name = args.keyVaultName
    # except AttributeError as e:
    #     print(f"Missing key vault name in the arguments, trying to read from environment variable: {e}")
    #     key_vault_name = os.environ["KEY_VAULT_NAME"]

    # try:
    #     if args.clientId is None:
    #         client_id = ""
    #     else:
    #         client_id = args.clientId
    # except AttributeError as e:
    #     print(f"Missing clientId in the arguments, trying to read from environment variable: {e}")
    #     client_id = os.environ["CLIENT_ID"]
    
    # try:   
    #     if args.clientSecret is None:
    #         client_secret = ""
    #     else:
    #         client_secret = args.clientSecret
    # except AttributeError as e:
    #     print(f"Missing clientSecret in the arguments, trying to read from environment variable: {e}")
    #     client_secret = os.environ["CLIENT_SECRET"]

    # try:
    #     if args.tenantId is None:
    #         tenant_id = ""
    #     else:
    #         tenant_id = args.tenantId
    # except AttributeError as e:
    #     print(f"Missing tenantId in the arguments, trying to read from environment variable: {e}")
    #     tenant_id = os.environ["TENANT_ID"]

    # we will first check if the service principal details are present.
    if (client_id == "" or client_secret == "" or tenant_id == ""):
        print("Using the Default credentials")
        credential = DefaultAzureCredential()
        
    else:
        print("Using the Service Principal credentials")
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # read the config file where we have all the environment and configuration details

    # get the current working directory
    # print(f"Current working directory: {os.getcwd()}")
    with open(f"{os.getcwd()}/AzureSearch/config/config.json") as file:
        config = json.load(file)
    
    # key_vault_url = f"https://{key_vault_name}.vault.azure.net"
    # environment_details = config["key-vault-config"]["environment-details"]

    # try:
    #     COSMOS_ENDPOINT = get_secret_from_keyvault( key_vault_url, credential, environment_details["secret_COSMOS_ENDPOINT"])
        
    # except KeyError as e:
    #     print(f"Missing key vault secrets : {e}")
        
    DATABASE_NAME = config["cosmos-config"]["cosmos_db_name"]
    CONTAINER_NAME = config["cosmos-config"]["cosmos_db_container_name"]
    COSMOS_DB_PARTITION_KEY = config["cosmos-config"]["cosmos_db_partition_key"]

    # https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/samples/document_management.py#L149-L156

    # authentication using SPN
    client = CosmosClient(COSMOS_ENDPOINT, credential=credential)


    db = client.create_database_if_not_exists(id=DATABASE_NAME)
    # setup container for this sample
    container = db.create_container_if_not_exists(id=CONTAINER_NAME,
                                                    partition_key=PartitionKey(path=f'/{COSMOS_DB_PARTITION_KEY}', kind='Hash'))

    # read the products.csv file from (AzureSearch\data\products.csv), remove spaces and new lines from the column values


    # print(f"Current working directory: {os.getcwd()}")
    products_df = pd.read_csv(f"{os.getcwd()}/AzureSearch/Data/catalog1.csv")
    
    # convert the id column from int to string before uploading to Cosmos DB
    products_df = products_df.astype(str)

    products_df = products_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    # rename the column Id to id
    products_df.rename(columns={"Id":"id"}, inplace=True)

    products_dict = products_df.to_dict(orient="records")    


    print(f"Schema of the products_dict: {products_df.dtypes}")
    for product in products_dict:
        # convert product into Json
        # product = json.loads(json.dumps(product))
        container.upsert_item(body=product)
        print(f"Product {product['id']} uploaded to Cosmos DB")
    
