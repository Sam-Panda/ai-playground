import os 
import json
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from dotenv import load_dotenv

if __name__ == "__main__":
        
    load_dotenv()
    key_vault_name  = ""
    key_vault_url = f"https://{key_vault_name}.vault.azure.net"
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
    ## read the .env file line by line and extract out the key value pairs. .env file is in the root directory

    ## change the execution directory to the parent directory
    # os.chdir(os.path.dirname(os.getcwd())) 
    # print(os.getcwd())

    with open('.env', 'r') as file:
        lines = file.readlines()
        for line in lines:
            try:
                key, value = line.split('=')
                # remove the spaces
                key = key.strip()
                value = value.strip()
                # replace "_" with "-" for the key
                key = key.replace("_", "-")
                #remove " from the value 
                value = value.replace('"', '')
                secret = secret_client.set_secret(key, value)
            except Exception as e:
                print(e)
                print(f"Error in setting the secret {key} in the key vault")

    