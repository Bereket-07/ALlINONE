from fastapi import APIRouter, HTTPException, status, Depends, Form, File, UploadFile
from typing import Optional, List
from src.domain.models.llm_selection import QueryResponse
from src.use_cases.route_query import route_unified_query_to_best_llm
from src.controllers.auth_controller import get_current_user

router = APIRouter(
    prefix="/api/v1",
    tags=["Query Routing"]
)

@router.post("/query", response_model=QueryResponse)
async def handle_query(
    query: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    current_user: dict = Depends(get_current_user),
    conversation_id: Optional[str] = Form(None)
):
    """
    Unified endpoint that receives a user query and/or files, routes to the best LLM, and returns the response.
    Supports three scenarios:
    1. Query only: text input
    2. Files only: uploads analyzed with default query
    3. Query + Files: both inputs used
    Requires Bearer token authentication.
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: User ID not found."
        )

    try:
        print(f"DEBUG - Received query: {query}")
        print(f"DEBUG - Received files: {[file.filename for file in files] if files else 'None'}")

        has_query = query and query.strip()
        has_files = files and len(files) > 0

        if not has_query and not has_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either query or files must be provided"
            )

        # Handle different scenarios
        if has_query and not has_files:
            # Scenario 1: Query only
            print("DEBUG - Processing query only")
            final_query = query
            final_files = None

        elif not has_query and has_files:
            # Scenario 2: Files only - use constant query for automatic insights
            print("DEBUG - Processing files only with auto insights")
            final_query = """Please provide a comprehensive analysis of this document including:
1. Document Summary - Brief overview of the main content
2. Key Topics & Themes - Main subjects and recurring themes
3. Important Information - Critical data, findings, or conclusions
4. Structure & Organization - How the document is organized
5. Key Takeaways - Most important points to remember
6. Actionable Items - Any tasks, recommendations, or next steps mentioned
7. Context & Significance - Why this document matters and its broader implications"""
            final_files = files

        else:
            # Scenario 3: Both query and files
            print("DEBUG - Processing both query and files")
            final_query = query
            final_files = files

        result = await route_unified_query_to_best_llm(final_query, final_files, user_id=user_id,conversation_id=conversation_id)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        # print(f"DEBUG - Final result: {result}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG - Exception occurred: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )
