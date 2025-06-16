# tests/test_advanced_analytics_phase5.py
import pytest
import httpx
from datetime import datetime, timedelta, timezone

from core.enums import LicenseTier as CoreLicenseTierEnum
from core.audit_logger import log_interaction # To populate data

# Mark all tests in this module to use asyncio
pytestmark = pytest.mark.anyio

# Helper to create some audit log data
async def populate_audit_data(api_key_to_log: str, num_entries_per_provider: int = 2):
    providers = ["skill:echo", "gemini_pro_model", "ollama_default", None] # Include a None provider
    task_types = ["echo", "default_llm_tasks", "another_task"]
    statuses = ["success", "error"]
    
    # Create entries over a few days
    base_time = datetime.now(timezone.utc) - timedelta(days=5)

    for i in range(num_entries_per_provider * len(providers)):
        provider = providers[i % len(providers)]
        task_type = task_types[i % len(task_types)]
        status = statuses[i % len(statuses)]
        # Vary timestamps to test date filtering
        timestamp = base_time + timedelta(days=i // len(providers), hours=i % 24)
        
        # Manually call log_interaction, need to ensure DB_PATH is correct for tests
        # This assumes the main audit DB is used by these tests, as setup by setup_test_environment
        log_interaction(
            request_id=f"test_adv_analytics_{i}",
            task_type=task_type,
            status=status,
            latency_ms=(i + 1) * 100,
            provider=provider,
            api_key=api_key_to_log, # Use the provided API key
            prompt=f"Test prompt {i}",
            response_data={"message": f"Test response {i}"},
            # We need to mock datetime.now for log_interaction or pass timestamp
            # For simplicity, log_interaction uses datetime.now(). We'll rely on natural time progression.
            # Or, modify log_interaction to accept a timestamp (better for testing).
            # For now, we'll assume log_interaction uses its own now()
        )

@pytest.fixture(scope="module", autouse=True)
async def setup_analytics_data(valid_api_key_1: str, event_loop): # event_loop needed for async fixture
    """Populate audit data once per module for advanced analytics tests."""
    # This assumes that the main audit DB is initialized by setup_test_environment
    # and that log_interaction writes to it.
    await populate_audit_data(valid_api_key_1, num_entries_per_provider=3)


async def test_tasks_over_time_analytics(async_client: httpx.AsyncClient, valid_api_key_1: str, mocker):
    mocker.patch("core.license_manager.get_current_license_tier", return_value=CoreLicenseTierEnum.ENTERPRISE)
    headers = {"X-API-Key": valid_api_key_1}
    
    response = await async_client.get("/api/v1/analytics/tasks-over-time?granularity=day", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    if data: # Check content if data is present
        assert "date_group" in data[0]
        assert "count" in data[0]
        assert isinstance(data[0]["count"], int)

async def test_requests_per_provider_analytics(async_client: httpx.AsyncClient, valid_api_key_1: str, mocker):
    mocker.patch("core.license_manager.get_current_license_tier", return_value=CoreLicenseTierEnum.ENTERPRISE)
    headers = {"X-API-Key": valid_api_key_1}

    response = await async_client.get("/api/v1/analytics/requests-per-provider", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    if data:
        assert "provider_name" in data[0]
        assert "count" in data[0]
        assert isinstance(data[0]["count"], int)
        # Check if 'N/A' provider is handled if present
        assert any(item["provider_name"] == "N/A" for item in data) or not any(p is None for p in ["skill:echo", "gemini_pro_model", "ollama_default", None])

async def test_average_latency_per_provider_analytics(async_client: httpx.AsyncClient, valid_api_key_1: str, mocker):
    mocker.patch("core.license_manager.get_current_license_tier", return_value=CoreLicenseTierEnum.ENTERPRISE)
    headers = {"X-API-Key": valid_api_key_1}

    response = await async_client.get("/api/v1/analytics/average-latency-per-provider", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    if data:
        assert "provider_name" in data[0]
        assert "average_latency" in data[0]
        assert isinstance(data[0]["average_latency"], float)

async def test_advanced_analytics_licensing_community_tier(async_client: httpx.AsyncClient, valid_api_key_1: str, mocker):
    mocker.patch("core.license_manager.get_current_license_tier", return_value=CoreLicenseTierEnum.COMMUNITY)
    headers = {"X-API-Key": valid_api_key_1}

    endpoints_to_test = [
        "/api/v1/analytics/tasks-over-time",
        "/api/v1/analytics/requests-per-provider",
        "/api/v1/analytics/average-latency-per-provider"
    ]
    for endpoint in endpoints_to_test:
        response = await async_client.get(endpoint, headers=headers)
        assert response.status_code == 403
        assert "Advanced Analytics feature is not available" in response.json()["detail"]

async def test_advanced_analytics_licensing_pro_tier(async_client: httpx.AsyncClient, valid_api_key_1: str, mocker):
    # Assuming ADVANCED_ANALYTICS_UI is available for PRO tier based on TIER_FEATURES
    mocker.patch("core.license_manager.get_current_license_tier", return_value=CoreLicenseTierEnum.PRO)
    headers = {"X-API-Key": valid_api_key_1}

    # Test one endpoint, assuming if one works, the dependency is correctly applied
    response = await async_client.get("/api/v1/analytics/tasks-over-time", headers=headers)
    assert response.status_code == 200 # PRO tier should have access

async def test_tasks_over_time_invalid_granularity(async_client: httpx.AsyncClient, valid_api_key_1: str, mocker):
    mocker.patch("core.license_manager.get_current_license_tier", return_value=CoreLicenseTierEnum.ENTERPRISE)
    headers = {"X-API-Key": valid_api_key_1}
    
    response = await async_client.get("/api/v1/analytics/tasks-over-time?granularity=invalid", headers=headers)
    assert response.status_code == 400
    assert "Invalid granularity" in response.json()["detail"]

# Note: The populate_audit_data helper and setup_analytics_data fixture assume that
# log_interaction writes to the main audit DB (logs/praximous_audit.db) and that
# this DB is initialized by the session-scoped setup_test_environment fixture in
# test_api_phase7.py. If tests require truly isolated DBs for analytics data population,
# a more complex fixture setup involving monkeypatching DB_PATH for log_interaction
# within the scope of these tests would be needed, similar to temp_audit_db in test_api_phase3.py.
# For now, we rely on the global audit DB being populated.