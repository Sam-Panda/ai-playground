$resourceGroupName="rg-lw2kntuhjulzg-westus"
$version="v0.0.9"
$acrName="acrpythonjobretailsearch"


$jobImageName="${acrName}.azurecr.io/ai-search-python-job:${version}"
az acr login -n $acrName

cd ..

docker build -t $jobImageName .

docker push $jobImageName

