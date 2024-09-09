metadata description = 'Creates a role assignment for a service principal.'
param principalIds array = []

@allowed([
  'Device'
  'ForeignGroup'
  'Group'
  'ServicePrincipal'
  'User'
  'managedidentity'
])
param principalType string = 'ServicePrincipal'
param roleDefinitionId string


@batchSize(1)
resource role 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for principalId in principalIds: {
  name: guid(subscription().id, resourceGroup().id, principalId, roleDefinitionId)
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)

   
  }
}
]
