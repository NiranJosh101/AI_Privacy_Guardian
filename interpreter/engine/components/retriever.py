import os
import logging
from uuid import uuid4
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from .config_entities import EmbeddingConfig, VectorDBConfig

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
                spec=ServerlessSpec(cloud="aws", region="us-east-1") # Example region
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

    def delete_namespace(self, namespace: str):
        """Cleanup after analysis is done to keep storage lean."""
        self.index.delete(delete_all=True, namespace=namespace)
        logger.info(f"Deleted temporary data for namespace: {namespace}")