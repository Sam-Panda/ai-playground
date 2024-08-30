#!/bin/sh

# run the python script
echo "Running the python script"
echo "Uploading the data into CosmosDB"

python3 AzureSearch/uploadDatatoCosmosDB.py

echo "Creating the Azure Search Index"
python3 AzureSearch/createAzureSearchIndex.py
