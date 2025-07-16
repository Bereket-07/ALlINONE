from fastapi import APIRouter, HTTPException, status, Depends, Request, UploadFile
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
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Unified endpoint that receives a user query and/or files, routes to the best LLM, and returns the response.
    
    Supports three scenarios:
    1. JSON-only: {"query": "...", "files": "None"}
    2. FormData-only: files uploaded, no query (auto analysis prompt is used)
    3. FormData with query and files: both are used
    
    Requires Bearer token authentication.
    """

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: User ID not found."
        )

    try:
        content_type = request.headers.get("content-type", "")
        query = None
        files_to_process: Optional[List[UploadFile]] = None
        conversation_id = None

        # === multipart/form-data handling ===
        if "multipart/form-data" in content_type:
            form = await request.form()
            query = form.get("query")
            conversation_id = form.get("conversation_id")
            files = form.getlist("files")

            valid_files = []
            for file in files:
                if hasattr(file, "filename") and file.filename:
                    valid_files.append(file)
            files_to_process = valid_files if valid_files else None

        # === JSON handling ===
        elif "application/json" in content_type:
            body = await request.json()
            query = body.get("query")
            conversation_id = body.get("conversation_id")
            files_param = body.get("files", "None")
            if files_param != "None":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Files cannot be sent via JSON. Use FormData instead."
                )

        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only multipart/form-data or application/json are supported."
            )

        # === Validate inputs ===
        has_query = query and query.strip()
        has_files = files_to_process and len(files_to_process) > 0

        if not has_query and not has_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either query or files must be provided."
            )

        # === Scenario handling ===
        if has_query and not has_files:
            final_query = query
            final_files = None

        elif not has_query and has_files:
            final_query = """Please provide a comprehensive analysis of this document including:
1. Document Summary - Brief overview of the main content
2. Key Topics & Themes - Main subjects and recurring themes
3. Important Information - Critical data, findings, or conclusions
4. Structure & Organization - How the document is organized
5. Key Takeaways - Most important points to remember
6. Actionable Items - Any tasks, recommendations, or next steps mentioned
7. Context & Significance - Why this document matters and its broader implications"""
            final_files = files_to_process

        else:  # both query and files
            final_query = query
            final_files = files_to_process

        # === Route to LLM handler ===
        result = await route_unified_query_to_best_llm(
            final_query,
            final_files,
            user_id=user_id,
            conversation_id=conversation_id
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )
