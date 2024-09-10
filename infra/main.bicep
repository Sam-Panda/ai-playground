
targetScope = 'subscription'

param location string = 'westus'
@secure()
param spnObjectId string = 'a6b0fb66-4af8-416d-bc65-507704d09252'
// param spnObjectId string = '0632dc76-0224-455a-bea2-3efca1538c4e'

param addressPrefix string = '10.100.0.0/16'
param isPrivate bool = true
param tags object = {
  environment: 'dev'
}
var prefix = toLower(uniqueString(subscription().id, '-', location))
var cosmosDbDatabaseName = 'catalogDb'
var cosmosDbContainerName = 'products'
var cosmosDbPrivateEndpointName = '${prefix}-cosmosdb-pe'
var paritionKey = '/id'

var searchServiceName = '${prefix}-search'

// set the variable if isPrivate is true
var publicNetworkAccess = isPrivate ? 'disabled' : 'enabled'

//OpenAI realted config
var  openAiServiceName  =  '${prefix}-openai'
param useGPT4V bool = false
param openAiSkuName string = 'S0'

@allowed([ 'azure', 'openai', 'azure_custom' ])
param openAiHost string = 'azure' // Set in main.parameters.json
// param isAzureOpenAiHost bool = startsWith(openAiHost, 'azure')

param chatGptModelName string = ''
param chatGptDeploymentName string = ''
param chatGptDeploymentVersion string = ''
param chatGptDeploymentCapacity int = 0
var chatGpt = {
  modelName: !empty(chatGptModelName) ? chatGptModelName : startsWith(openAiHost, 'azure') ? 'gpt-35-turbo' : 'gpt-3.5-turbo'
  deploymentName: !empty(chatGptDeploymentName) ? chatGptDeploymentName : 'chat'
  deploymentVersion: !empty(chatGptDeploymentVersion) ? chatGptDeploymentVersion : '0613'
  deploymentCapacity: chatGptDeploymentCapacity != 0 ? chatGptDeploymentCapacity : 2
}

param embeddingModelName string = ''
param embeddingDeploymentName string = ''
param embeddingDeploymentVersion string = ''
param embeddingDeploymentCapacity int = 0
param embeddingDimensions int = 0
var embedding = {
  modelName: !empty(embeddingModelName) ? embeddingModelName : 'text-embedding-ada-002'
  deploymentName: !empty(embeddingDeploymentName) ? embeddingDeploymentName : 'embedding'
  deploymentVersion: !empty(embeddingDeploymentVersion) ? embeddingDeploymentVersion : '2'
  deploymentCapacity: embeddingDeploymentCapacity != 0 ? embeddingDeploymentCapacity : 2
  dimensions: embeddingDimensions != 0 ? embeddingDimensions : 1536
}

param gpt4vModelName string = 'gpt-4o'
param gpt4vDeploymentName string = 'gpt-4o'
param gpt4vModelVersion string = '2024-05-13'
param gpt4vDeploymentCapacity int = 10


//creating the resourcegroup

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name:  'rg-${prefix}-${location}'
  location: location
  tags: tags
}

// creating the vnet 
module vnet './modules/network/vnet.bicep'  = if (isPrivate) {
  scope: rg
  name: 'vnet'
  params: {
    prefix: prefix
    location: location
    tags: tags
    addressPrefix: addressPrefix
  }
}
// creating the cosmosdb 


module cosmos 'modules/cosmosDB/cosmosdb.bicep' = {
  scope: rg
  name: 'cosmos'
  params: {
    prefix: prefix
    location: location
    tags: tags
    partitionKey: paritionKey
    isPrivate: isPrivate
    vnet: vnet.outputs.vnet
    cosmosDbDatabaseName: cosmosDbDatabaseName
    cosmosDbContainerName: cosmosDbContainerName
    cosmosDbPrivateEndpointName: cosmosDbPrivateEndpointName
  }
}

// role creation for the cosmosdb and assignment to the service principal

// module  cosmosdbRoleCreationAndAssignment 'modules/cosmosDB/cosmosDbCustomRole.bicep' = {
//   scope: rg
//   name: 'cosmosdbRoleCreationAndAssignment'
//   params: {
//     accountName: cosmos.outputs.cosmosDbAccount.name
//     databaseAccount: cosmos.outputs.cosmosDbAccount
//     roleDefinitionName: 'CosmosDBSQLReadWriteRole'
//     dataActions: [
//       'Microsoft.DocumentDB/databaseAccounts/readMetadata'
//       'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/*'
//       'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/*'
//     ]
//     principalId: spnObjectId
//   }
// }

// creating the serach service

module searchService './modules/searchService/search.bicep' = {
  scope: rg
  name: 'searchService'
  params: {
    name: searchServiceName
    isPrivate: isPrivate
    prefix: prefix
    location: location
    tags: tags
    vnet: vnet.outputs.vnet
    publicNetworkAccess: publicNetworkAccess
    
  }
}

// OpenAI deployment

var defaultOpenAiDeployments = [
  // {
  //   name: chatGpt.deploymentName
  //   model: {
  //     format: 'OpenAI'
  //     name: chatGpt.modelName
  //     version: chatGpt.deploymentVersion
  //   }
  //   sku: {
  //     name: 'Standard'
  //     capacity: chatGpt.deploymentCapacity
  //   }
  // }
  {
    name: embedding.deploymentName
    model: {
      format: 'OpenAI'
      name: embedding.modelName
      version: embedding.deploymentVersion
    }
    sku: {
      name: 'Standard'
      capacity: embedding.deploymentCapacity
    }
  }
]

var openAiDeployments = concat(defaultOpenAiDeployments, useGPT4V ? [
    {
      name: gpt4vDeploymentName
      model: {
        format: 'OpenAI'
        name: gpt4vModelName
        version: gpt4vModelVersion
      }
      sku: {
        name: 'Standard'
        capacity: gpt4vDeploymentCapacity
      }
    }
  ] : [])

module openAi './modules/openAI/cognitiveservices.bicep' =  {
  name: 'openai'
  scope: rg
  params: {
    name: openAiServiceName
    location: location
    tags: tags
    publicNetworkAccess: publicNetworkAccess
    sku: {
      name: openAiSkuName
    }
    deployments: openAiDeployments
    disableLocalAuth: true
    isPrivate: isPrivate
    prefix: prefix
    vnet: vnet.outputs.vnet
  }

}

// provide search service endpoint access "Azure AI Developer" to the openai service

module openAiRoleUser './modules/security/role.bicep' =  {
  scope: rg
  name: 'openai-azure-ai-developer'
  params: {
    principalIds: [searchService.outputs.principalId]
    roleDefinitionId: '64702f94-c441-49e6-a78b-ef80e0188fee'
  }
  dependsOn: [
    openAi
  ]
}



// provide service principal access to serach service as "Search Service Contributor"
module searchServiceRoleContributor './modules/security/role.bicep' =  {
  scope: rg
  name: 'search-service-contributor'
  params: {
    principalIds: [spnObjectId]
    roleDefinitionId: '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
  }
  dependsOn: [
    searchService
  ]
}

// provide search service endpoint Cosmos DB Account Reader Role 

module cosmosDbAccountReaderRole './modules/security/role.bicep' =  {
  scope: rg
  name: 'cosmosdb-reader'
  params: {
    principalIds: [searchService.outputs.principalId]
    roleDefinitionId: 'fbdf93bf-df7d-467e-a4d2-9458aa1360c8'
  }
  dependsOn: [
    cosmos,searchService
  ]
}


