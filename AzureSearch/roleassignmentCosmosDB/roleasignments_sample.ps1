# check if the module is installed, if not instal it 
if (-not (Get-Module -Name Az.CosmosDB -ListAvailable)) {
    Install-Module -Name Az.CosmosDB -AllowClobber -Force
}
Set-AzContext -TenantId  ""

$resourceGroupName = "RGAzAI"
$accountName = "azcosmXXXXXXXX"
# https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-setup-rbac#built-in-role-definitions
$readOnlyRoleDefinitionId = "00000000-0000-0000-0000-000000000002" # as fetched above
# For Service Principals make sure to use the Object ID as found in the Enterprise applications section of the Azure Active Directory portal blade.
$principalId = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
New-AzCosmosDBSqlRoleAssignment -AccountName $accountName -ResourceGroupName $resourceGroupName -RoleDefinitionId $readOnlyRoleDefinitionId -Scope "/" -PrincipalId $principalId

