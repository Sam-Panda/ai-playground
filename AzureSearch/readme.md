# Creating Azure AI Search Index to scan the data from Azure Cosmos DB

## Objective
In this example, we will upload a sample data into cosmsos db and create an index in Azure AI Search to scan the data from cosmos db. While creating the Azure AI Search Index we will also create the other associated resources like Skillset, Indexer, Data Source, and Vectorizer.

## Prerequisites
1. You already have an Active Azure Subscription.
2. (Optional) You have already created a service principal to authenticate to the Microsoft Purview Environment. If you do not have the Azure Service Principal
3. You have a python virtual environment where the required modules are already installed (requirements.txt).
4. Please follow the steps to [setup the authentication](https://learn.microsoft.com/en-us/purview/tutorial-using-rest-apis).
5. In the Azure Purview environment, you have already registered the Azure SQL DB as a datasource.


## Upload Data to Cosmos DB