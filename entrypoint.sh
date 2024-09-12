#!/bin/sh

# run the python script
echo "Running the python script"
echo "Uploading the data into CosmosDB"

python3 AzureSearch/uploadDatatoCosmosDB.py && python3 AzureSearch/createAzureSearchIndex.py


