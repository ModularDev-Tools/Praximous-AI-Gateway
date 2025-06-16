# tests/conftest.py
import pytest
import httpx
import sys
import os
import pytest_asyncio # Import for the decorator
from typing import AsyncGenerator, Set, Optional # Keep Set and Optional
import warnings # Import the warnings module

# --- Eager sys.path modification ---
# This will run as soon as conftest.py is loaded by pytest,
# which is very early in the process, before test module imports.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
    # You can add a print here for debugging if needed:
    # print(f"DEBUG [conftest.py - Eager]: Project root '{_project_root}' inserted into sys.path.")
# --- End Eager sys.path modification ---

# Centralized Test API Keys
TEST_API_KEY_1 = "test_key_001_abcdefghijklmnopqrstuvwxyz123456" # Fixed for predictability
TEST_API_KEY_2 = "test_key_002_zyxwutsrqponmlkjihgfedcba654321" # Fixed for predictability
INVALID_TEST_API_KEY = "this-is-an-invalid-key-for-testing"


@pytest.fixture(scope="session", autouse=True)
def add_project_root_to_path():
    """Ensure the project root is in sys.path for all test sessions."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        # This might be redundant if the eager modification above works,
        # but it's kept for explicitness and good practice.
            # Note: This fixture itself doesn't need to return anything.
            # Its purpose is to modify sys.path.
        sys.path.insert(0, project_root)

        # Filter specific DeprecationWarnings from google._upb
        warnings.filterwarnings("ignore", message="Type google\\._upb\\._message\\.MessageMapContainer uses PyType_Spec", category=DeprecationWarning)
        warnings.filterwarnings("ignore", message="Type google\\._upb\\._message\\.ScalarMapContainer uses PyType_Spec", category=DeprecationWarning)


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Specifies the asyncio backend for pytest-asyncio.
    """
    return "asyncio"


@pytest_asyncio.fixture(scope="module") # Explicitly mark as an asyncio fixture
async def async_client(test_api_keys_for_session: Set[str]) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Provides an asynchronous HTTP client for testing the FastAPI application.
    The client makes requests directly to the app in memory without needing a running server.
    It uses a dependency override for API key validation.
    """
    from api.server import app
    from core.security import validate_api_key as original_validate_api_key
    from fastapi import Security, HTTPException # For mock dependency
    from core.security import api_key_header # For mock dependency

    async def mock_validate_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
        if not test_api_keys_for_session: # Should not happen if fixture is set up
            # This case means the test_api_keys_for_session fixture didn't provide keys
            raise HTTPException(status_code=500, detail="Test API keys not configured for session.")
        if not api_key:
            raise HTTPException(status_code=401, detail="Not authenticated: API key is missing.")
        if api_key not in test_api_keys_for_session:
            raise HTTPException(status_code=403, detail=f"Access denied: Invalid API key for test session. Key: {api_key[:10]}...")
        return api_key

    app.dependency_overrides[original_validate_api_key] = mock_validate_api_key

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
    
    # Clear the override after the client's scope ends
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def test_api_keys_for_session() -> Set[str]:
    """Provides a set of API keys valid for the test session."""
    return {TEST_API_KEY_1, TEST_API_KEY_2}

@pytest.fixture(scope="session")
def valid_api_key_1() -> str:
    return TEST_API_KEY_1

@pytest.fixture(scope="session")
def invalid_api_key_for_test() -> str:
    return INVALID_TEST_API_KEY
