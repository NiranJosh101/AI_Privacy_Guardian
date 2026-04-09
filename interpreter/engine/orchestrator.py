import uuid
import time
import json
from engine.components.chunker import PolicyChunker
from engine.components.retriever import PolicyRetriever
from engine.components.synthesizer import PolicySynthesizer
from configs.config_manager import ConfigManager
from engine.prompts.queries import QUERY_BUCKETS

class InterpreterOrchestrator:
    def __init__(self, config_manager: ConfigManager):
        print(f"DEBUG: Initializing InterpreterOrchestrator...")
        self.config = config_manager.get_interpreter_config()
        self.chunker = PolicyChunker(self.config.chunking)
        self.retriever = PolicyRetriever(self.config.embeddings, self.config.vector_db)
        self.synthesizer = PolicySynthesizer()
        print(f"DEBUG: Components initialized successfully.")

    async def interpret_policy(self, domain: str, raw_text: str):
        start_time = time.time()
        
        # Domain Safeguard
        clean_domain = domain if isinstance(domain, list) and len(domain) > 0 else str(domain)
        session_id = f"run_{uuid.uuid4().hex}"
        
        print(f"\n{'='*60}\nDEBUG START: {clean_domain}\n{'='*60}")
        
        # 1. Chunking
        chunks = self.chunker.split(raw_text)
        print(f"DEBUG: Phase 1 (Chunking) -> Created {len(chunks)} chunks.")

        # 2. Ingestion
        print(f"DEBUG: Phase 2 (Ingestion) -> Sending to Pinecone (Namespace: {session_id})...")
        self.retriever.ingest_chunks(chunks, namespace=session_id)

        # 3. Retrieval
        relevant_chunks = []
        for bucket_name, queries in QUERY_BUCKETS.items():
            print(f"DEBUG: Phase 2.5 (Retrieval) -> Searching '{bucket_name}'...")
            results = await self.retriever.search_parallel(queries, namespace=session_id)
            relevant_chunks.extend(results)
        
        unique_relevant = list(set(relevant_chunks))
        print(f"DEBUG: Phase 2.5 Result -> Gathered {len(unique_relevant)} unique context chunks.")

        # 4. Synthesis & THE ACTUAL PROFILE
        print(f"DEBUG: Phase 3 (Synthesis) -> Requesting LLM Analysis...")
        try:
            site_profile = self.synthesizer.analyze(unique_relevant)
            
            # --- THIS IS THE PART YOU WANTED ---
            print("\n" + "🚀" * 10 + " FINAL SITE PROFILE " + "🚀" * 10)
            try:
                # Try pydantic v2 dump
                profile_data = site_profile.model_dump()
            except AttributeError:
                # Fallback for pydantic v1 or dict
                profile_data = site_profile.dict() if hasattr(site_profile, 'dict') else site_profile
            
            print(json.dumps(profile_data, indent=4))
            print("🚀" * 31 + "\n")
            # -----------------------------------

        except Exception as e:
            print(f"DEBUG: ERROR during Synthesis: {str(e)}")
            self.retriever.delete_namespace(session_id)
            raise e

        # 5. Cleanup
        print(f"DEBUG: Phase 4 (Cleanup) -> Deleting Pinecone Namespace {session_id}...")
        self.retriever.delete_namespace(session_id)
        
        total_duration = time.time() - start_time
        print(f"DEBUG: Total Runtime: {total_duration:.2f}s")
        print(f"{'='*60}\nDEBUG END\n{'='*60}\n")
        
        return site_profile