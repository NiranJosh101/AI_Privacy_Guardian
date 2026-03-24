import os
import json

from typing import Dict, Any
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import ExplorerState



load_dotenv()

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

    if not any(raw_map.values()):
        return {"regulatory_map": {}}

  
    simplified_map = {
        cat: [item["url"] for item in links]
        for cat, links in raw_map.items()
    }

    
    prompt = f"""
        You are a Legal Data Engineer.
        From the given categories of URLs, select the SINGLE most authoritative and relevant URL for each category.

        Guidelines:
        1. Prefer main/global versions over regional or localized ones.
        2. Ignore archive, summary, or outdated versions.
        3. Prefer cleaner, canonical URLs.
        4. If no good option exists, return an empty list for that category.

        Input:
        {json.dumps(simplified_map, indent=2)}

        Return ONLY a JSON object with this exact structure:
        {{
            "privacy": ["url"],
            "terms": ["url"],
            "legal": ["url"]
        }}
    """

    try:
       
        response = await llm.ainvoke([
            SystemMessage(content="You are a JSON assistant. You output raw JSON only, no markdown headers or conversational text."),
            HumanMessage(content=prompt)
        ])

       
        content = response.content.strip().removeprefix("```json").removesuffix("```").strip()
        refined_map = json.loads(content)

    except Exception as e:
        print(f"LLM Error, falling back: {e}")
        
        refined_map = {
            cat: links[:1] for cat, links in simplified_map.items()
        }

    return {"regulatory_map": refined_map}