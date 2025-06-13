# tests/conftest.py
import pytest
import httpx
import sys
import os
from typing import AsyncGenerator

# --- Eager sys.path modification ---
# This will run as soon as conftest.py is loaded by pytest,
# which is very early in the process, before test module imports.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
    # You can add a print here for debugging if needed:
    # print(f"DEBUG [conftest.py - Eager]: Project root '{_project_root}' inserted into sys.path.")
# --- End Eager sys.path modification ---

@pytest.fixture(scope="session", autouse=True)
def add_project_root_to_path():
    """Ensure the project root is in sys.path for all test sessions."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        # This might be redundant if the eager modification above works,
        # but it's kept for explicitness and good practice.
        sys.path.insert(0, project_root)

@pytest.fixture(scope="session")
def anyio_backend():
    """
    Specifies the asyncio backend for pytest-asyncio.
    """
    return "asyncio"


@pytest.fixture(scope="module")
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Provides an asynchronous HTTP client for testing the FastAPI application.
    The client makes requests directly to the app in memory without needing a running server.
    """
    # Import app here, after sys.path has been modified by add_project_root_to_path
    # Ensure your project root is in PYTHONPATH or adjust import accordingly
    # For this structure, if running pytest from the project root, this should work.
    from api.server import app
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
