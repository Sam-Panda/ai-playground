metadata description = 'Creates an Azure AI Search instance.'
param name string
param isPrivate bool 
param prefix string
param location string = resourceGroup().location
param tags object = {}
param vnet object
@secure()
param comsosAccountResourceID string
@secure()
param openAIResourceID string



param sku object = {
  name: 'standard'
}

param authOptions object = {
  aadOrApiKey: {
    aadAuthFailureMode: 'http401WithBearerChallenge'
  }
}
param disableLocalAuth bool = true
param encryptionWithCmk object = {
  enforcement: 'Unspecified'
}
@allowed([
  'default'
  'highDensity'
])
param hostingMode string = 'default'
@allowed([
  'enabled'
  'disabled'
])
param publicNetworkAccess string = 'disabled'
param partitionCount int = 1
param replicaCount int = 1
@allowed([
  'disabled'
  'free'
  'standard'
])
param semanticSearch string = 'free'



var searchIdentityProvider = (sku.name == 'free') ? null : {
  type: 'SystemAssigned'
}

resource search 'Microsoft.Search/searchServices@2023-11-01'  = {
  name: name
  location: location
  tags: tags
  // The free tier does not support managed identity
  identity: searchIdentityProvider
  properties: {
    authOptions: disableLocalAuth ? null : authOptions
    disableLocalAuth: disableLocalAuth
    encryptionWithCmk: encryptionWithCmk
    hostingMode: hostingMode
    partitionCount: partitionCount
    publicNetworkAccess: publicNetworkAccess
    replicaCount: replicaCount
    semanticSearch: semanticSearch

  }
  sku: sku
  resource sharedPrivateLinkResourceOpenAi 'sharedPrivateLinkResources@2023-11-01' =  {
    name: 'search-shared-private-link-openAi'
    properties: {
      groupId: 'openai_account'
      status: 'Approved'
      provisioningState: 'Succeeded'
      requestMessage: 'automatically created by the system'
      privateLinkResourceId: openAIResourceID
    }
  }
  resource sharedPrivateLinkResourceCosmosDb 'sharedPrivateLinkResources@2023-11-01' =  {
    name: 'search-shared-private-link-cosmosDb'
    properties: {
      groupId: 'Sql'
      status: 'Approved'
      provisioningState: 'Succeeded'
      requestMessage: 'automatically created by the system'
      privateLinkResourceId: comsosAccountResourceID
    }
  }

}


output id string = search.id
output endpoint string = 'https://${name}.search.windows.net/'
output name string = search.name
output principalId string = !empty(searchIdentityProvider) ? search.identity.principalId : ''
output searchService object = search
