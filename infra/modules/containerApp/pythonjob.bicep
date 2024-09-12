param containerJobName string
param location string
param containerAppUserManagedIdentity object
param cosmosDbAccount object
param database object
param acrLogInServer string
param openAiEndpoint string
param containerAppEnvironmentName string
param tags object
param lawName string
param vnet object
param jobImageName string
param aiSearchName string





resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: lawName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource containerAppEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppEnvironmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: law.properties.customerId
        sharedKey: listKeys(law.id, law.apiVersion).primarySharedKey
      }
    }
    vnetConfiguration: {
      internal: false
      infrastructureSubnetId: vnet.properties.subnets[1].id
    }
  }
}


resource pythonContainer 'Microsoft.App/jobs@2024-03-01' = {
  name: containerJobName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${containerAppUserManagedIdentity.id}': {}
    }
  }
  properties: {
    configuration: {
      manualTriggerConfig: {
        parallelism: 1
        replicaCompletionCount: 1
      }
      replicaRetryLimit: 1
      secrets: [
        {
          name: 'cosmosdbcxnstring'
          value: 'ResourceId=/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosDbAccount.name};Database=${database.name};IdentityAuthType=AccessToken'
        }
      ]
      replicaTimeout: 300
      triggerType: 'Manual'
      registries: [
        {
          identity: containerAppUserManagedIdentity.id
          server: acrLogInServer
        }
      ]
    }
    environmentId: containerAppEnv.id
    template: {
      containers: [
        {
          name: 'python-job'
          image: jobImageName
          env: [
            {
              name: 'AZURE_TENANT_ID'
              value: tenant().tenantId
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: containerAppUserManagedIdentity.properties.clientId
            }
            {
              name: 'AZURE_SEARCH_ENDPOINT'
              value: 'https://${aiSearchName}.search.windows.net'
            }
            {
              name: 'COSMOS_ENDPOINT'
              value: cosmosDbAccount.properties.documentEndpoint
            }
            {
              name: 'COSMOS_DATABASE'
              value: database.name
            }
            {
              name: 'COSMOS_DB_CONNECTION_STRING'
              secretRef: 'cosmosdbcxnstring'
            }
            {
              name: 'OPEN_AI_ENDPOINT'
              value: openAiEndpoint
            }
          ]
        }
      ]
    }
  }
}

// resource runPythonJob 'Microsoft.Resources/deploymentScripts@2023-08-01' = {
//   name: 'runPythonJob'
//   location: location
//   kind: 'AzureCLI'
//   identity: {
//     type: 'UserAssigned'
//     userAssignedIdentities: {
//       '${containerAppUserManagedIdentity.id}': {}
//     }
//   }
//   properties: {
//     azCliVersion: '2.61.0'
//     retentionInterval: 'PT1H'
//     scriptContent: 'az containerapp job start --name ${pythonContainer.name} --resource-group ${resourceGroup().name}'
//   }
// }



