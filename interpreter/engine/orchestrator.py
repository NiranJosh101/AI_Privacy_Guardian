from .components.chunker import PolicyChunker
from .components.retriever import PolicyRetriever
from .components.synthesizer import PolicySynthesizer
from .configs.config_manager import ConfigManager



class InterpreterOrchestrator:
    def __init__(self, config_manager):
        self.config = config_manager.get_interpreter_config()
        self.chunker = PolicyChunker(self.config.chunking)
        self.retriever = PolicyRetriever(self.config.embeddings, self.config.vector_db)
        self.synthesizer = PolicySynthesizer(self.config.llm.model_name)

    async def interpret_policy(self, domain: str, raw_text: str):
        # 1. Chunking (Phase 1)
        chunks = self.chunker.split(raw_text)
        
        # 2. Ingestion (Phase 2)
        # We use the domain as the namespace for isolation
        self.retriever.ingest_chunks(chunks, namespace=domain)
        
        # 3. Targeted Retrieval (Phase 2 Continued)
        # We perform parallel searches across our QUERY_BUCKETS
        relevant_chunks = []
        for bucket in QUERY_BUCKETS.values():
            results = self.retriever.search_parallel(bucket, namespace=domain)
            relevant_chunks.extend(results)
            
        # 4. Structured Synthesis (Phase 3)
        site_profile = self.synthesizer.analyze(relevant_chunks)
        
        # 5. Cleanup
        self.retriever.delete_namespace(domain)
        
        return site_profile