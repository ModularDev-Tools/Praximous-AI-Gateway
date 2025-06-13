# api/server.py
import time
import uuid
# --- MODIFIED: Import Query for endpoint parameters ---
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from core.logger import log
from core.skill_manager import skill_manager
from core.model_router import model_router, NoAvailableProviderError
# --- MODIFIED: Import the new count function ---
from core.audit_logger import log_interaction, get_all_interactions, count_interactions

# ... (ProcessRequest and ProcessResponse models are unchanged) ...
class ArbitraryKwargsBaseModel(BaseModel):
    model_config = {"extra": "allow"}

class ProcessRequest(ArbitraryKwargsBaseModel):
    task_type: str
    prompt: str

class ProcessResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    message: str | None = None
    details: Optional[str] = None
    request_id: str

# --- MODIFIED: Analytics models now include pagination info ---
class InteractionRecord(BaseModel):
    id: int
    request_id: str
    timestamp: str
    task_type: str
    provider: Optional[str]
    status: str
    latency_ms: Optional[int]
    prompt: Optional[str]
    response_data: Optional[str]

class AnalyticsResponse(BaseModel):
    total_matches: int
    limit: int
    offset: int
    data: List[InteractionRecord]
# --- END MODIFIED ---

app = FastAPI(
    title="Praximous API",
    version="1.0-mvp",
    description="Secure, On-Premise AI Gateway"
)

# ... (process_task endpoint is unchanged from the last step) ...
@app.post("/api/v1/process", response_model=ProcessResponse)
async def process_task(request: ProcessRequest):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    status = "error"
    provider = None
    response_data = None
    try:
        log.info(f"API: [ReqID: {request_id}] Received task='{request.task_type}', prompt='{request.prompt[:50]}...'")
        if request.task_type in model_router.routing_rules:
            try:
                log.info(f"API: [ReqID: {request_id}] Routing to LLM for task_type='{request.task_type}'")
                llm_result = await model_router.route_request(prompt=request.prompt, task_type=request.task_type)
                status = "success" 
                provider = llm_result.get('provider', 'unknown')
                response_data = llm_result
                return ProcessResponse(status=status, result=response_data, message=f"Request routed via {provider}", request_id=request_id)
            except NoAvailableProviderError as e:
                log.error(f"API: [ReqID: {request_id}] All providers failed for task '{request.task_type}': {e}", exc_info=True)
                provider = "failover_exhausted"
                raise HTTPException(status_code=503, detail="All LLM providers are currently unavailable.")
            except Exception as e:
                log.error(f"API: [ReqID: {request_id}] An unexpected error occurred during LLM routing for task '{request.task_type}': {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="An unexpected error occurred during LLM routing.")
        skill_class = skill_manager.get_skill(request.task_type)
        if not skill_class:
            log.warning(f"API: [ReqID: {request_id}] Skill or LLM route not found for task_type='{request.task_type}'")
            raise HTTPException(status_code=404, detail=f"Skill or LLM route '{request.task_type}' not found.")
        skill_instance = skill_class()
        provider = f"skill:{skill_instance.name}" 
        log.info(f"API: [ReqID: {request_id}] Executing skill='{skill_instance.name}'")
        skill_kwargs = request.model_dump(exclude={"task_type", "prompt"})
        skill_response = await skill_instance.execute(prompt=request.prompt, **skill_kwargs)
        if skill_response.get("success"):
            log.info(f"API: [ReqID: {request_id}] Skill='{skill_instance.name}' execution successful.")
            status = "success"
            response_data = skill_response.get("data")
            return ProcessResponse(status=status, result=response_data, message=skill_response.get("message"), details=skill_response.get("details"), request_id=request_id)
        else:
            log.warning(f"API: [ReqID: {request_id}] Skill='{skill_instance.name}' execution reported failure: {skill_response.get('error')}")
            error_detail = skill_response.get("error", "Skill execution failed.")
            if skill_response.get("details"): error_detail += f" (Details: {skill_response.get('details')})"
            raise HTTPException(status_code=400, detail=error_detail)
    except HTTPException:
        raise
    except Exception:
        raise
    finally:
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        log_interaction(request_id=request_id, task_type=request.task_type, status=status, latency_ms=latency_ms, provider=provider, prompt=request.prompt, response_data=response_data)


# --- MODIFIED ENDPOINT ---
@app.get("/api/v1/analytics", response_model=AnalyticsResponse, summary="Get interaction records with pagination and filtering")
async def get_analytics_data(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    task_type: Optional[str] = Query(None, description="Filter records by a specific task_type")
):
    """
    Retrieves a paginated and optionally filtered list of interactions from the audit database.
    """
    try:
        records = get_all_interactions(limit=limit, offset=offset, task_type=task_type)
        total_matches = count_interactions(task_type=task_type)
        return AnalyticsResponse(
            total_matches=total_matches,
            limit=limit,
            offset=offset,
            data=records
        )
    except Exception as e:
        log.error(f"Failed to retrieve analytics data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve analytics data.")
# --- END MODIFIED ---

# ... (list_skills_capabilities and get_skill_capabilities endpoints are unchanged) ...
@app.get("/api/v1/skills", summary="List all available skills and their capabilities")
async def list_skills_capabilities():
    capabilities = {}
    for skill_name, skill_class in skill_manager.skills.items():
        try:
            skill_instance = skill_class() 
            capabilities[skill_name] = skill_instance.get_capabilities()
        except Exception as e:
            log.error(f"Error getting capabilities for skill {skill_name}: {e}", exc_info=True)
            capabilities[skill_name] = {"skill_name": skill_name, "error": "Could not retrieve capabilities."}
    return capabilities

@app.get("/api/v1/skills/{skill_name}/capabilities", summary="Get capabilities of a specific skill")
async def get_skill_capabilities(skill_name: str):
    skill_class = skill_manager.get_skill(skill_name)
    if not skill_class:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found.")
    try:
        skill_instance = skill_class() 
        return skill_instance.get_capabilities()
    except Exception as e:
        log.error(f"Error getting capabilities for skill {skill_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve skill capabilities.")