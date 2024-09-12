param containerAppUmidName string
param location string

resource containerAppUserManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  name: containerAppUmidName
  location: location
}
output containerAppUserManagedIdentity object = containerAppUserManagedIdentity

