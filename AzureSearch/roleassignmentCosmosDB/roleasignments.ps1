

# https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-setup-rbac#built-in-role-definitions
$readOnlyRoleDefinitionId = "00000000-0000-0000-0000-000000000002" # as fetched above
# $principalId="1a03fe00-228c-4ac5-9579-2abfc601baa8"
$principalId="a25cb071-acf9-4713-acfd-7d317ae934aa"
$ResourceGroupName="RGOpenAI"
$accountName="azcosmosdbopenai"

# check if the role is present
$roleAssignment = Get-AzCosmosDBSqlRoleAssignment -AccountName $accountName -ResourceGroupName $resourceGroupName | Where-Object { $_.PrincipalId -eq $principalId -and $_.RoleDefinitionId -match $readOnlyRoleDefinitionId }
if (!$roleAssignment) {
    Write-Output "Assigning role to the service principal"
    New-AzCosmosDBSqlRoleAssignment -AccountName $accountName -ResourceGroupName $resourceGroupName -RoleDefinitionId $readOnlyRoleDefinitionId -Scope "/" -PrincipalId $principalId  
}





