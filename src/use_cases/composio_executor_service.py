# src/use_cases/composio_executor_service.py

import asyncio
import logging
from typing import Dict, Any, List, Optional
from composio import ComposioToolSet, App, Action

logger = logging.getLogger(__name__)

class ComposioAuthRequired(Exception):
    """Custom exception to signal that OAuth is needed."""
    def __init__(self, app_name: str, auth_url: str, message="Authentication is required."):
        self.app_name = app_name
        self.auth_url = auth_url
        self.message = message
        super().__init__(self.message)

class ComposioExecutorService:
    """
    A service to orchestrate Composio actions, refactored for server-side use.
    It returns data and raises specific exceptions instead of using print/input.
    """
    def __init__(self, entity_id: str = "default"):
        self.entity_id = entity_id
        self.toolset = ComposioToolSet(entity_id=self.entity_id)

    def refresh_client(self):
        """Re-initializes the toolset to pick up new authentications."""
        logger.info("Refreshing Composio toolset to detect new authentications.")
        self.toolset = ComposioToolSet(entity_id=self.entity_id)

    async def check_and_handle_authentication(self, app_name: str) -> bool:
        """
        Checks if an app is authenticated. If not, raises ComposioAuthRequired.
        Returns True if already authenticated.
        """
        logger.info(f"Checking authentication for app: {app_name}")
        connected_accounts = await asyncio.to_thread(self.toolset.get_connected_accounts)
        
        app_is_connected = any(
            (hasattr(acc, 'appName') and acc.appName.upper() == app_name.upper()) or
            (hasattr(acc, 'app') and str(acc.app).upper() == app_name.upper())
            for acc in connected_accounts
        )

        if app_is_connected:
            logger.info(f"App '{app_name}' is already authenticated.")
            return True

        logger.warning(f"App '{app_name}' is not authenticated. Raising auth challenge.")
        app_enum = getattr(App, app_name.upper(), None)
        if not app_enum:
            raise ValueError(f"App '{app_name}' is not a valid Composio App.")

        # This will be caught by the orchestrator and sent to the user
        oauth_request = await asyncio.to_thread(
            lambda: self.toolset.initiate_connection(
                app=app_enum,
                entity_id=self.entity_id
            )
        )
        if not oauth_request or not hasattr(oauth_request, 'redirectUrl'):
            raise ConnectionError(f"Failed to generate OAuth URL for {app_name}.")
            
        raise ComposioAuthRequired(app_name=app_name, auth_url=oauth_request.redirectUrl)

    async def get_actions_for_app(self, app_name: str) -> List[Action]:
        """Fetches available actions for a given app."""
        logger.info(f"Fetching actions for app: {app_name}")
        app_enum = getattr(App, app_name.upper(), None)
        if not app_enum:
            raise ValueError(f"App '{app_name}' is not a valid Composio App.")
        
        actions = await asyncio.to_thread(lambda: list(app_enum.get_actions()))
        logger.info(f"Found {len(actions)} actions for {app_name}.")
        return actions

    async def get_action_schema(self, action: Action) -> Dict[str, Any]:
        """Fetches the schema for a single, specific action."""
        logger.info(f"Fetching schema for action: {action.name}")
        schema_list = await asyncio.to_thread(
            lambda: self.toolset.get_action_schemas(actions=[action])
        )
        if not schema_list:
            raise ValueError(f"Could not retrieve schema for action {action.name}")
        return schema_list[0]

    async def execute_action(self, action: Action, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a Composio action with the given parameters."""
        logger.info(f"Executing action '{action.name}' with params: {params}")
        try:
            result = await asyncio.to_thread(
                lambda: self.toolset.execute_action(
                    action=action,
                    params=params,
                    entity_id=self.entity_id
                )
            )
            logger.info(f"Action '{action.name}' executed successfully.")
            return result
        except Exception as e:
            logger.error(f"Execution of action '{action.name}' failed: {e}", exc_info=True)
            raise