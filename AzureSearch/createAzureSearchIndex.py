import os 
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.identity import ClientSecretCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswParameters,
    HnswAlgorithmConfiguration,
    SemanticPrioritizedFields,
    SearchableField,
    SearchField,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchFieldDataType,
    SearchIndex,
    SemanticSearch,
    SemanticConfiguration,
    SemanticField,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    SearchIndexerSkillset,
    IndexingParametersConfiguration,
    IndexingParameters,
    SearchIndexer,
    FieldMapping

)

from typing import List, Dict
from openai import AzureOpenAI
from dotenv import load_dotenv

from pathlib import Path



def data_source_creation(
    service_endpoint: str,
    credential: ClientSecretCredential,
    cosmos_db_container_name: str,
    azure_cosmosdb_resource_id_connection_string: str,
    search_indexer_data_source_name: str,
):

    ds_client = SearchIndexerClient(service_endpoint, credential)
    container = SearchIndexerDataContainer(name=cosmos_db_container_name)
    data_source_connection = SearchIndexerDataSourceConnection(
            name=search_indexer_data_source_name, type="cosmosdb", connection_string=azure_cosmosdb_resource_id_connection_string, container=container
        )
    data_source = ds_client.create_or_update_data_source_connection(data_source_connection)
    return data_source

# creating the Indexes
def create_search_index(
        credential: ClientSecretCredential,
        config: Dict,
        service_endpoint: str,
        search_index_name: str,
        search_index_all_fields: List[Dict],
        search_index_key_field: str,
        searchable_fields: List[str],
        filterable_fields: List[str],
        sortable_fields: List[str],
        facetable_fields: List[str],
        vector_field: str,
        semantic_config_isEnabled: bool,
        semantic_config_name: str,
        semantic_config_title_filed: str,
        semantic_config_keyword_fields: List[str],
        semantic_config_content_fields: List[str],        
        azure_openai_endpoint: str,
        open_ai_embedding_deployment_name: str,
        open_ai_embedding_model_name: str

):

    vector_search_profile_name = f"Hnsw_{vector_field}_Profile"
    vector_search_vectorizer_name = f"Vectorizer_{vector_field}"

    # Define the index fields
    client = SearchIndexClient(service_endpoint, credential)
    fields = []
    for search_index_field in search_index_all_fields:
        field = search_index_field["field"]
        datatype = search_index_field["type"]
        
        if field == vector_field:
            print(f"Vector Field {field}")
            srch = SearchField(
                    name=field,
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_profile_name=vector_search_profile_name,
                    vector_search_dimensions=1536                              
            )
        
        else:
            print(f"Field {field}") 
            type = ""
            # setting the datatype
            if datatype == "string":
                type = SearchFieldDataType.String
            elif datatype == "integer" or datatype == "int":
                type = SearchFieldDataType.Int32
            elif datatype == "double" or datatype == "float":
                type = SearchFieldDataType.Double
            elif datatype == "datetime":
                type = SearchFieldDataType.DateTimeOffset
            elif datatype == "bool" or datatype == "boolean":
                type = SearchFieldDataType.Boolean
            else:
                type = SearchFieldDataType.String

            if field in searchable_fields:
                srch = SearchableField(name=field, type=type)
            else:
                srch = SimpleField(name=field, type=type)

         
            
            # setting up the different flags in the index definition
            if field == search_index_key_field:
                srch.key = True
            else:
                srch.key = False

            if field in filterable_fields:
                srch.filterable = True
            else:
                srch.filterable = False

            if field in sortable_fields:
                srch.sortable = True
            else:
                srch.sortable = False

            if field in facetable_fields:
                srch.facetable = True
            else:
                srch.facetable = False

        fields.append(srch)

    # create the semantic configuration
    if (semantic_config_isEnabled):
        
        prioritized_fields = SemanticPrioritizedFields()

        # title field
        semantic_title_field = SemanticField(field_name=semantic_config_title_filed)

        #keyword fields
        semantic_keyword_fields = []
        for field in semantic_config_keyword_fields:
            semantic_keyword_fields.append(SemanticField(field_name=field))
        prioritized_fields.keywords_fields = semantic_keyword_fields

        # content field
        semantic_content_fields = []
        for field in semantic_config_content_fields:
            semantic_content_fields.append(SemanticField(field_name=field))
        prioritized_fields.content_fields = semantic_content_fields

        semantic_config_prioritized_fields = prioritized_fields
        semantic_config = SemanticConfiguration(name=semantic_config_name, prioritized_fields=semantic_config_prioritized_fields)


    # create the vector configuration

    vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="myHnsw",
                    kind=VectorSearchAlgorithmKind.HNSW,
                    parameters=HnswParameters(
                        m=4,
                        ef_construction=400,
                        ef_search=500,
                        metric=VectorSearchAlgorithmMetric.COSINE,
                    ),
                ),
                ExhaustiveKnnAlgorithmConfiguration(
                    name="myExhaustiveKnn",
                    kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                    parameters=ExhaustiveKnnParameters(
                        metric=VectorSearchAlgorithmMetric.COSINE
                    ),
                ),
            ],
            profiles=[
                VectorSearchProfile(
                    name=vector_search_profile_name,
                    algorithm_configuration_name="myHnsw",
                    vectorizer_name=vector_search_vectorizer_name,
                ),
                VectorSearchProfile(
                    name="myExhaustiveKnnProfile",
                    algorithm_configuration_name="myExhaustiveKnn",
                ),
            ],
            vectorizers= [
                AzureOpenAIVectorizer(
                    vectorizer_name=vector_search_vectorizer_name,
                    parameters=AzureOpenAIVectorizerParameters(
                        resource_url=azure_openai_endpoint,
                        deployment_name=open_ai_embedding_deployment_name,
                        model_name=open_ai_embedding_model_name
                    )
                )
            ]
        )


    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    
    index = SearchIndex(name=search_index_name, fields=fields, 
                        semantic_search=semantic_search, 
                        vector_search=vector_search)

    client.create_or_update_index(index)
    return index


