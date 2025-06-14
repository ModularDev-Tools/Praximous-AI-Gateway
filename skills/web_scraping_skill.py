# skills/web_scraping_skill.py
from typing import Dict, Any, Optional, List
from core.skill_manager import BaseSkill
from core.logger import log
import httpx
from bs4 import BeautifulSoup # Add 'beautifulsoup4' to requirements.txt

class WebScrapingSkill(BaseSkill):
    name: str = "web_scraper"

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "get_page_content").lower()
        url = kwargs.get("url")
        selector = kwargs.get("selector") # CSS selector for extract_elements

        log.info(f"WebScrapingSkill executing. Operation: '{operation}', URL: '{url}', Selector: '{selector}', Prompt: '{prompt}'")

        if not url:
            return self._build_response(success=False, error="Input Error", details="'url' parameter is required.")

        headers = {
            "User-Agent": "PraximousMVP/1.0 (WebScrapingSkill; +http://yourdomain.com/botinfo)" # Be a good bot citizen
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                content = response.text

            if operation == "get_page_content":
                return self._build_response(success=True, data={"url": url, "raw_html_length": len(content), "content_preview": content[:500]+"..."})
            
            elif operation == "extract_text":
                soup = BeautifulSoup(content, "html.parser")
                # Remove script and style elements
                for script_or_style in soup(["script", "style"]):
                    script_or_style.decompose()
                text = soup.get_text(separator=" ", strip=True)
                return self._build_response(success=True, data={"url": url, "extracted_text_length": len(text), "text_preview": text[:500]+"..."})

            elif operation == "extract_elements":
                if not selector:
                    return self._build_response(success=False, error="Input Error", details="'selector' (CSS selector) is required for 'extract_elements' operation.")
                soup = BeautifulSoup(content, "html.parser")
                elements = soup.select(selector)
                extracted_data: List[str] = [el.get_text(strip=True) for el in elements]
                return self._build_response(success=True, data={"url": url, "selector": selector, "elements_found": len(extracted_data), "extracted_elements": extracted_data[:20]}) # Limit preview

            else:
                return self._build_response(success=False, error="Unsupported Operation", details=f"Operation '{operation}' is not supported.")

        except httpx.HTTPStatusError as e:
            log.error(f"WebScrapingSkill HTTP error for {url}: {e.response.status_code}", exc_info=True)
            return self._build_response(success=False, error="API Error", details=f"Failed to fetch URL '{url}'. Status: {e.response.status_code}")
        except httpx.RequestError as e:
            log.error(f"WebScrapingSkill Request error for {url}: {e}", exc_info=True)
            return self._build_response(success=False, error="Network Error", details=f"Could not connect to URL '{url}'. Error: {str(e)}")
        except Exception as e:
            log.error(f"WebScrapingSkill unexpected error for {url}: {e}", exc_info=True)
            return self._build_response(success=False, error="Internal Skill Error", details=str(e))

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Fetches and extracts content from web pages. Use responsibly and ethically, respecting robots.txt and terms of service.",
            "operations": {
                "get_page_content": {
                    "description": "Fetches the raw HTML content of a web page.",
                    "parameters_schema": {"prompt": {"type": "string", "description": "Optional descriptive text."}, "url": {"type": "string", "format": "url", "description": "The URL of the web page to fetch."}},
                    "example_request_payload": {"task_type": self.name, "operation": "get_page_content", "url": "https://example.com"}
                },
                "extract_text": {
                    "description": "Fetches a web page and extracts all visible text content.",
                    "parameters_schema": {"prompt": {"type": "string", "description": "Optional descriptive text."}, "url": {"type": "string", "format": "url", "description": "The URL of the web page."}},
                    "example_request_payload": {"task_type": self.name, "operation": "extract_text", "url": "https://example.com"}
                },
                "extract_elements": {
                    "description": "Fetches a web page and extracts text from elements matching a CSS selector.",
                    "parameters_schema": {
                        "prompt": {"type": "string", "description": "Optional descriptive text."},
                        "url": {"type": "string", "format": "url", "description": "The URL of the web page."},
                        "selector": {"type": "string", "description": "CSS selector (e.g., 'h1', '.my-class', '#my-id p')."}
                    },
                    "example_request_payload": {"task_type": self.name, "operation": "extract_elements", "url": "https://example.com", "selector": "h1"}
                }
            }
        }