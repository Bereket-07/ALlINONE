from fastapi import APIRouter, HTTPException, status, Depends, Form, File, UploadFile, Request
from typing import Optional, List, Union
from src.domain.models.llm_selection import QueryResponse, QueryRequest
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
    1. Query only: JSON with files: "None" 
    2. Files only: FormData with files, processes with automatic insights query
    3. Query + Files: FormData with both query and files
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
        
        # Debug prints
        print(f"DEBUG - Content-Type: {content_type}")
        
        query = None
        files_to_process = None
        
        if "multipart/form-data" in content_type:
            # Handle FormData (files present)
            form = await request.form()
            query = form.get("query")
            files = form.getlist("files")
            
            print(f"DEBUG - FormData query: {query}")
            print(f"DEBUG - FormData files: {files}")
            print(f"DEBUG - Files length: {len(files) if files else 0}")
            
            # Process files
            valid_files = []
            for file in files:
                if hasattr(file, 'filename') and file.filename:
                    valid_files.append(file)
                    print(f"DEBUG - Valid file: {file.filename}")
            
            files_to_process = valid_files if valid_files else None
            
        else:
            # Handle JSON (text-only with files: "None")
            body = await request.json()
            query = body.get("query")
            files_param = body.get("files")
            
            print(f"DEBUG - JSON query: {query}")
            print(f"DEBUG - JSON files param: {files_param}")
            
            # files should be "None" for text-only queries
            if files_param != "None":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="For JSON requests, files parameter should be 'None'"
                )
        
        # Determine the scenario
        has_query = query and query.strip()
        has_files = files_to_process and len(files_to_process) > 0
        
        print(f"DEBUG - Has query: {has_query}")
        print(f"DEBUG - Has files: {has_files}")
        
        # Validate scenarios
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
            final_files = files_to_process
            
        else:
            # Scenario 3: Both query and files
            print("DEBUG - Processing both query and files")
            final_query = query
            final_files = files_to_process
        
        # Route to unified handler
        result = await route_unified_query_to_best_llm(final_query, final_files, user_id=user_id)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        print(f"DEBUG - Final result: {result}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"DEBUG - Exception occurred: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )

