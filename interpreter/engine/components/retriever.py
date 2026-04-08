import os
import logging
from uuid import uuid4
import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from configs.config_entities import EmbeddingConfig, VectorDBConfig

logger = logging.getLogger(__name__)

class PolicyRetriever:
    def __init__(self, embed_config: EmbeddingConfig, vdb_config: VectorDBConfig):
        self.vdb_config = vdb_config
        
        # 1. Initialize Free Local Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=embed_config.model_name)
        
        # 2. Initialize Pinecone Client
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # 3. Ensure Index Exists (Serverless)
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
        Embeds and stores chunks in Pinecone. 
        We use 'namespace' (e.g., the domain name) to isolate different websites.
        """
        try:
            vector_store = PineconeVectorStore.from_texts(
                texts=chunks,
                embedding=self.embeddings,
                index_name=self.vdb_config.index_name,
                namespace=namespace
            )
            logger.info(f"Successfully ingested {len(chunks)} chunks into Pinecone namespace: {namespace}")
            return vector_store
        except Exception as e:
            logger.error(f"Failed Pinecone ingestion: {str(e)}")
            raise e
        
    

    async def search_parallel(self, queries: list[str], namespace: str, top_k: int = 3) -> list[str]:
        """
        Executes multiple vector searches concurrently to reduce overall latency.
        Returns a deduplicated list of the most relevant text chunks.
        """
        # Initialize the LangChain VectorStore abstraction for searching
        vector_store = PineconeVectorStore(
            index_name=self.vdb_config.index_name,
            embedding=self.embeddings,
            namespace=namespace
        )

        # 1. Create a list of 'tasks' (one for each query in the bucket)
        # We use a wrapper to make the synchronous search call 'awaitable'
        tasks = [
            self._async_search(vector_store, query, top_k) 
            for query in queries
        ]

        # 2. Fire all queries at once and wait for the results
        results_nested = await asyncio.gather(*tasks)

        # 3. Flatten the list and deduplicate (avoiding feeding the same text twice to the LLM)
        flat_results = [item for sublist in results_nested for item in sublist]
        unique_results = list(set(flat_results))

        logger.info(f"Parallel search completed for {len(queries)} queries. Found {len(unique_results)} unique chunks.")
        return unique_results

    async def _async_search(self, vector_store, query, top_k):
        """Helper to run the blocking similarity search in a thread."""
        loop = asyncio.get_event_loop()
        # similarity_search is a blocking network call, so we run it in a thread pool
        docs = await loop.run_in_executor(
            None, 
            vector_store.similarity_search, 
            query, 
            top_k
        )
        return [doc.page_content for doc in docs]

    def delete_namespace(self, namespace: str):
        """Cleanup after analysis is done to keep storage lean."""
        self.index.delete(delete_all=True, namespace=namespace)
        logger.info(f"Deleted temporary data for namespace: {namespace}")