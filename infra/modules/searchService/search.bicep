metadata description = 'Creates an Azure AI Search instance.'
param name string
param isPrivate bool 
param prefix string
param location string = resourceGroup().location
param tags object = {}
param vnet object

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

var aisearchPrivateEndpointName = '${prefix}-aisearch-pe'

var searchIdentityProvider = (sku.name == 'free') ? null : {
  type: 'SystemAssigned'
}

resource search 'Microsoft.Search/searchServices@2023-11-01' = {
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

}

resource aisearchprivateEndpoint 'Microsoft.Network/privateEndpoints@2024-01-01' = if (isPrivate) {
  name: aisearchPrivateEndpointName
  location: location
  tags: tags
  properties: {
    privateLinkServiceConnections: [
      {
        name: 'searchService'
        properties: {
          privateLinkServiceId: search.id
          groupIds: [
            'searchService'
          ]
        }
      }
    ]
    subnet: {
      id: vnet.properties.subnets[0].id
    }
  }
}


resource aisearchPrivateLinkServiceGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-01-01' = if (isPrivate) {
  parent: aisearchprivateEndpoint
  name: '${prefix}-aisearch-plsg'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'searchService'
        properties: {
          privateDnsZoneId: aiSearchPrivateDnsZone.id
        }
      }
    ]
  }
}

resource aiSearchPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (isPrivate) {
  name: 'privatelink.search.windows.net'
  location: 'global'
  tags: tags
}


output id string = search.id
output endpoint string = 'https://${name}.search.windows.net/'
output name string = search.name
output principalId string = !empty(searchIdentityProvider) ? search.identity.principalId : ''
output searchService object = search
