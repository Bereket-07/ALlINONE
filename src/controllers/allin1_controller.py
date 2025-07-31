import logging
from fastapi import (
    APIRouter, HTTPException, status, Depends, Body, WebSocket, WebSocketDisconnect
)
from pydantic import BaseModel

from src.controllers.auth_controller import get_current_user
from src.use_cases.planner_agent import generate_task_tree
# Import the new generator-based use case
from src.use_cases.information_gatherer import interactive_information_gathering_loop
from src.domain.models.task_tree import TaskTree
from src.infrastructure.firebase.firestore_service import FirestoreService

router = APIRouter(
    prefix="/api/v1",
    tags=["Allin1 - Task Orchestration"]
)

logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    query: str

@router.post("/tasks", response_model=TaskTree, status_code=status.HTTP_201_CREATED)
async def create_task_plan(
    request_body: QueryRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Receives a user query, generates a task tree (plan), and saves it.
    This is the entry point. The frontend should use the returned task_tree_id
    to connect to the WebSocket for the interactive follow-up.
    """
    user_id = current_user.get("sub")
    # ... (the rest of your existing create_task_plan logic remains the same) ...
    try:
        task_tree = await generate_task_tree(request_body.query)
        task_tree_id = await FirestoreService.save_task_tree(
            user_id=user_id,
            task_tree_data=task_tree.model_dump()
        )
        task_tree.task_tree_id = task_tree_id
        return task_tree
    except Exception as e:
        logger.error(f"Failed to create task plan: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create a valid task plan.")


# In src/controllers/allin1_controller.py

@router.websocket("/ws/tasks/{task_tree_id}/gather")
async def websocket_gather_info(websocket: WebSocket, task_tree_id: str):
    """
    WebSocket endpoint for interactively gathering missing task information.
    """
    await websocket.accept()
    
    # In a real app, you would get this from a JWT in the WebSocket connection
    user_id = "17ad8405-6035-46be-9662-c805ac844977" # Using your example UID

    try:
        # --- FIX 1: Call get_task_tree with only the required argument ---
        # The method in FirestoreService only needs the task_tree_id to find the document.
        print(f"Fetching task tree with ID: {task_tree_id}")
        task_tree_dict = FirestoreService.get_task_tree(task_tree_id)
        
        if not task_tree_dict:
            await websocket.send_json({"error": "Task not found."})
            await websocket.close()
            return
        
        # --- FIX 2: Add a crucial security check ---
        # Verify that the user connected to the WebSocket is the owner of this task.
        if task_tree_dict.get("user_id") != user_id:
            logger.warning(f"Security alert: User {user_id} attempted to access task {task_tree_id} owned by {task_tree_dict.get('user_id')}")
            await websocket.send_json({"error": "Access denied."})
            await websocket.close()
            return

        # Now that we have the validated data, create the Pydantic model
        task_tree = TaskTree(**task_tree_dict)

        # The rest of the function proceeds as before...
        info_gatherer = interactive_information_gathering_loop(user_id, task_tree)
        question_to_ask = await info_gatherer.asend(None)

        while question_to_ask:
            await websocket.send_json(question_to_ask)
            answer_data = await websocket.receive_json()
            user_answer = answer_data.get("answer")
            if user_answer is None:
                await websocket.send_json({"error": "Invalid response format. 'answer' key is required."})
                continue
            question_to_ask = await info_gatherer.asend(user_answer)

        await websocket.send_json({
            "status": "completed",
            "message": "All information has been gathered.",
            "final_plan": task_tree.model_dump()
        })

    except WebSocketDisconnect:
        logger.warning(f"WebSocket disconnected for task {task_tree_id}.")
    except Exception as e:
        logger.error(f"Error in WebSocket for task {task_tree_id}: {e}", exc_info=True)
        if not websocket.client_state == 'DISCONNECTED':
            await websocket.send_json({"error": "An internal server error occurred."})
    finally:
        if not websocket.client_state == 'DISCONNECTED':
            await websocket.close()