# api/server.py
import time
import uuid
# --- MODIFIED: Import Query for endpoint parameters ---
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
# --- NEW IMPORTS FOR GUI ---
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse # Added FileResponse
from typing import Dict, Any, Optional, List

from core.logger import log
from core.skill_manager import skill_manager
from core.model_router import model_router, NoAvailableProviderError
from core.audit_logger import (
    log_interaction, 
    get_all_interactions, 
    count_interactions,
    get_tasks_over_time_data,
    get_requests_per_provider_data,
    get_average_latency_per_provider_data)
from core.provider_manager import provider_manager, PROVIDERS_CONFIG_PATH # Import provider_manager
from pathlib import Path
import yaml # For reading providers.yaml

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

# --- NEW: System Status Models ---
class ProviderStatus(BaseModel):
    name: str
    status: str # e.g., "Active", "Disabled", "Error"
    details: Optional[str] = None

class SystemStatusResponse(BaseModel):
    providers_status: List[ProviderStatus]

# --- NEW: Chart Data Models ---
class TasksOverTimeDataPoint(BaseModel):
    date_group: str # e.g., "YYYY-MM-DD" or "YYYY-MM"
    count: int

class RequestsPerProviderDataPoint(BaseModel):
    provider_name: str
    count: int

class AverageLatencyDataPoint(BaseModel):
    provider_name: str
    average_latency: float # Can be float due to AVG
# --- END NEW SYSTEM STATUS MODELS ---

# --- END MODIFIED ---

app = FastAPI(
    title="Praximous API",
    version="1.0-mvp",
    description="Secure, On-Premise AI Gateway"
)

# --- API ENDPOINTS MUST BE DEFINED BEFORE THE CATCH-ALL STATIC FILE SERVING ---

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
            status = "error" # Ensure status is marked as error for logging
            error_detail = skill_response.get("error", "Skill execution failed.")
            if skill_response.get("details"): error_detail += f" (Details: {skill_response.get('details')})"
            # Return a ProcessResponse with error status instead of raising HTTPException for skill-specific failures
            return ProcessResponse(status=status, message=error_detail, request_id=request_id)
    except HTTPException:
        status = "error" # Explicitly mark status for logging on known HTTP exceptions
        raise
    except Exception as e: # Catch any other unexpected errors
        log.error(f"API: [ReqID: {request_id}] Unhandled exception in process_task: {e}", exc_info=True)
        status = "error" # Explicitly mark status for logging
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")

    finally:
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        log_interaction(request_id=request_id, task_type=request.task_type, status=status, latency_ms=latency_ms, provider=provider, prompt=request.prompt, response_data=response_data)


