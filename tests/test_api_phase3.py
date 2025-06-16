# tests/test_api_phase3.py
import pytest
import os
import sqlite3
import httpx
from unittest.mock import patch, AsyncMock # Import AsyncMock here

# Mark all tests in this module to use asyncio
pytestmark = pytest.mark.anyio
# API Key will be injected by fixture `valid_api_key_1` from conftest.py

@pytest.fixture
def temp_audit_db(tmp_path, monkeypatch):
    """
    Pytest fixture to create a temporary, isolated audit database for testing.
    This ensures that each test run is independent and doesn't affect the real audit log.
    """
    # Create a temporary database file in the test's temp directory
    db_path = tmp_path / "test_audit.db"
    
    # Use monkeypatch to redirect the DB_PATH constant in the audit_logger module
    # to our temporary database path for the duration of the test.
    monkeypatch.setattr("core.audit_logger.DB_PATH", str(db_path))
    
    # Import the module *after* patching, or reload it if already imported.
    import core.audit_logger
    core.audit_logger.init_db() # Initialize the schema in the temp DB
    
    yield str(db_path) # Provide the path to the test function if needed

async def test_api_process_creates_audit_log(async_client: httpx.AsyncClient, temp_audit_db: str, valid_api_key_1: str):
    """
    Tests that a successful call to /api/v1/process creates a correct entry in the audit log.
    """
    payload = {"task_type": "echo", "prompt": "Test audit logging"}
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 200
    
    # Directly query the temporary database to verify the log entry
    with sqlite3.connect(temp_audit_db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interactions")
        record = cursor.fetchone()
        
        assert record is not None
        assert record["task_type"] == "echo"
        assert record["status"] == "success"
        assert record["provider"] == "skill:echo"
        assert record["prompt"] == "Test audit logging"
        assert record["api_key"] == valid_api_key_1 # Verify API key is logged

async def test_analytics_endpoint_pagination(async_client: httpx.AsyncClient, temp_audit_db: str, valid_api_key_1: str):
    """
    Tests the limit and offset pagination on the /api/v1/analytics endpoint.
    """
    headers = {"X-API-Key": valid_api_key_1}
    # Create 5 log entries
    for i in range(5):
        await async_client.post("/api/v1/process", json={"task_type": "echo", "prompt": f"test {i}"}, headers=headers)

    # Test limit
    response_limit = await async_client.get("/api/v1/analytics?limit=3", headers=headers)
    assert response_limit.status_code == 200
    data_limit = response_limit.json()
    assert data_limit["total_matches"] == 5
    assert len(data_limit["data"]) == 3
    assert data_limit["data"][0]["prompt"] == "test 4" # Most recent
    # Ensure API key is not in analytics response
    assert "api_key" not in data_limit["data"][0]

    # Test offset
    response_offset = await async_client.get("/api/v1/analytics?limit=3&offset=3", headers=headers)
    assert response_offset.status_code == 200
    data_offset = response_offset.json()
    assert data_offset["total_matches"] == 5
    assert len(data_offset["data"]) == 2 # Only 2 records left after skipping 3
    assert data_offset["data"][0]["prompt"] == "test 1"

async def test_analytics_endpoint_filtering(async_client: httpx.AsyncClient, temp_audit_db: str, valid_api_key_1: str):
    """
    Tests the task_type filtering on the /api/v1/analytics endpoint.
    """
    headers = {"X-API-Key": valid_api_key_1}
    # Use a mock for the model router to simulate an LLM task
    with patch("core.model_router.ModelRouter.route_request", new_callable=AsyncMock) as mock_route:
        # Configure the mock to return a dictionary that looks like a real provider response
        mock_route.return_value = {"provider": "gemini", "text": "mocked response"}

        # Log two 'echo' tasks and one 'default_llm_tasks' task
        await async_client.post("/api/v1/process", json={"task_type": "echo", "prompt": "echo 1"}, headers=headers)
        await async_client.post("/api/v1/process", json={"task_type": "echo", "prompt": "echo 2"}, headers=headers)
        await async_client.post("/api/v1/process", json={"task_type": "default_llm_tasks", "prompt": "llm task"}, headers=headers)

    # Fetch only the 'echo' tasks
    response = await async_client.get("/api/v1/analytics?task_type=echo", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_matches"] == 2
    assert len(data["data"]) == 2
    assert all(r["task_type"] == "echo" for r in data["data"])

    # Fetch only the 'default_llm_tasks' tasks
    response_llm = await async_client.get("/api/v1/analytics?task_type=default_llm_tasks", headers=headers)
    assert response_llm.status_code == 200
    data_llm = response_llm.json()
    assert data_llm["total_matches"] == 1
    assert data_llm["data"][0]["task_type"] == "default_llm_tasks"