metadata description = 'Creates an Azure Cognitive Services instance.'
param name string
param location string = resourceGroup().location
param tags object = {}
@description('The custom subdomain name used to access the API. Defaults to the value of the name parameter.')
param customSubDomainName string = name
param disableLocalAuth bool = false
param deployments array = []
param kind string = 'OpenAI'

@allowed([ 'enabled', 'disabled' ])
param publicNetworkAccess string = 'enabled'
param sku object = {
  name: 'S0'
}
@allowed([ 'None', 'AzureServices' ])
param bypass string = 'None'

param vnet object 
param isPrivate bool 
param prefix string

var networkAcls = {
  defaultAction: 'Allow'
}

var networkAclsWithBypass = {
  defaultAction: 'Allow'
  bypass: bypass
}

resource account 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = {
  name: name
  location: location
  tags: tags
  kind: kind
  properties: {
    customSubDomainName: customSubDomainName
    publicNetworkAccess: publicNetworkAccess
    // Some services do not support bypass in network acls
    networkAcls: (kind == 'FormRecognizer' || kind == 'ComputerVision' || kind == 'SpeechServices') ? networkAcls : networkAclsWithBypass
    disableLocalAuth: disableLocalAuth
  }
  sku: sku
}

@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in deployments: {
  parent: account
  name: deployment.name
  properties: {
    model: deployment.model
    raiPolicyName: contains(deployment, 'raiPolicyName') ? deployment.raiPolicyName : null
  }
  sku: contains(deployment, 'sku') ? deployment.sku : {
    name: 'Standard'
    capacity: 20
  }
}]


resource openAIPrivateEndpoint 'Microsoft.Network/privateEndpoints@2024-01-01' = if (isPrivate) {
  name: '${prefix}-openai-pe'
  location: location
  tags: tags
  properties: {
    privateLinkServiceConnections: [
      {
        name: 'account'
        properties: {
          privateLinkServiceId: account.id
          groupIds: [
            'account'
          ]
        }
      }
    ]
    subnet: {
      id: vnet.properties.subnets[0].id
    }
  }
}

resource openAIPrivateLinkServiceGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-01-01' = if (isPrivate) {
  parent: openAIPrivateEndpoint
  name: '${prefix}-openai-plsg'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'openai'
        properties: {
          privateDnsZoneId: openaibPrivateDnsZone.id
        }
      }
    ]
  }
}

resource openaibPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (isPrivate) {
  name: 'privatelink.openai.azure.com'
  location: 'global'
  tags: tags
}


output endpoint string = account.properties.endpoint
output id string = account.id
output name string = account.name
output location string = account.location
output openAiResourceId string = account.id
