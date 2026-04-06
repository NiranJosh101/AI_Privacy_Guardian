import os
from langchain_groq import ChatGroq
from .prompts import INTERPRETER_SYSTEM_PROMPT
from ..models.domain import SiteProfile

class PolicySynthesizer:
    def __init__(self, model_name: str = "llama3-70b-8192"):
        # We use temperature 0 for extraction to ensure deterministic results
        self.llm = ChatGroq(
            temperature=0, 
            model_name=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        # This is the "Magic" — it forces the LLM to return a SiteProfile object
        self.structured_llm = self.llm.with_structured_output(SiteProfile)

    def analyze(self, relevant_chunks: list[str]) -> SiteProfile:
        """
        Synthesizes the final SiteProfile from the retrieved chunks.
        """
        # 1. Join chunks into one context block
        context = "\n\n---\n\n".join(relevant_chunks)
        
        # 2. Format the prompt
        prompt = INTERPRETER_SYSTEM_PROMPT.format(context=context)
        
        # 3. Invoke LLM and get validated Pydantic object
        try:
            site_profile = self.structured_llm.invoke(prompt)
            return site_profile
        except Exception as e:
            # In production, you'd log this for MLOps monitoring
            print(f"Extraction Error: {e}")
            raise e