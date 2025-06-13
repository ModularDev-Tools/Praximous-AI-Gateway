# core/model_router.py
from typing import List, Dict, Any

from core.logger import log
from core.provider_manager import provider_manager # Import our global instance

class NoAvailableProviderError(Exception):
    """Custom exception raised when all providers fail for a given request."""
    pass

class ModelRouter:
    def __init__(self):
        # For the MVP, we'll use a simple dictionary to define routing rules.
        # This can be expanded later to load from a YAML config file.
        self.routing_rules: Dict[str, List[str]] = {
            "default_llm_tasks": ["gemini", "ollama"],
            # Example of a task that should only use a local/cheap model
            "internal_summary": ["ollama"],
        }
        self.provider_manager = provider_manager
        log.info("ModelRouter initialized.")

    async def route_request(self, prompt: str, task_type: str = "default_llm_tasks") -> Dict[str, Any]:
        """
        Routes a request to the best available provider based on routing rules
        and handles failover.
        """
        provider_preference = self.routing_rules.get(task_type, self.routing_rules["default_llm_tasks"])
        log.info(f"Routing request for task_type='{task_type}'. Provider preference: {provider_preference}")

        last_error = None
        for provider_name in provider_preference:
            provider = self.provider_manager.get_provider(provider_name)

            if not provider:
                log.warning(f"Provider '{provider_name}' from routing rule not available in ProviderManager.")
                continue

            try:
                log.info(f"Attempting to use provider: {provider_name}")
                result = await provider.generate_async(prompt)
                log.info(f"Successfully received response from provider: {provider_name}")
                return result # Return on the first successful response
            except Exception as e:
                log.error(f"Provider '{provider_name}' failed for task_type '{task_type}': {e}", exc_info=True)
                last_error = e
                # Continue to the next provider in the list (failover)

        # If the loop completes without returning, all providers have failed.
        log.error(f"All configured providers ({provider_preference}) failed for task_type '{task_type}'.")
        raise NoAvailableProviderError(f"All providers failed. Last error: {last_error}")

# Global instance for easy access
model_router = ModelRouter()