def create_open_ai_embedding_skillset(
    service_endpoint: str,
    credential: ClientSecretCredential,
    search_skillset_openai_embedding_name: str,
    search_skillset_openai_embedding_input: str,
    search_skillset_openai_embedding_output: str,
    azure_openai_endpoint: str,
    open_ai_embedding_deployment_name: str,
    open_ai_embedding_model_name: str
):

    client = SearchIndexerClient(service_endpoint, credential)
    inp = InputFieldMappingEntry(name="text", source=search_skillset_openai_embedding_input)
    output = OutputFieldMappingEntry(name="embedding", target_name=search_skillset_openai_embedding_output)
    s = AzureOpenAIEmbeddingSkill(name="open-ai-embedding", inputs=[inp], outputs=[output],
                resource_url=azure_openai_endpoint, deployment_name=open_ai_embedding_deployment_name,
                model_name=open_ai_embedding_model_name, dimensions=1536)

    skillset = SearchIndexerSkillset(name=search_skillset_openai_embedding_name, skills=[s], description="example skillset")
    result = client.create_or_update_skillset(skillset)
    return result


def create_search_indexer(
    service_endpoint: str,
    credential: ClientSecretCredential,
    search_indexer_name: str,
    data_source_name: str,
    index_name: str,
    open_ai_embedding_skillset_name: str,
    vector_field: str,
    search_skillset_openai_embedding_output:str,

        
):    
    # we pass the data source, skillsets and targeted index to build an indexer
    configuration = IndexingParametersConfiguration(parsing_mode=None, query_timeout=None, excluded_file_name_extensions=None,
                                                    indexed_file_name_extensions=None, fail_on_unsupported_content_type=None,
                                                    fail_on_unprocessable_document=None,
                                                    index_storage_metadata_only_for_oversized_documents=None,
                                                    first_line_contains_headers=None,
                                                    data_to_extract=None,
                                                    image_action=None,
                                                    allow_skillset_to_read_file_data=None,
                                                    pdf_text_rotation_algorithm=None,
                                                    
                                                    
                                                    )
    parameters = IndexingParameters(configuration=configuration)
    indexer = SearchIndexer(
        name=search_indexer_name,
        data_source_name=data_source_name,
        target_index_name=index_name,
        skillset_name=open_ai_embedding_skillset_name,
        parameters=parameters,
        field_mappings=None,
        output_field_mappings=[FieldMapping(source_field_name=f"document/{search_skillset_openai_embedding_output}", target_field_name=vector_field)],
    )

    indexer_client = SearchIndexerClient(service_endpoint, credential)
    indexer_client.create_or_update_indexer(indexer)
    return indexer

