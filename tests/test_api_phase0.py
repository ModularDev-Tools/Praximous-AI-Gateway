# tests/test_api_phase0.py
import pytest
import httpx # For the async_client type hint

# Mark all tests in this module to use asyncio
pytestmark = pytest.mark.anyio

# API Key will be injected by fixture `valid_api_key_1` from conftest.py

async def test_echo_skill_success(async_client: httpx.AsyncClient, valid_api_key_1: str):
    payload = {"task_type": "echo", "prompt": "Hello Test!"}
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["echoed_prompt"] == "Hello Test!"
    assert data["result"]["message"] == "Prompt was successfully echoed."

async def test_text_manipulation_skill_uppercase_success(async_client: httpx.AsyncClient, valid_api_key_1: str):
    payload = {"task_type": "text_manipulation", "prompt": "test upper", "operation": "uppercase"}
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["original_text"] == "test upper"
    assert data["result"]["modified_text"] == "TEST UPPER"

async def test_text_manipulation_skill_invalid_operation(async_client: httpx.AsyncClient, valid_api_key_1: str):
    payload = {"task_type": "text_manipulation", "prompt": "test invalid", "operation": "nonexistent"}
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 400 # Skill should report error, API translates to 400
    data = response.json()
    assert "detail" in data
    assert "Unsupported operation: nonexistent" in data["detail"]

async def test_simple_math_skill_add_success(async_client: httpx.AsyncClient, valid_api_key_1: str):
    payload = {"task_type": "simple_math", "prompt": "Add", "num1": 5, "num2": 3, "operation": "add"}
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["result"] == 8

async def test_simple_math_skill_divide_by_zero(async_client: httpx.AsyncClient, valid_api_key_1: str):
    payload = {"task_type": "simple_math", "prompt": "Divide", "num1": 5, "num2": 0, "operation": "divide"}
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Cannot divide by zero" in data["detail"]
    
async def test_simple_math_skill_missing_number(async_client: httpx.AsyncClient, valid_api_key_1: str):
    payload = {"task_type": "simple_math", "prompt": "Missing num2", "num1": 5, "operation": "add"}
    headers = {"X-API-Key": valid_api_key_1} # Use the injected fixture
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Both 'num1' and 'num2' must be provided as numbers" in data["detail"]

async def test_process_non_existent_skill(async_client: httpx.AsyncClient, valid_api_key_1: str):
    payload = {"task_type": "non_existent_skill", "prompt": "This should fail"}
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Skill or LLM route 'non_existent_skill' not found."

async def test_process_missing_task_type(async_client: httpx.AsyncClient, valid_api_key_1: str):
    payload = {"prompt": "Missing task_type"} # task_type is missing
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 422 # Unprocessable Entity due to Pydantic validation
    data = response.json()
    assert "detail" in data
    # Make message check more robust
    assert any(
        d.get("loc") == ["body", "task_type"] and "field required" in d.get("msg", "").lower()
        for d in data["detail"])

async def test_process_missing_prompt(async_client: httpx.AsyncClient, valid_api_key_1: str):
    payload = {"task_type": "echo"} # prompt is missing
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.post("/api/v1/process", json=payload, headers=headers)
    assert response.status_code == 422 # Unprocessable Entity
    data = response.json()
    assert "detail" in data
    assert any(
        d.get("loc") == ["body", "prompt"] and "field required" in d.get("msg", "").lower()
        for d in data["detail"])

async def test_list_all_skills_capabilities(async_client: httpx.AsyncClient, valid_api_key_1: str):
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.get("/api/v1/skills", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "echo" in data
    assert "text_manipulation" in data
    assert "simple_math" in data
    assert data["echo"]["skill_name"] == "echo"
    assert "description" in data["echo"]

async def test_get_specific_skill_capabilities_success(async_client: httpx.AsyncClient, valid_api_key_1: str):
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.get("/api/v1/skills/echo/capabilities", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["skill_name"] == "echo"
    assert "A simple skill that echoes back the provided prompt." in data["description"]

async def test_get_capabilities_non_existent_skill(async_client: httpx.AsyncClient, valid_api_key_1: str):
    headers = {"X-API-Key": valid_api_key_1}
    response = await async_client.get("/api/v1/skills/non_existent_skill/capabilities", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Skill 'non_existent_skill' not found."
