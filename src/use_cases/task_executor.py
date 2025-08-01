# src/use_cases/task_executor.py

import logging
from fastapi import WebSocket
from typing import Dict, Any

from src.domain.models.task_tree import TaskTree, Subtask
from src.use_cases.composio_executor_service import ComposioExecutorService, ComposioAuthRequired
from src.infrastructure.firebase.firestore_service import FirestoreService
from composio import Action

logger = logging.getLogger(__name__)

async def execute_task_tree(user_id: str, task_tree: TaskTree, websocket: WebSocket):
    """
    Orchestrates the execution of a TaskTree, handling interactive auth via WebSocket.
    """
    logger.info(f"Starting execution for TaskTree ID: {task_tree.task_tree_id}")
    task_tree.status = "executing"
    FirestoreService.update_task_tree(task_tree.task_tree_id, {"status": "executing"})
    await websocket.send_json({
        "status": "executing",
        "message": "Plan is complete. Starting execution..."
    })

    composio_service = ComposioExecutorService(entity_id=user_id)
    
    # Store results from subtasks to be used in later subtasks (e.g., RESULT:...)
    execution_context = {}

    for i, subtask in enumerate(task_tree.subtasks):
        try:
            await execute_subtask(
                user_id=user_id,
                task_tree=task_tree,
                subtask=subtask,
                websocket=websocket,
                composio_service=composio_service,
                execution_context=execution_context
            )
            logger.info(f"Subtask '{subtask.subtask_name}' completed successfully.")
            await websocket.send_json({
                "status": "subtask_complete",
                "subtask_name": subtask.subtask_name,
                "detail": "Successfully executed."
            })

        except ComposioAuthRequired as e:
            logger.warning(f"Authentication required for {e.app_name}. Notifying client.")
            await websocket.send_json({
                "status": "auth_required",
                "app_name": e.app_name,
                "auth_url": e.auth_url,
                "message": f"Please authenticate with {e.app_name} to continue."
            })

            # Wait for the client to confirm authentication
            response = await websocket.receive_json()
            if response.get("event") == "auth_completed":
                logger.info("Client confirmed authentication. Retrying subtask.")
                composio_service.refresh_client()
                # Retry the same subtask
                await execute_subtask(
                    user_id, task_tree, subtask, websocket, composio_service, execution_context
                )
            else:
                raise Exception("User did not complete the authentication flow.")

        except Exception as e:
            logger.error(f"Failed to execute subtask '{subtask.subtask_name}': {e}", exc_info=True)
            task_tree.status = "failed"
            subtask.result = f"Error: {e}"
            FirestoreService.save_task_tree(user_id, task_tree.model_dump(), task_tree.task_tree_id)
            raise # Re-raise to be caught by the controller

    task_tree.status = "executed"
    FirestoreService.save_task_tree(user_id, task_tree.model_dump(), task_tree.task_tree_id)
    logger.info(f"TaskTree ID {task_tree.task_tree_id} executed successfully.")
    

async def execute_subtask(
    user_id: str,
    task_tree: TaskTree,
    subtask: Subtask,
    websocket: WebSocket,
    composio_service: ComposioExecutorService,
    execution_context: Dict[str, Any]
):
    """Handles the logic for a single subtask."""
    # Simple heuristic to map API to Composio App
    # This can be made more robust with an LLM call or a mapping dictionary
    app_name = subtask.api.split(" ")[0].upper().replace("API", "")
    
    # Check auth BEFORE doing anything else for this app
    await composio_service.check_and_handle_authentication(app_name)
    
    # Find the correct Composio action
    # This is a simplification; a real implementation would use an LLM to select
    # the best action from the list based on subtask_name.
    available_actions = await composio_service.get_actions_for_app(app_name)
    target_action: Action = find_best_action(subtask.function, available_actions)

    if not target_action:
        raise ValueError(f"Could not find a suitable Composio action for function '{subtask.function}'")

    # Resolve payload parameters (e.g., replace "RESULT:...")
    resolved_payload = resolve_payload(subtask.payload, execution_context)

    # Execute
    result = await composio_service.execute_action(target_action, resolved_payload)

    # Update subtask and context
    subtask.result = str(result) # Or a more detailed summary
    execution_context[subtask.function] = result # Store the full result for chaining

    # Persist progress
    FirestoreService.save_task_tree(user_id, task_tree.model_dump(), task_tree.task_tree_id)


def find_best_action(function_name: str, actions: list[Action]) -> Action | None:
    """
    Finds the best matching Composio Action.
    This is a simple implementation. An LLM could do this more intelligently.
    """
    # Exact match
    for action in actions:
        if action.name.lower().endswith(function_name.lower()):
            return action
    # Partial match
    for action in actions:
        if function_name.lower() in action.name.lower():
            return action
    return None


def resolve_payload(payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replaces placeholders like "RESULT:search_flights:flight_id" with actual values.
    """
    resolved = {}
    for key, value in payload.items():
        if isinstance(value, str) and value.startswith("RESULT:"):
            _, source_function, result_key = value.split(":")
            if source_function in context and result_key in context[source_function]:
                 resolved[key] = context[source_function][result_key]
            else:
                 raise ValueError(f"Could not resolve dependency: {value}")
        else:
            resolved[key] = value
    return resolved