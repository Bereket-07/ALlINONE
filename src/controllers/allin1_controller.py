import logging
from fastapi import (
    APIRouter, HTTPException, status, Depends, Body, WebSocket, WebSocketDisconnect
)
from pydantic import BaseModel

from src.controllers.auth_controller import get_current_user
from src.use_cases.planner_agent import generate_task_tree
# Import the new generator-based use case
from src.use_cases.information_gatherer import interactive_information_gathering_loop
from src.use_cases.task_executor import execute_task_tree 
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
async def websocket_gather_info_and_execute(websocket: WebSocket, task_tree_id: str):
    """
    WebSocket endpoint for a full task lifecycle:
    1. Interactively gathers missing information.
    2. Triggers and manages task execution.
    3. Handles interactive authentication for execution.
    """
    await websocket.accept()
    
    user_id = "17ad8405-6035-46be-9662-c805ac844977" # Replace with real user from token

    try:
        task_tree_dict = FirestoreService.get_task_tree(task_tree_id)
        if not task_tree_dict:
            # ... (handle not found)
            return
        if task_tree_dict.get("user_id") != user_id:
            # ... (handle access denied)
            return

        task_tree = TaskTree(**task_tree_dict)

        # --- STAGE 1: INFORMATION GATHERING ---
        if task_tree.status in ["pending", "in_progress"]:
            logger.info(f"Starting information gathering for task: {task_tree_id}")
            info_gatherer = interactive_information_gathering_loop(user_id, task_tree)
            
            question_to_ask = None
            try:
                question_to_ask = await info_gatherer.asend(None)
            except StopAsyncIteration:
                logger.info(f"No information gathering needed for task {task_tree_id}.")
                pass

            while question_to_ask:
                await websocket.send_json(question_to_ask)
                answer_data = await websocket.receive_json()
                user_answer = answer_data.get("answer")
                
                if user_answer is None:
                    # ... (handle invalid format)
                    continue
                
                try:
                    question_to_ask = await info_gatherer.asend(user_answer)
                except StopAsyncIteration:
                    logger.info(f"Information gathering complete for task {task_tree_id}.")
                    question_to_ask = None
        
        # At this point, task_tree is fully populated and its status is 'completed'.

        # --- STAGE 2: EXECUTION ---
        logger.info(f"Proceeding to execution phase for task: {task_tree_id}")
        # The execute_task_tree function will now handle all further communication
        await execute_task_tree(
            user_id=user_id,
            task_tree=task_tree,
            websocket=websocket
        )

        # Send final success message after execution
        await websocket.send_json({
            "status": "executed",
            "message": "Task workflow has been successfully executed.",
            "final_plan": task_tree.model_dump()
        })

    except WebSocketDisconnect:
        logger.warning(f"WebSocket disconnected for task {task_tree_id}.")
    except Exception as e:
        logger.error(f"Error in WebSocket lifecycle for task {task_tree_id}: {e}", exc_info=True)
        if not websocket.client_state == 'DISCONNECTED':
            await websocket.send_json({
                "status": "failed",
                "error": "An internal server error occurred during the workflow.",
                "detail": str(e)
            })
    finally:
        if not websocket.client_state == 'DISCONNECTED':
            await websocket.close()