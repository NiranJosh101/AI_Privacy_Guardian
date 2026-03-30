import os
import json
import logging
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import ExplorerState
from dotenv import load_dotenv


load_dotenv()


logger = logging.getLogger(__name__)

llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

async def classification_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Refines the regulatory_map by selecting the most authoritative links using Groq.
    """
    raw_map = state.get("regulatory_map", {})
    
    # Early exit if map is empty
    if not any(raw_map.values()):
        logger.warning("Classification: No links found in regulatory_map. Skipping.")
        return {"regulatory_map": {}}

    print(f"--- DEBUG: ENTERING CLASSIFICATION ---")
    print(f"--- DEBUG: Input Categories: {list(raw_map.keys())} ---")

    # Keep URL and Anchor Text for better LLM decision making
    rich_context = {
        cat: [{"url": l["url"], "text": l["anchor_text"]} for l in links]
        for cat, links in raw_map.items()
    }

    prompt = f"""
        Role: Legal Data Engineer.
        Task: Select the SINGLE most authoritative and relevant URL for each category based on the URL and Anchor Text.

        Categories to analyze:
        {json.dumps(rich_context, indent=2)}

        Selection Logic:
        1. Prioritize canonical pages (e.g., '/privacy-policy' over '/privacy-faq').
        2. Ensure the link points to a full legal document, not a settings toggle or a summary.
        3. If multiple links look identical, pick the one with the most descriptive anchor text.

        Return ONLY a raw JSON object with this exact structure:
        {{
            "privacy": ["url"],
            "terms": ["url"],
            "legal": ["url"]
        }}
    """

    try:
        response = await llm.ainvoke([
            SystemMessage(content="You are a strict JSON assistant. You output raw JSON only. No markdown, no preamble."),
            HumanMessage(content=prompt)
        ])

        # Robust string cleaning for LLM output
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json").split("```").strip()
        elif "```" in content:
            content = content.split("```").split("```").strip()

        refined_map = json.loads(content)
        
        # Validation: Ensure it returned lists
        for cat in refined_map:
            if isinstance(refined_map[cat], str):
                refined_map[cat] = [refined_map[cat]]

        print(f"--- CLASSIFICATION SUCCESS: {refined_map} ---")

    except Exception as e:
        logger.error(f"LLM Classification Error: {e}")
        # Fallback: Just take the highest confidence link from LinkScout
        refined_map = {
            cat: [links["url"]] if links else []
            for cat, links in raw_map.items()
        }
        print("--- CLASSIFICATION FALLBACK TRIGGERED ---")

    return {"regulatory_map": refined_map}