@app.get("/api/v1/analytics", response_model=AnalyticsResponse, summary="Get interaction records with pagination and filtering")
async def get_analytics_data(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    task_type: Optional[str] = Query(None, description="Filter records by a specific task_type"),
    start_date: Optional[str] = Query(None, description="Filter records from this date (YYYY-MM-DD)", regex="^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, description="Filter records up to this date (YYYY-MM-DD)", regex="^\d{4}-\d{2}-\d{2}$"),
    sort_by: Optional[str] = Query("timestamp", description="Column to sort by (e.g., timestamp, task_type, status, latency_ms)"),
    sort_order: Optional[str] = Query("desc", description="Sort order: 'asc' or 'desc'")
):
    # ... (implementation of get_analytics_data remains the same)
    """
    Retrieves a paginated and optionally filtered list of interactions from the audit database.
    """
    try:
        records = get_all_interactions(
            limit=limit, offset=offset, task_type=task_type, 
            start_date=start_date, end_date=end_date,
            sort_by=sort_by, sort_order=sort_order or "desc"
        )
        total_matches = count_interactions(
            task_type=task_type, 
            start_date=start_date, 
            end_date=end_date
        )
        return AnalyticsResponse(
            total_matches=total_matches,
            limit=limit,
            offset=offset,
            data=records
        )
    except Exception as e:
        log.error(f"Failed to retrieve analytics data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve analytics data.")

@app.get("/api/v1/system-status", response_model=SystemStatusResponse, summary="Get the status of configured LLM providers")
async def get_system_status():
    # ... (implementation of get_system_status remains the same)
    provider_statuses: List[ProviderStatus] = []
    try:
        with open(PROVIDERS_CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)

        if config and 'providers' in config and isinstance(config['providers'], list):
            for provider_config_entry in config['providers']:
                if not isinstance(provider_config_entry, dict):
                    continue
                
                name = provider_config_entry.get('name')
                if not name:
                    continue

                is_enabled_in_config = provider_config_entry.get("enabled", True) # Default to True if 'enabled' key is missing
                
                if not is_enabled_in_config:
                    provider_statuses.append(ProviderStatus(name=name, status="Disabled", details="Disabled in configuration."))
                else:
                    # Check if the provider was successfully initialized by ProviderManager
                    if provider_manager.get_provider(name):
                        provider_statuses.append(ProviderStatus(name=name, status="Active", details="Initialized and active."))
                    else:
                        # Enabled in config but not found in initialized providers means an initialization error occurred
                        provider_statuses.append(ProviderStatus(name=name, status="Error", details="Failed to initialize (e.g., missing API key or configuration issue). Check server logs."))
        else:
            log.warning("providers.yaml not found or improperly formatted for system status check.")

    except Exception as e:
        log.error(f"Error fetching system status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve system status.")
    return SystemStatusResponse(providers_status=provider_statuses)

@app.get("/api/v1/analytics/charts/tasks-over-time", response_model=List[TasksOverTimeDataPoint], summary="Get data for tasks over time chart")
async def get_chart_tasks_over_time(
    start_date: Optional[str] = Query(None, description="Filter records from this date (YYYY-MM-DD)", regex="^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, description="Filter records up to this date (YYYY-MM-DD)", regex="^\d{4}-\d{2}-\d{2}$"),
    granularity: str = Query("day", description="Granularity of time grouping: 'day', 'month', 'year'")
):
    # ... (implementation remains the same)
    try:
        if granularity not in ["day", "month", "year"]:
            raise HTTPException(status_code=400, detail="Invalid granularity. Must be 'day', 'month', or 'year'.")
        data = get_tasks_over_time_data(start_date=start_date, end_date=end_date, granularity=granularity)
        return data
    except Exception as e:
        log.error(f"Failed to retrieve tasks over time chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve tasks over time chart data.")

@app.get("/api/v1/analytics/charts/requests-per-provider", response_model=List[RequestsPerProviderDataPoint], summary="Get data for requests per provider chart")
async def get_chart_requests_per_provider(
    start_date: Optional[str] = Query(None, description="Filter records from this date (YYYY-MM-DD)", regex="^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, description="Filter records up to this date (YYYY-MM-DD)", regex="^\d{4}-\d{2}-\d{2}$")
):
    # ... (implementation remains the same)
    try:
        data = get_requests_per_provider_data(start_date=start_date, end_date=end_date)
        return data
    except Exception as e:
        log.error(f"Failed to retrieve requests per provider chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve requests per provider chart data.")

@app.get("/api/v1/analytics/charts/average-latency-per-provider", response_model=List[AverageLatencyDataPoint], summary="Get data for average latency per provider chart")
async def get_chart_average_latency_per_provider(
    start_date: Optional[str] = Query(None, description="Filter records from this date (YYYY-MM-DD)", regex="^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, description="Filter records up to this date (YYYY-MM-DD)", regex="^\d{4}-\d{2}-\d{2}$")
):
    # ... (implementation remains the same)
    try:
        data = get_average_latency_per_provider_data(start_date=start_date, end_date=end_date)
        return data
    except Exception as e:
        log.error(f"Failed to retrieve average latency per provider chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve average latency per provider chart data.")

@app.get("/api/v1/skills", summary="List all available skills and their capabilities")
async def list_skills_capabilities():
    # ... (implementation remains the same)
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
    # ... (implementation remains the same)
    skill_class = skill_manager.get_skill(skill_name)
    if not skill_class:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found.")
    try:
        skill_instance = skill_class() 
        return skill_instance.get_capabilities()
    except Exception as e:
        log.error(f"Error getting capabilities for skill {skill_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve skill capabilities.")

# --- NEW: Configuration Viewing Endpoints ---
@app.get("/api/v1/config/providers", response_model=str, summary="Get the content of providers.yaml")
async def get_providers_config_content():
    try:
        if not PROVIDERS_CONFIG_PATH.is_file():
            raise HTTPException(status_code=404, detail="providers.yaml not found.")
        with open(PROVIDERS_CONFIG_PATH, 'r') as f:
            content = f.read()
        return content
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error reading providers.yaml: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not read provider configuration file.")
# --- END API ENDPOINTS ---

# --- UPDATED: Setup for serving the React GUI ---
# Determine the project root directory relative to this file (api/server.py)
# server.py -> api -> project_root
PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
REACT_APP_BUILD_DIR = PROJECT_ROOT_DIR / "frontend-react" / "dist"

# Serve static assets (JS, CSS, images) from the React app's build output.
# Vite typically places these in an 'assets' subfolder within 'dist'.
# Adjust the path if your Vite build configuration is different.
if (REACT_APP_BUILD_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=(REACT_APP_BUILD_DIR / "assets")), name="react-assets")
else:
    log.warning(f"React assets directory not found at {REACT_APP_BUILD_DIR / 'assets'}. GUI may not load correctly.")

# Serve the main index.html for any other GET request that doesn't match an API route.
# This allows client-side routing in the React app to function correctly.
@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def serve_react_app(full_path: str):
    index_html_path = REACT_APP_BUILD_DIR / "index.html"
    # Attempt to serve a static file if full_path points to an existing file in the build directory
    # e.g., /vite.svg should serve REACT_APP_BUILD_DIR/vite.svg
    potential_static_file = (REACT_APP_BUILD_DIR / full_path.lstrip("/")).resolve()

    # Security check: ensure the resolved path is still within REACT_APP_BUILD_DIR
    if potential_static_file.is_file() and str(potential_static_file).startswith(str(REACT_APP_BUILD_DIR.resolve())):
        # Let FileResponse guess the media type based on the file extension
        return FileResponse(potential_static_file)

    # Fallback to serving index.html for SPA routing if no specific file matched
    if not index_html_path.is_file():
        log.error(f"React app index.html not found at {index_html_path}. Ensure the React app is built.")
        return HTMLResponse(content="Praximous React App not found. Please build the frontend application.", status_code=404)
    return FileResponse(index_html_path) # Serve index.html using FileResponse
# --- END UPDATED REACT GUI SETUP ---