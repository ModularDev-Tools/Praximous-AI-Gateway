# tests/test_api_phase2.py
import pytest
import httpx  # For the async_client type hint
from unittest.mock import AsyncMock, patch # For mocking async methods and os.getenv
import os
import yaml

# Mark all tests in this module to use asyncio
pytestmark = pytest.mark.anyio

# Import necessary classes for testing and mocking
from core.provider_manager import ProviderManager, GeminiProvider, OllamaProvider
# NoAvailableProviderError will be implicitly tested via API status codes

async def test_api_successful_routing_to_primary_provider(async_client: httpx.AsyncClient, mocker):
    """
    Test that a request through /api/v1/process successfully uses the primary provider
    when the ModelRouter and ProviderManager are integrated.
    Assumes 'gemini' is the first in 'default_llm_tasks' preference.
    """
    mock_gemini_response = {"provider": "gemini", "text": "Response from primary (Gemini)"}
    # Patch the generate_async method of the GeminiProvider class
    mocker.patch.object(GeminiProvider, 'generate_async', AsyncMock(return_value=mock_gemini_response))
    # Ensure Ollama is not called if Gemini succeeds
    mock_ollama_generate = mocker.patch.object(OllamaProvider, 'generate_async', AsyncMock())

    payload = {"task_type": "default_llm_tasks", "prompt": "Hello primary provider!"}
    response = await async_client.post("/api/v1/process", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["text"] == "Response from primary (Gemini)"
    assert data["result"]["provider"] == "gemini"
    assert data["message"] == "Request routed via gemini"
    mock_ollama_generate.assert_not_called()


async def test_api_failover_to_secondary_provider(async_client: httpx.AsyncClient, mocker):
    """
    Test that if the primary provider fails, the request automatically routes
    to the secondary provider (e.g., Ollama).
    Assumes 'gemini' fails and 'ollama' is next in 'default_llm_tasks'.
    """
    # Mock the primary provider (Gemini) to raise an exception
    mocker.patch.object(GeminiProvider, 'generate_async', AsyncMock(side_effect=Exception("Primary provider failed intentionally for test")))
    
    # Mock the secondary provider's (Ollama) successful response
    mock_ollama_response = {"provider": "ollama", "text": "Response from secondary (Ollama)"}
    mocker.patch.object(OllamaProvider, 'generate_async', AsyncMock(return_value=mock_ollama_response))

    payload = {"task_type": "default_llm_tasks", "prompt": "Testing failover!"}
    response = await async_client.post("/api/v1/process", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["text"] == "Response from secondary (Ollama)"
    assert data["result"]["provider"] == "ollama"
    assert data["message"] == "Request routed via ollama"


async def test_api_all_providers_fail(async_client: httpx.AsyncClient, mocker):
    """
    Test the API response when all configured LLM providers fail.
    """
    # Mock all configured providers in 'default_llm_tasks' to raise exceptions
    mocker.patch.object(GeminiProvider, 'generate_async', AsyncMock(side_effect=Exception("Gemini provider failed for test")))
    mocker.patch.object(OllamaProvider, 'generate_async', AsyncMock(side_effect=Exception("Ollama provider failed for test")))

    payload = {"task_type": "default_llm_tasks", "prompt": "What if everyone is down?"}
    response = await async_client.post("/api/v1/process", json=payload)
    
    assert response.status_code == 503 # Service Unavailable
    data = response.json()
    assert "detail" in data
    assert "All LLM providers are currently unavailable." in data["detail"]

@patch('core.provider_manager.os.getenv') # Patch os.getenv within the provider_manager module
def test_provider_manager_loads_config_correctly_unit(mock_getenv, tmp_path):
    """
    Test that ProviderManager correctly loads and interprets providers.yaml.
    This would be more of a unit test for ProviderManager itself.
    """
    # Setup mock for os.getenv
    def side_effect_getenv(key):
        if key == "GEMINI_API_KEY":
            return "fake_gemini_key_for_test"
        if key == "OLLAMA_API_URL":
            return "http://fakeollamaurl:11434"
        return None # Default behavior for other keys
    mock_getenv.side_effect = side_effect_getenv

    # Create a temporary providers.yaml for this test
    temp_config_dir = tmp_path / "config"
    temp_config_dir.mkdir()
    temp_providers_yaml_path = temp_config_dir / "providers.yaml"
    
    test_providers_config_content = {
        "providers": {
            "gemini": {"enabled": True, "api_key_env_var": "GEMINI_API_KEY"}, # Added api_key_env_var for clarity
            "ollama": {"enabled": True, "url_env_var": "OLLAMA_API_URL"},     # Added url_env_var for clarity
            "disabled_provider": {"enabled": False},
            "unsupported_provider": {"enabled": True} # A provider not in PROVIDER_CLASSES
        }
    }
    with open(temp_providers_yaml_path, 'w') as f:
        yaml.dump(test_providers_config_content, f)

    # Patch PROVIDERS_CONFIG_PATH in core.provider_manager to use our temp file
    with patch('core.provider_manager.PROVIDERS_CONFIG_PATH', str(temp_providers_yaml_path)):
        # Instantiate ProviderManager to trigger _load_providers
        pm = ProviderManager()

    assert "gemini" in pm.providers
    assert isinstance(pm.providers["gemini"], GeminiProvider)
    # The GeminiProvider itself calls os.getenv("GEMINI_API_KEY") in its __init__
    assert pm.providers["gemini"].api_key == "fake_gemini_key_for_test"

    assert "ollama" in pm.providers
    assert isinstance(pm.providers["ollama"], OllamaProvider)
    # The OllamaProvider itself calls os.getenv("OLLAMA_API_URL") in its __init__
    assert pm.providers["ollama"].base_url == "http://fakeollamaurl:11434"

    assert "disabled_provider" not in pm.providers # Check that disabled providers are not loaded
    assert "unsupported_provider" not in pm.providers # Check that unsupported providers are logged but not loaded

    # Check that os.getenv was called by the provider initializers
    mock_getenv.assert_any_call("GEMINI_API_KEY")
    mock_getenv.assert_any_call("OLLAMA_API_URL")