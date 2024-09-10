param containerJobName object
param location string

resource swaUserManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  name: swaUmidName
  location: location
}

resource containerAppUserManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  name: containerAppUmidName
  location: location
}

resource containerAppEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppEnvironmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'

    }
    vnetConfiguration: {
      internal: false
      infrastructureSubnetId: vnet.properties.subnets[2].id
    }
  }
}



resource pythonJob 'Microsoft.App/jobs@2024-03-01' = {
  name: containerJobName
  location: location
  properties: {
    configuration: {
      secrets: [
        {
          name: 'keyvaultname'
          value: ''
        }
        {
          name: 'tenantid'
          value: tenant().tenantId
        }
        {
          name: 'clientid'
          value: containerAppUserManagedIdentity.properties.clientId
        }
      ]
      replicaTimeout: 'PT1H'
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
            
          ]
        }
      ]
    }
  }
}
