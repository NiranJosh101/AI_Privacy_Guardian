import os
import logging
from uuid import uuid4
import asyncio
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from configs.config_entities import EmbeddingConfig, VectorDBConfig

load_dotenv()
logger = logging.getLogger(__name__)

class PolicyRetriever:
    def __init__(self, embed_config: EmbeddingConfig, vdb_config: VectorDBConfig):
        self.vdb_config = vdb_config
        self.embeddings = HuggingFaceEmbeddings(model_name=embed_config.model_name)
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        if self.vdb_config.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.vdb_config.index_name,
                dimension=self.vdb_config.dimension,
                metric=self.vdb_config.metric,
                spec=ServerlessSpec(cloud="aws", region="us-east-1") 
            )
        
        self.index = self.pc.Index(self.vdb_config.index_name)

    def ingest_chunks(self, chunks: list[str], namespace: str):
        """
        Embeds and stores chunks. 
        Force-converts namespace to string to prevent 'list' errors.
        """
        try:
            # Ensure namespace is a string even if a list or None was passed
            safe_namespace = str(namespace) if isinstance(namespace, list) else str(namespace)
            
            vector_store = PineconeVectorStore.from_texts(
                texts=chunks,
                embedding=self.embeddings,
                index_name=self.vdb_config.index_name,
                namespace=safe_namespace
            )
            logger.info(f"Ingested into Pinecone namespace: {safe_namespace}")
            return vector_store
        except Exception as e:
            logger.error(f"Failed Pinecone ingestion: {str(e)}")
            raise e

    async def search_parallel(self, queries: list[str], namespace: str, top_k: int = 3) -> list[str]:
        # Force-convert namespace to string
        safe_namespace = str(namespace) if isinstance(namespace, list) else str(namespace)
        
        vector_store = PineconeVectorStore(
            index_name=self.vdb_config.index_name,
            embedding=self.embeddings,
            namespace=safe_namespace
        )

        tasks = [self._async_search(vector_store, query, top_k) for query in queries]
        results_nested = await asyncio.gather(*tasks)

        flat_results = [item for sublist in results_nested for item in sublist]
        unique_results = list(set(flat_results))
        return unique_results

    async def _async_search(self, vector_store, query, top_k):
        loop = asyncio.get_event_loop()
        docs = await loop.run_in_executor(
            None, 
            vector_store.similarity_search, 
            query, 
            top_k
        )
        return [doc.page_content for doc in docs]

    def delete_namespace(self, namespace: str):
        # Force-convert namespace to string
        safe_namespace = str(namespace) if isinstance(namespace, list) else str(namespace)
        self.index.delete(delete_all=True, namespace=safe_namespace)
        logger.info(f"Deleted namespace: {safe_namespace}")