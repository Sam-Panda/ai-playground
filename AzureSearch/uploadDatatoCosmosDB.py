from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.identity import DefaultAzureCredential, ClientSecretCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
import os, json
from dotenv import load_dotenv
import pandas as pd
import argparse
from typing import List, Dict , Union
import sys

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
    MI_CLIENT_ID = os.environ["MI_CLIENT_ID"]

    # print the values of the environment variables
    print(f"COSMOS_ENDPOINT: {COSMOS_ENDPOINT}")
    print(f"tenant_id: {tenant_id}")
    print(f"client_id: {client_id}")
    # print(f"client_secret: {client_secret}")
    print(f"MI_CLIENT_ID: {MI_CLIENT_ID}")
    

    '''

    (Optional) If we are reading the environment details from the keyvault. We need to pass an keyvault name as the arguement
    (Optional) If we want to do authentication using the service principal, we need to pass the client_id, client_secret and tenant_id in the arguments


    ## uncomment below if we are calling the python using the arguments
    parser = argparse.ArgumentParser()  
    parser.add_argument("--keyVaultName", type=str, help="The name of the key vault")
    parser.add_argument("--clientId", type=str, nargs='?', const='', help="The client id of the service principal")
    parser.add_argument("--clientSecret", type=str,  nargs='?', const='',  help="The client secret of the service principal")
    parser.add_argument("--tenantId", type=str, nargs='?', const='',  help="The tenant id of the service principal")
    args = parser.parse_args()
    '''
    #=======================================================================================================
    # Uncomment below if we are reading the environment details from keyvault and using the service principal for authentication
    #========================================================================================================
    '''
    try:
        key_vault_name = args.keyVaultName
    except AttributeError as e:
        print(f"Missing key vault name in the arguments, trying to read from environment variable: {e}")
        key_vault_name = os.environ["KEY_VAULT_NAME"]

    try:
        if args.clientId is None:
            client_id = ""
        else:
            client_id = args.clientId
    except AttributeError as e:
        print(f"Missing clientId in the arguments, trying to read from environment variable: {e}")
        client_id = os.environ["CLIENT_ID"]
    
    try:   
        if args.clientSecret is None:
            client_secret = ""
        else:
            client_secret = args.clientSecret
    except AttributeError as e:
        print(f"Missing clientSecret in the arguments, trying to read from environment variable: {e}")
        client_secret = os.environ["CLIENT_SECRET"]

    try:
        if args.tenantId is None:
            tenant_id = ""
        else:
            tenant_id = args.tenantId
    except AttributeError as e:
        print(f"Missing tenantId in the arguments, trying to read from environment variable: {e}")
        tenant_id = os.environ["TENANT_ID"]
    '''
    # we will first check if the service principal details are present.
    
    if (MI_CLIENT_ID != ""):
        print("Using the Managed Identity credentials")
        credential = ManagedIdentityCredential(client_id=MI_CLIENT_ID)

    elif (client_id == "" or client_secret == "" or tenant_id == ""):
        print("Using the Default credentials")
        credential = DefaultAzureCredential()
        
    else:
        print("Using the Service Principal credentials")
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # read the config file where we have all the environment and configuration details

    # get the current working directory
    # print(f"Current working directory: {os.getcwd()}")
    with open(f"{os.getcwd()}/config/config.json") as file:
        config = json.load(file)
    
    #=======================================================================================================
    # Uncomment below if we are reading the environment details from keyvault and using the service principal for authentication
    #========================================================================================================
    '''
    key_vault_url = f"https://{key_vault_name}.vault.azure.net"
    environment_details = config["key-vault-config"]["environment-details"]

    try:
        COSMOS_ENDPOINT = get_secret_from_keyvault( key_vault_url, credential, environment_details["secret_COSMOS_ENDPOINT"])
        
    except KeyError as e:
        print(f"Missing key vault secrets : {e}")
    '''
        
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

    # read the catalog1.csv file from (AzureSearch\data\products.csv), remove spaces and new lines from the column values

    products_df = pd.read_csv(f"{os.getcwd()}/Data/catalog1.csv")
    
    # convert the id column from int to string before uploading to Cosmos DB
    products_df = products_df.astype(str)
    products_df = products_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    products_df.rename(columns={"Id":"id"}, inplace=True)
    products_dict = products_df.to_dict(orient="records")    


    for product in products_dict:
        try:
            print(f"Inserting product ID: {product['id']} to Cosmos DB")
            container.upsert_item(body=product)
            print(f"Product {product['id']} uploaded to Cosmos DB")
        except exceptions.CosmosHttpResponseError as error:
            print(f"Exception inserting product {product['id']} into database. {error}")
            sys.exit(1)

