import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import ExplorerState

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

async def classification_node(state: ExplorerState) -> Dict[str, Any]:
    """
    Refines the regulatory_map by selecting the most authoritative links.
    """

    raw_map = state.get("regulatory_map", {})

    if not any(raw_map.values()):
        return {"regulatory_map": {}}

    # Simplify input (reduce tokens + noise)
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
        {simplified_map}

        Return ONLY valid JSON in this format:
        {{
        "privacy": ["url"],
        "terms": ["url"],
        "legal": ["url"]
        }}
    """

    try:
        response = await llm.ainvoke([
            SystemMessage(content="You strictly return valid JSON only."),
            HumanMessage(content=prompt)
        ])

        refined_map = json.loads(response.content)

    except Exception:
        # Safe fallback: pick top link from each category
        refined_map = {
            cat: links[:1] for cat, links in simplified_map.items()
        }

    return {"regulatory_map": refined_map}