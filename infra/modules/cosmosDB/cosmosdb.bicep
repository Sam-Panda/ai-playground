
param prefix string
param location string
param tags object
param partitionKey string
param isPrivate bool
param vnet object
param cosmosDbAccountName string = '${prefix}-cosmosdb'
param cosmosDbDatabaseName string
param cosmosDbContainerName string
param cosmosDbPrivateEndpointName string
param cosmosDbDataReaders array = []
param cosmosDbDataContributors array =[]



resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosDbAccountName
  location: location
  tags: tags
  properties: {
    networkAclBypass: 'AzureServices'
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        isZoneRedundant: false
      }
    ]
    publicNetworkAccess: 'Disabled'
    capabilities: []
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2022-05-15' = {
  parent: cosmosDbAccount
  name: cosmosDbDatabaseName
  properties: {
    resource: {
      id: cosmosDbDatabaseName
    }
  }
}

resource container 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: database
  name: cosmosDbContainerName
  properties: {
    resource: {
      id: cosmosDbContainerName
      partitionKey: {
        paths: [
          partitionKey
        ]
        kind: 'Hash'
      }
    }
  }
}

resource cosmosDbPrivateEndpoint 'Microsoft.Network/privateEndpoints@2024-01-01' = if (isPrivate) {
  name: cosmosDbPrivateEndpointName
  location: location
  tags: tags
  properties: {
    privateLinkServiceConnections: [
      {
        name: 'Sql'
        properties: {
          privateLinkServiceId: cosmosDbAccount.id
          groupIds: [
            'Sql'
          ]
        }
      }
    ]
    subnet: {
      id: vnet.properties.subnets[0].id
    }
  }
}

resource cosmosDbPrivateLinkServiceGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-01-01' = if (isPrivate) {
  parent: cosmosDbPrivateEndpoint
  name: '${prefix}-cosmosdb-plsg'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'cosmosDb'
        properties: {
          privateDnsZoneId: cosmosDbPrivateDnsZone.id
        }
      }
    ]
  }
}

resource cosmosDbPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (isPrivate) {
  name: 'privatelink.documents.azure.com'
  location: 'global'
  tags: tags
}


var cosmosDataReaderRoleDefinitionId = '00000000-0000-0000-0000-000000000001'

@batchSize(1)
resource sqlReaderRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2023-04-15' = [for cosmosDbDataReader in cosmosDbDataReaders: {
  name: guid(
    cosmosDataReaderRoleDefinitionId,
    cosmosDbDataReader,
    cosmosDbAccount.id,
    'sqlDbDataContributorRoleAssignment'
  )
  parent: cosmosDbAccount
  properties: {
    principalId: cosmosDbDataReader
    roleDefinitionId: '/${subscription().id}/resourceGroups/${resourceGroup().name}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosDbAccount.name}/sqlRoleDefinitions/${cosmosDataReaderRoleDefinitionId}'
    scope: cosmosDbAccount.id
  }
}
]


var cosmosDataContributorRoleDefinitionId = '00000000-0000-0000-0000-000000000002'

@batchSize(1)
resource sqlContributorRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2023-04-15' = [for cosmosDbDataReader in cosmosDbDataReaders: {
  name: guid(
    cosmosDataContributorRoleDefinitionId,
    cosmosDbDataReader,
    cosmosDbAccount.id,
    'sqlDbDataContributorRoleAssignment'
  )
  parent: cosmosDbAccount
  properties: {
    principalId: cosmosDbDataReader
    roleDefinitionId: '/${subscription().id}/resourceGroups/${resourceGroup().name}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosDbAccount.name}/sqlRoleDefinitions/${cosmosDataContributorRoleDefinitionId}'
    scope: cosmosDbAccount.id
  }
}
]


output cosmosDbAccount object = cosmosDbAccount

