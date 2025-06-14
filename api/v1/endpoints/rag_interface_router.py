# api/v1/endpoints/rag_interface_router.py
from fastapi import APIRouter, HTTPException, status, Depends
from core.license_manager import is_feature_enabled, Feature, get_current_license_tier, LicenseTier
from core.logger import log

router = APIRouter(
    prefix="/rag",
    tags=["RAG Interface (Enterprise)"]
)

async def verify_rag_access():
    """Dependency to check RAG interface access."""
    if not is_feature_enabled(Feature.RAG_INTERFACE):
        log.warning(f"RAG Interface access denied. Current tier: {get_current_license_tier().name}. Required: {LicenseTier.ENTERPRISE.name}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"RAG Interface feature is not available for your current license tier ({get_current_license_tier().name}). Please upgrade to Enterprise."
        )
    log.info("RAG Interface access granted for Enterprise tier.")

@router.post("/query", dependencies=[Depends(verify_rag_access)])
async def query_rag_interface(query: str):
    """
    Placeholder for querying the RAG interface. Enterprise Tier Only.
    """
    # ... In a real implementation, RAG query logic would go here ...
    return {"message": "RAG query processed successfully (Enterprise feature)", "received_query": query}

@router.get("/settings", dependencies=[Depends(verify_rag_access)])
async def get_rag_settings():
    """
    Placeholder for RAG interface settings. Enterprise Tier Only.
    """
    # ... In a real implementation, RAG settings logic would go here ...
    return {"settings": {"model": "advanced_rag_model_v2", "chunk_size": 512}, "message": "RAG settings retrieved (Enterprise feature)"}