if __name__ == "__main__":
        
    load_dotenv()

    service_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    tenant_id = os.environ["TENANT_ID"]
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    azure_cosmosdb_resource_id_connection_string = os.environ["AZURE_COSMOSDB_RESOURCE_ID_CONNECTION_STRING"]
    azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]

    credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    search_index_client = SearchIndexClient(service_endpoint, credential)

    with open("config/config.json") as file:
        config = json.load(file)


    search_indexer_data_source_name = config["ai-search-config"]["data-source-config"]["cosmos_db_data_source_name"]
    cosmos_db_container_name = config["cosmos-config"]["cosmos_db_container_name"]


    # create the datasource connecting to the cosmosdb
    # The authentication will be done using the search service managed identity.
    # https://learn.microsoft.com/en-us/azure/search/search-howto-index-cosmosdb#supported-credentials-and-connection-strings

    print("Creating the data source")
    data_source = data_source_creation(
        service_endpoint=service_endpoint,
        credential=credential,
        cosmos_db_container_name=cosmos_db_container_name,
        azure_cosmosdb_resource_id_connection_string=azure_cosmosdb_resource_id_connection_string,
        search_indexer_data_source_name=search_indexer_data_source_name,
    )

    # creating Index
    search_index_name = config["ai-search-config"]["search-index-config"]["name"]
    search_index_all_fields = config["ai-search-config"]["search-index-config"]["all_fields"]
    search_index_key_field = config["ai-search-config"]["search-index-config"]["key_field"]
    retrievable_fields = config["ai-search-config"]["search-index-config"]["retrievable_fields"]
    searchable_fields = config["ai-search-config"]["search-index-config"]["searchable_fields"]
    filterable_fields = config["ai-search-config"]["search-index-config"]["filterable_fields"]
    sortable_fields = config["ai-search-config"]["search-index-config"]["sortable_fields"]
    facetable_fields = config["ai-search-config"]["search-index-config"]["facetable_fields"]

    # we are considering that we will have one vector field.
    vector_field = config["ai-search-config"]["search-index-config"]["vector_fields"]

    #semantic configuration details

    semantic_config_isEnabled = config["ai-search-config"]["search-index-config"]["semantic_configurations"]["isEnabled"]
    semantic_config_name = config["ai-search-config"]["search-index-config"]["semantic_configurations"]["name"]
    semantic_config_title_filed = config["ai-search-config"]["search-index-config"]["semantic_configurations"]["title_field"] 
    semantic_config_keyword_fields = config["ai-search-config"]["search-index-config"]["semantic_configurations"]["keyword_fields"]
    semantic_config_content_fields = config["ai-search-config"]["search-index-config"]["semantic_configurations"]["content_fields"]

    open_ai_embedding_deployment_name = config["open_ai_config"]["embedding_deployment_name"]
    open_ai_embedding_model_name = config["open_ai_config"]["embedding_model_name"]

    print("Creating the search index")
    index = create_search_index(
        credential=credential,
        config=config,
        service_endpoint=service_endpoint,
        search_index_name=search_index_name,
        search_index_all_fields=search_index_all_fields,
        search_index_key_field=search_index_key_field,
        searchable_fields=searchable_fields,
        filterable_fields=filterable_fields,
        sortable_fields=sortable_fields,
        facetable_fields=facetable_fields,
        vector_field=vector_field,
        azure_openai_endpoint=azure_openai_endpoint,
        semantic_config_isEnabled=semantic_config_isEnabled,
        semantic_config_name=semantic_config_name,
        semantic_config_title_filed=semantic_config_title_filed,
        semantic_config_keyword_fields=semantic_config_keyword_fields,
        semantic_config_content_fields=semantic_config_content_fields,
        open_ai_embedding_deployment_name=open_ai_embedding_deployment_name,
        open_ai_embedding_model_name=open_ai_embedding_model_name
        
    )

    # create Azure Open AI Embedding skillset

    search_skillset_openai_embedding_name = config["ai-search-config"]["search-skillset-config"]["openai-embedding"]["name"]
    search_skillset_openai_embedding_input = config["ai-search-config"]["search-skillset-config"]["openai-embedding"]["input-column"]
    search_skillset_openai_embedding_output = config["ai-search-config"]["search-skillset-config"]["openai-embedding"]["output-column"]

    print("Creating the skillset")
    open_ai_embedding_skillset = create_open_ai_embedding_skillset(
        service_endpoint=service_endpoint,
        credential=credential,
        search_skillset_openai_embedding_name=search_skillset_openai_embedding_name,
        search_skillset_openai_embedding_input=search_skillset_openai_embedding_input,
        search_skillset_openai_embedding_output=search_skillset_openai_embedding_output,
        azure_openai_endpoint=azure_openai_endpoint,
        open_ai_embedding_deployment_name=open_ai_embedding_deployment_name,
        open_ai_embedding_model_name=open_ai_embedding_model_name
    )


    # create an Indexer
    search_indexer_name = config["ai-search-config"]["search-indexer-config"]["name"]
    print("Creating the indexer")
    indexer = create_search_indexer(
        service_endpoint=service_endpoint,
        credential=credential,
        search_indexer_name=search_indexer_name,
        data_source_name=search_indexer_data_source_name,
        index_name=search_index_name,
        open_ai_embedding_skillset_name=search_skillset_openai_embedding_name,
        vector_field=vector_field,
        search_skillset_openai_embedding_output=search_skillset_openai_embedding_output
    )

    print("Indexer created successfully")

