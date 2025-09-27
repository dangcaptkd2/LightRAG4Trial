from lightrag import LightRAG
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.llm.ollama import ollama_embed
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.settings import settings
from lightrag.types import GPTKeywordExtractionFormat
from lightrag.utils import EmbeddingFunc


async def openai_alike_model_complete(
    prompt,
    system_prompt=None,
    history_messages=None,
    keyword_extraction=False,
    **kwargs,
) -> str:
    keyword_extraction = kwargs.pop("keyword_extraction", None)
    if keyword_extraction:
        kwargs["response_format"] = GPTKeywordExtractionFormat
    if history_messages is None:
        history_messages = []

    return await openai_complete_if_cache(
        model=settings.llm_settings.llm_model,
        prompt=prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        base_url=settings.llm_settings.llm_binding_host,
        api_key=settings.llm_settings.llm_binding_api_key,
        **kwargs,
    )


embedding_func = EmbeddingFunc(
    embedding_dim=settings.embedding_settings.embedding_dim,
    func=lambda texts: openai_embed(
        texts,
        model=settings.embedding_settings.embedding_model,
        base_url=settings.embedding_settings.embedding_binding_host,
        api_key=settings.embedding_settings.embedding_binding_api_key,
    ),
)

embedding_ollama_func = EmbeddingFunc(
    embedding_dim=settings.embedding_settings.embedding_dim,
    func=lambda texts: ollama_embed(
        texts,
        embed_model=settings.embedding_settings.embedding_model,
    ),
)


async def initialize_rag():
    rag = LightRAG(
        working_dir=settings.working_dir,
        workspace=settings.workspace,
        llm_model_func=openai_alike_model_complete,
        llm_model_name=settings.llm_settings.llm_model,
        llm_model_max_async=settings.max_async,
        summary_max_tokens=settings.max_tokens,
        chunk_token_size=int(settings.chunk_size),
        chunk_overlap_token_size=int(settings.chunk_overlap_size),
        embedding_func=embedding_func,
        kv_storage=settings.storage_settings.lightrag_KV_storage,
        graph_storage=settings.storage_settings.lightrag_graph_storage,
        vector_storage=settings.storage_settings.lightrag_vector_storage,
        doc_status_storage=settings.storage_settings.lightrag_doc_status_storage,
        vector_db_storage_cls_kwargs={
            "cosine_better_than_threshold": settings.cosine_threshold
        },
        enable_llm_cache_for_entity_extract=settings.llm_settings.enable_llm_cache_for_extract,
        enable_llm_cache=settings.llm_settings.enable_llm_cache,
        max_parallel_insert=settings.max_parallel_insert,
        max_graph_nodes=settings.max_graph_nodes,
        addon_params={"language": settings.summary_language},
    )
    await rag.initialize_storages()  # Initialize storage backends
    await initialize_pipeline_status()  # Initialize processing pipeline
    return rag
