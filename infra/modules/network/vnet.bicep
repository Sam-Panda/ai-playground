param prefix string
param location string
param tags object
param addressPrefix string



resource vnet 'Microsoft.Network/virtualNetworks@2024-01-01' = {
  name: '${prefix}-vnet'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [

      {
        name: 'privateEndpoontSubnet'
        properties: {
          addressPrefix: cidrSubnet(cidrSubnet(addressPrefix, 22, 0), 24, 1)
        }
      }
      {
        name: 'miscSubnet'
        properties: {
          addressPrefix: cidrSubnet(cidrSubnet(addressPrefix, 22, 1), 23, 0)
        }
      }
    ]
  }
}

output vnet object = vnet
