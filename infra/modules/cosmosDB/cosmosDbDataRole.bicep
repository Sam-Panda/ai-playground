param roleAssignmentName string
param cosmosDbAccount object
param cosmosDataRoleDefinitionId string
param principalId string
param parent resource


resource sqlRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2023-04-15' = {
  name: roleAssignmentName
  parent: cosmosDbAccount
  properties: {
    principalId: principalId
    roleDefinitionId: '/${subscription().id}/resourceGroups/${resourceGroup().name}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosDbAccount.name}/sqlRoleDefinitions/${cosmosDataRoleDefinitionId}'
    scope: cosmosDbAccount.id
  }
}
