from fastapi import APIRouter, HTTPException, status, Depends
from src.domain.models.llm_selection import QueryRequest, QueryResponse
from src.use_cases.route_query import route_query_to_best_llm
from src.controllers.auth_controller import get_current_user

router = APIRouter(
    prefix="/api/v1",
    tags=["Query Routing"]
)

@router.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest, current_user: dict = Depends(get_current_user)):
    """
    Receives a user query, routes it to the best LLM, and returns the response.
    Requires Bearer token authentication.
    """
    result = await route_query_to_best_llm(request.query)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result