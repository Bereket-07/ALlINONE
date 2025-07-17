import logging
from fastapi import APIRouter, HTTPException, status, Depends, Body
from pydantic import BaseModel

from src.controllers.auth_controller import get_current_user
from src.use_cases.planner_agent import generate_task_tree
from src.domain.models.task_tree import TaskTree
from src.infrastructure.firebase.firestore_service import FirestoreService

# Create a new router for Allin1 specific functions
router = APIRouter(
    prefix="/api/v1/allin1",
    tags=["Allin1 - Task Orchestration"]
)

logger = logging.getLogger(__name__)

# This class defines the expected JSON body for the /execute endpoint
class QueryRequest(BaseModel):
    query: str

@router.post("/execute", response_model=TaskTree)
async def execute_task_plan(
    request_body: QueryRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Receives a user query, generates a task tree, saves it, and returns it.
    """
    user_id = current_user.get("sub")
    user_query = request_body.query

    if not user_query or not user_query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty."
        )

    try:
        # 1. Generate the task tree using the Planner Agent (This part is working!)
        task_tree = await generate_task_tree(user_query)

        # 2. Save the generated task tree to Firebase.
        # ✅ FIXED: Changed the method call to the correct 'save_task_tree' method
        # that exists in your merged FirestoreService class.
        task_tree_id = await FirestoreService.save_task_tree(
            user_id=user_id,
            task_tree_data=task_tree.model_dump()
        )
        
        if not task_tree_id:
            # Handle the case where saving to Firestore failed
            logger.error("Failed to save task tree to Firestore. The task will proceed without a saved ID.")
        
        task_tree.task_tree_id = task_tree_id  # Add the saved ID to the response model

        # 3. Return the complete plan to the frontend
        return task_tree

    except ValueError as e:
        # This error comes from the planner_agent if it fails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate a valid task plan: {str(e)}"
        )
    except Exception as e:
        # This is a general catch-all for other unexpected errors
        logger.error(f"An unexpected error occurred in /execute endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred while processing the task plan."
        )