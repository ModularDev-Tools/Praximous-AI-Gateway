# core/provider_manager.py
import abc
import os
import yaml
from typing import Dict, Any, Type, Optional

from core.logger import log

PROVIDERS_CONFIG_PATH = os.path.join('config', 'providers.yaml')

class BaseLLMProvider(abc.ABC):
    """Abstract base class for all LLM providers."""
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        log.info(f"Initialized LLM Provider: {self.name}")

    @abc.abstractmethod
    async def generate_async(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generates a response from the LLM asynchronously."""
        pass

class GeminiProvider(BaseLLMProvider):
    """Provider for Google Gemini models."""
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        # Specific Gemini client initialization would go here
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            log.error("GEMINI_API_KEY not found in environment variables.")
            raise ValueError("Missing GEMINI_API_KEY")

    async def generate_async(self, prompt: str, **kwargs) -> Dict[str, Any]:
        log.info(f"GeminiProvider ({self.name}) generating response...")
        # Placeholder for actual Gemini API call
        # You would use a library like 'google.generativeai' here
        return {"provider": self.name, "text": f"Response from Gemini for: '{prompt}'"}

class OllamaProvider(BaseLLMProvider):
    """Provider for local Ollama models."""
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        # Specific Ollama client initialization would go here
        self.base_url = os.getenv("OLLAMA_API_URL")
        if not self.base_url:
            log.error("OLLAMA_API_URL not found in environment variables.")
            raise ValueError("Missing OLLAMA_API_URL")

    async def generate_async(self, prompt: str, **kwargs) -> Dict[str, Any]:
        log.info(f"OllamaProvider ({self.name}) generating response...")
        # Placeholder for actual Ollama API call
        # You would use a library like 'httpx' to call the Ollama endpoint
        return {"provider": self.name, "text": f"Response from Ollama for: '{prompt}'"}


class ProviderManager:
    """Loads and manages all configured LLM providers."""
    PROVIDER_CLASSES: Dict[str, Type[BaseLLMProvider]] = {
        "gemini": GeminiProvider,
        "ollama": OllamaProvider,
    }

    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._load_providers()

    def _load_providers(self):
        log.info("Loading LLM providers from 'config/providers.yaml'...")
        try:
            with open(PROVIDERS_CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f)

            if not config or 'providers' not in config:
                log.warning("Provider config is empty or missing 'providers' key.")
                return

            if not isinstance(config['providers'], list):
                log.error("'providers' key in config/providers.yaml is not a list.")
                return

            for provider_config_entry in config['providers']: # Iterate over the list of provider configurations
                if not isinstance(provider_config_entry, dict):
                    log.warning(f"Skipping invalid provider entry (not a dictionary): {provider_config_entry}")
                    continue

                provider_instance_name = provider_config_entry.get('name')
                provider_type = provider_config_entry.get('type')

                if not provider_instance_name or not provider_type:
                    log.warning(f"Skipping provider entry due to missing 'name' or 'type': {provider_config_entry}")
                    continue

                # Providers are enabled by default unless 'enabled: false' is explicitly set
                if provider_config_entry.get("enabled", True):
                    provider_class = self.PROVIDER_CLASSES.get(provider_type)
                    if provider_class:
                        try:
                            # Pass the instance name and the full config dict for that provider
                            self.providers[provider_instance_name] = provider_class(name=provider_instance_name, config=provider_config_entry)
                        except ValueError as ve:
                            # ValueErrors from provider __init__ are often due to missing env vars/config.
                            log.error(f"Failed to initialize provider '{provider_instance_name}' (type: {provider_type}) due to a configuration issue: {ve}")
                        except Exception as e: # For other unexpected errors during initialization
                            log.error(f"An unexpected error occurred while initializing provider '{provider_instance_name}' (type: {provider_type}): {e}", exc_info=True)
                    else:
                        log.warning(f"No provider class found for type '{provider_type}' (name: '{provider_instance_name}').")
                else:
                    log.info(f"Provider '{provider_instance_name}' (type: {provider_type}) is disabled in config.")
        except FileNotFoundError:
            log.error(f"Provider configuration file not found at '{PROVIDERS_CONFIG_PATH}'.")
        except Exception as e:
            log.error(f"Error loading provider configuration: {e}", exc_info=True)

    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        return self.providers.get(name)

# Global instance for easy access
provider_manager = ProviderManager()