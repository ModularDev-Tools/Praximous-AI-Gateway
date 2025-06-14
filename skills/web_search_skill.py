# skills/web_search_skill.py
from typing import Dict, Any, List
from core.skill_manager import BaseSkill
from core.logger import log
import httpx
import os
import json

# Example: Using Serper API (serper.dev)
# You would set SERPER_API_KEY in your .env file
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY") # e.g., SERPER_API_KEY
SEARCH_API_ENDPOINT = "https://google.serper.dev/search" # Example for Serper

class WebSearchSkill(BaseSkill):
    name: str = "web_search_tool"

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "perform_search").lower()
        query = kwargs.get("query", prompt) # Use 'query' kwarg or the main prompt
        num_results = kwargs.get("num_results", 5)

        log.info(f"WebSearchSkill executing. Operation: '{operation}', Query: '{query}', Num Results: {num_results}")

        if not SEARCH_API_KEY:
            return self._build_response(success=False, error="Configuration Error", details="SEARCH_API_KEY is not set in environment variables.")
        if not query or not query.strip():
            return self._build_response(success=False, error="Input Error", details="'query' cannot be empty.")

        if operation == "perform_search":
            headers = {
                "X-API-KEY": SEARCH_API_KEY,
                "Content-Type": "application/json"
            }
            payload = json.dumps({
                "q": query,
                "num": int(num_results)
            })

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(SEARCH_API_ENDPOINT, headers=headers, content=payload)
                    response.raise_for_status()
                    search_results = response.json()

                # Adapt this part based on the actual structure of your chosen search API's response
                # For Serper, results are often in an 'organic' list
                processed_results = []
                if "organic" in search_results:
                    for item in search_results["organic"][:int(num_results)]:
                        processed_results.append({
                            "title": item.get("title"),
                            "link": item.get("link"),
                            "snippet": item.get("snippet")
                        })
                
                return self._build_response(success=True, data={"query": query, "results_count": len(processed_results), "results": processed_results})
            except httpx.HTTPStatusError as e:
                log.error(f"WebSearchSkill HTTP error: {e.response.status_code} - {e.response.text}", exc_info=True)
                return self._build_response(success=False, error="API Error", details=f"Search API request failed with status {e.response.status_code}.")
            except Exception as e:
                log.error(f"WebSearchSkill unexpected error: {e}", exc_info=True)
                return self._build_response(success=False, error="Internal Skill Error", details=str(e))
        else:
            return self._build_response(success=False, error="Unsupported Operation", details=f"Operation '{operation}' is not supported.")

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Performs a web search using an external search engine API (e.g., Serper.dev). Requires SEARCH_API_KEY.",
            "operations": {
                "perform_search": {
                    "description": "Searches the web for a given query and returns a list of results (title, link, snippet).",
                    "parameters_schema": {
                        "query": {"type": "string", "description": "The search query. Can also be passed via 'prompt'."},
                        "num_results": {"type": "integer", "default": 5, "description": "Number of search results to return."}
                    },
                    "example_request_payload": {"task_type": self.name, "operation": "perform_search", "query": "latest advancements in AI", "num_results": 3}
                }
            }
        }