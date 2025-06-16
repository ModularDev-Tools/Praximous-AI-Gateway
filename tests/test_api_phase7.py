# tests/test_api_phase7.py
import sqlite3
import sys # For sys.executable
import importlib # For reloading modules if needed
import pytest
import subprocess
import os
from httpx import AsyncClient
from unittest.mock import call # For checking mock call arguments
from typing import AsyncGenerator # Set is not used directly in this file's top level
import pytest_asyncio # Import for the decorator
# import secrets # secrets is not used directly as keys come from conftest

# Make sure the main app can be imported
from api.server import app
import core # Import core package to access submodules like core.audit_logger
# Import specific names from core.audit_logger for the session-scoped fixture and security module
from core.audit_logger import DB_PATH as ORIGINAL_MODULE_DB_PATH, init_db as original_module_init_db
# Test keys are now sourced from conftest.py
from .conftest import TEST_API_KEY_1, TEST_API_KEY_2, INVALID_TEST_API_KEY # These are fixed strings from conftest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up the environment for testing API key authentication.
    This runs once per session.
    """
    # core.audit_logger.DB_PATH is 'logs/praximous_audit.db'
    main_db_path = ORIGINAL_MODULE_DB_PATH # Use the directly imported original path
    os.makedirs(os.path.dirname(main_db_path), exist_ok=True)
    if os.path.exists(main_db_path): # Clean up main audit DB at start of session
        try:
            os.remove(main_db_path)
        except PermissionError:
            print(f"WARNING: Could not remove main audit DB {main_db_path} at session start, might be in use.", file=sys.stderr)
    original_module_init_db() # Initialize the main audit DB using the original init_db

def test_generate_api_key_cli():
    """
    Tests the `python main.py --generate-api-key` CLI command.
    """
    # Define variables before using them
    python_exe = sys.executable
    env = os.environ.copy() # Create a copy of the current environment
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Prepend project_root to PYTHONPATH if it's not already there for the subprocess
    existing_pythonpath = env.get("PYTHONPATH", "")
    args_list = [python_exe, os.path.join(project_root, "main.py"), "--generate-api-key"]
    env_vars = env
    cwd_dir = project_root

    if project_root not in existing_pythonpath.split(os.pathsep):
        env_vars["PYTHONPATH"] = project_root + os.pathsep + existing_pythonpath

    result = subprocess.run(args_list, capture_output=True, text=True, check=False, env=env_vars, cwd=cwd_dir)
    assert result.returncode == 0, f"CLI command failed. Stderr: {result.stderr}"
    
    # Extract the key: it's printed between two newlines, and might be preceded/followed by logs.
    # Find the line that is exactly 64 characters long after stripping whitespace.
    output_lines = result.stdout.strip().splitlines()
    generated_key_line = next((line for line in output_lines if len(line.strip()) == 64), None)
    assert generated_key_line is not None, f"Could not find 64-character API key in CLI output. Stdout: {result.stdout}"
    # Assert the stripped length is 64, just in case
    assert len(generated_key_line.strip()) == 64, f"Generated key format is incorrect. Found line: {generated_key_line}"
    assert "Generated new API Key." in result.stdout, f"Expected log message not found in CLI output. Stdout: {result.stdout}"

@pytest.mark.asyncio
async def test_process_endpoint_no_api_key(async_client: AsyncClient): # Use async_client from conftest
    """Test /api/v1/process endpoint without an API key."""
    response = await async_client.post("/api/v1/process", json={"task_type": "test", "prompt": "hello"})
    assert response.status_code == 401 # Or 403 depending on auto_error in APIKeyHeader
    assert "Not authenticated" in response.json()["detail"].lower() or "api key is missing" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_process_endpoint_invalid_api_key(async_client: AsyncClient, invalid_api_key_for_test: str): # Use async_client and fixture
    """Test /api/v1/process endpoint with an invalid API key."""
    headers = {"X-API-Key": invalid_api_key_for_test} # Use the key from conftest fixture
    response = await async_client.post("/api/v1/process", json={"task_type": "test", "prompt": "hello"}, headers=headers)
    assert response.status_code == 403
    assert "invalid api key" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_process_endpoint_valid_api_key_skill_not_found(async_client: AsyncClient, valid_api_key_1: str): # Use async_client and fixture
    """
    Test /api/v1/process endpoint with a valid API key but a non-existent skill.
    This also implicitly tests that the API key validation passed.
    """
    headers = {"X-API-Key": valid_api_key_1} # Use the key from conftest fixture
    # Assuming "non_existent_skill" is not a real skill or LLM route
    response = await async_client.post("/api/v1/process", json={"task_type": "non_existent_skill", "prompt": "hello"}, headers=headers)
    assert response.status_code == 404 # Skill not found
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_audit_log_captures_api_key(async_client: AsyncClient, valid_api_key_1: str, mocker): # Use async_client, key fixture, and mocker
    """
    Test that the audit log correctly captures the API key for /api/v1/process.
    by checking the arguments passed to a mocked log_interaction.
    """
    # Patch log_interaction where it's used by the process_task endpoint
    mock_log_interaction = mocker.patch("api.server.log_interaction")

    headers = {"X-API-Key": valid_api_key_1} # Use one of the known valid test keys from conftest
    request_payload = {"task_type": "audit_test_skill", "prompt": "log this key"}

    # This request will likely result in a 404 if 'audit_test_skill' doesn't exist,
    # but the interaction (and API key) should still be logged in the finally block.
    await async_client.post("/api/v1/process", json=request_payload, headers=headers)

    # Assert that the mock was called once
    mock_log_interaction.assert_called_once()
    
    # Get the keyword arguments it was called with
    # call_args is a tuple; call_args[1] is the kwargs dict
    called_kwargs = mock_log_interaction.call_args[1] 

    assert called_kwargs.get("api_key") == valid_api_key_1
    assert called_kwargs.get("task_type") == request_payload["task_type"]
    assert called_kwargs.get("prompt") == request_payload["prompt"]
    # You can add more assertions for other arguments like 'status', 'request_id' if needed


# Add more tests for other endpoints (e.g., /api/v1/analytics, /api/v1/skills)
# to ensure they are also protected.

@pytest.mark.asyncio
async def test_skills_endpoint_protected(async_client: AsyncClient, valid_api_key_1: str): # Use async_client and fixture
    """Test /api/v1/skills endpoint requires API key."""
    response_no_key = await async_client.get("/api/v1/skills")
    assert response_no_key.status_code == 401

    headers = {"X-API-Key": valid_api_key_1} # Use the key from conftest fixture
    response_with_key = await async_client.get("/api/v1/skills", headers=headers)
    assert response_with_key.status_code == 200 # Assuming it returns 200 on success

@pytest.mark.asyncio
async def test_analytics_endpoint_protected(async_client: AsyncClient):
    """Test /api/v1/analytics endpoint requires API key."""
    response_no_key = await async_client.get("/api/v1/analytics")
    assert response_no_key.status_code == 401

@pytest.mark.asyncio
async def test_specific_skill_capabilities_endpoint_protected(async_client: AsyncClient):
    """Test /api/v1/skills/{skill_name}/capabilities endpoint requires API key."""
    response_no_key = await async_client.get("/api/v1/skills/echo/capabilities") # Using 'echo' as an example skill
    assert response_no_key.status_code == 401


# --- Unit tests for core.security functions ---

def test_load_api_keys_from_env(monkeypatch):
    """Test core.security.load_api_keys loads keys correctly from environment."""
    test_keys_str = "key1, key2 , key3  ,key4"
    expected_keys_set = {"key1", "key2", "key3", "key4"}
    monkeypatch.setenv("PRAXIMOUS_API_KEYS", test_keys_str)
    
    # Reload core.security to trigger load_api_keys with the new env var
    # or directly call load_api_keys if it's safe to do so without side effects
    # For this test, we'll directly call it after ensuring VALID_API_KEYS is accessible
    import core.security
    core.security.load_api_keys() # This will use the monkeypatched env var
    
    assert core.security.VALID_API_KEYS == expected_keys_set

def test_load_api_keys_empty_env(monkeypatch):
    """Test core.security.load_api_keys with an empty PRAXIMOUS_API_KEYS."""
    monkeypatch.setenv("PRAXIMOUS_API_KEYS", "")
    import core.security
    core.security.load_api_keys()
    assert core.security.VALID_API_KEYS == set()

def test_load_api_keys_no_env_var(monkeypatch):
    """Test core.security.load_api_keys when PRAXIMOUS_API_KEYS is not set."""
    monkeypatch.delenv("PRAXIMOUS_API_KEYS", raising=False)
    import core.security
    core.security.load_api_keys()
    assert core.security.VALID_API_KEYS == set()

@pytest.mark.asyncio
async def test_validate_api_key_unit_valid(mocker):
    """Unit test core.security.validate_api_key with a valid key."""
    from core.security import validate_api_key, VALID_API_KEYS, api_key_header
    
    VALID_API_KEYS.clear()
    VALID_API_KEYS.add("unit_test_valid_key")
    
    # Mock Security(api_key_header) to return our test key
    async def mock_security_call():
        return "unit_test_valid_key"
        
    mocker.patch("core.security.Security", return_value=mock_security_call) 
    # This patching of Security itself is a bit tricky. A more direct way is to pass the key.
    # Let's call validate_api_key directly with the key for simplicity in unit test.
    
    result = await validate_api_key(api_key="unit_test_valid_key")
    assert result == "unit_test_valid_key"
    VALID_API_KEYS.clear() # Clean up

@pytest.mark.asyncio
async def test_validate_api_key_unit_invalid(mocker):
    """Unit test core.security.validate_api_key with an invalid key."""
    from core.security import validate_api_key, VALID_API_KEYS, HTTPException
    VALID_API_KEYS.clear()
    VALID_API_KEYS.add("unit_test_valid_key")
    with pytest.raises(HTTPException) as excinfo:
        await validate_api_key(api_key="invalid_key")
    assert excinfo.value.status_code == 403
    VALID_API_KEYS.clear() # Clean up

@pytest.mark.asyncio
async def test_validate_api_key_unit_no_keys_configured():
    """Unit test core.security.validate_api_key when no keys are configured."""
    from core.security import validate_api_key, VALID_API_KEYS
    VALID_API_KEYS.clear() # Ensure it's empty
    result = await validate_api_key(api_key="any_key_but_should_pass_due_to_no_config")
    assert result == "unprotected_access_no_keys_defined"

# The temp_db_for_audit_test fixture is no longer needed by tests in this file
# as test_audit_log_captures_api_key now uses mocking.
# If other tests in this file were to need it, it could be kept,
# but ensure its DB interactions are robust (e.g., closing connections).
# For now, it's removed to simplify. If you have other tests needing it,
# ensure they correctly manage DB connections to avoid PermissionErrors on teardown.
