param containerJobName string
param location string
param containerAppUserManagedIdentity object



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
          server: acr.properties.loginServer
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
              value: 'https://${aiSearch.name}.search.windows.net'
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
              value: openAi.properties.endpoint
            }
          ]
        }
      ]
    }
  }
}

resource runPythonJob 'Microsoft.Resources/deploymentScripts@2023-08-01' = {
  name: 'runPythonJob'
  location: location
  kind: 'AzureCLI'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${containerAppUserManagedIdentity.id}': {}
    }
  }
  properties: {
    azCliVersion: '2.61.0'
    retentionInterval: 'PT1H'
    scriptContent: 'az containerapp job start --name ${pythonContainer.name} --resource-group ${resourceGroup().name}'
  }
}
