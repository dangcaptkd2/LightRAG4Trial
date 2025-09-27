from abc import ABC

from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectBaseSettings(BaseSettings, ABC):
    """Base settings for the project."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class LLMSettings(ProjectBaseSettings):
    """LLM settings."""

    llm_binding: str = "openai"
    llm_model: str = "gpt-4.1-nano"
    llm_binding_host: str = "https://api.openai.com/v1"
    llm_binding_api_key: str = "sk-proj-1234567890"

    enable_llm_cache_for_extract: bool = True
    enable_llm_cache: bool = True


class EmbeddingSettings(ProjectBaseSettings):
    """Settings for the embedding-related options."""

    embedding_binding: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    embedding_binding_host: str = "https://api.openai.com/v1"
    embedding_binding_api_key: str = "sk-proj-1234567890"


class StorageSettings(ProjectBaseSettings):
    """Settings for the storage-related options."""

    lightrag_graph_storage: str = "Neo4JStorage"
    lightrag_KV_storage: str = "PGKVStorage"
    lightrag_doc_status_storage: str = "PGDocStatusStorage"
    lightrag_vector_storage: str = "PGVectorStorage"


class PostgresSettings(ProjectBaseSettings):
    """Settings for the postgres-related options."""

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "postgres"
    postgres_max_connections: int = 10

    postgres_vector_index_type: str = "HNSW"
    postgres_HNSW_M: int = 16
    postgres_HNSW_ef: int = 200
    postgres_IVFFLAT_LISTS: int = 100


class Neo4JSettings(ProjectBaseSettings):
    """Settings for the neo4j-related options."""

    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j"

    neo4j_max_connection_pool_size: int = 100
    neo4j_connection_timeout: int = 30
    neo4j_connection_acquisition_timeout: int = 30
    neo4j_max_transaction_retry_time: int = 30
    neo4j_max_connection_lifetime: int = 300
    neo4j_liveness_check_timeout: int = 30
    neo4j_keep_alive: bool = True


class ProjectSettings(ProjectBaseSettings):
    """Project settings."""

    llm_settings: LLMSettings = LLMSettings()
    embedding_settings: EmbeddingSettings = EmbeddingSettings()
    storage_settings: StorageSettings = StorageSettings()
    postgres_settings: PostgresSettings = PostgresSettings()
    neo4j_settings: Neo4JSettings = Neo4JSettings()

    host: str = "0.0.0.0"
    port: int = 9621
    webui_title: str = "LightRAG"
    webui_description: str = (
        "LightRAG is a lightweight RAG framework for building AI-powered applications."
    )

    ### Directory Configuration (defaults to current working directory)
    input_dir: str = "."
    working_dir: str = "."
    workspace: str = "workspace"

    ### Max concurrency requests of LLM (for both query and document processing)
    max_async: int = 2
    max_tokens: int = 10000
    chunk_size: int = 1200
    chunk_overlap_size: int = 100
    timeout: int = 240
    cosine_threshold: float = 0.2
    max_parallel_insert: int = 2
    summary_language: str = "English"

    # Max nodes return from graph retrieval in webui
    max_graph_nodes: int = 10000


settings = ProjectSettings()

print(settings.embedding_settings.embedding_dim)
