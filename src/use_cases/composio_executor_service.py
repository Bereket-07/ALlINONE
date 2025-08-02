import asyncio
import logging
from typing import Dict, Any, List, Optional

from composio.client import Composio as ComposioToolSet
# ✅ FIX 1: The import for Composio is slightly redundant but okay. The main fix is deleting the ConnectedAccount import.
from composio import Composio
from composio.client.enums import App, Action
# ❌ DELETE THIS LINE: from composio.client import ConnectedAccount  # This is the source of the error
from composio.exceptions import InvalidParams

logger = logging.getLogger(__name__)

# --- NEW EXCEPTION FOR API KEYS ---
class ComposioApiKeyRequired(Exception):
    """Custom exception to signal that an API key is needed from the user."""
    def __init__(self, app_name: str, required_keys: list[str], message="API Key is required."):
        self.app_name = app_name
        self.required_keys = required_keys
        self.message = message
        super().__init__(self.message)
        
class ComposioAuthRequired(Exception):
    def __init__(self, app_name: str, auth_url: str, message="Authentication is required."):
        self.app_name = app_name
        self.auth_url = auth_url
        self.message = message
        super().__init__(self.message)

class ComposioExecutorService:
    # This __init__ needs to be present for self.toolset and self.entity_id
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.toolset = ComposioToolSet()

    def refresh_client(self):
        """Refreshes the Composio client."""
        logger.info("Refreshing Composio client...")
        self.toolset = ComposioToolSet()

    # --- THE MODIFIED FUNCTION ---
    async def check_and_handle_authentication(
        self,
        app_name: str,
        api_key_params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Checks app authentication.
        - If already connected, returns True.
        - If OAuth is needed, raises ComposioAuthRequired.
        - If an API Key is needed, raises ComposioApiKeyRequired.
        - If API key is provided, attempts to connect.
        """
        logger.info(f"Checking authentication for app: {app_name}")
        
        # ✅ THE FINAL FIX: Use the correct method name from the reference script.
        connected_accounts: List[Any] = await asyncio.to_thread(lambda: self.toolset.connected_accounts.list)

        # This logic should now work correctly, as it matches the original script's intent.
        if any(acc.app.value.upper() == app_name.upper() for acc in connected_accounts):
            logger.info(f"App '{app_name}' is already authenticated.")
            return True

        logger.warning(f"App '{app_name}' is not authenticated. Determining auth method.")
        app_enum = getattr(App, app_name.upper(), None)
        if not app_enum:
            raise ValueError(f"App '{app_name}' is not a valid Composio App.")

        try:
            oauth_request = await asyncio.to_thread(
                lambda: self.toolset.initiate_connection(
                    app=app_enum,
                    entity_id=self.entity_id,
                    connected_account_params=api_key_params or {}
                )
            )
            if api_key_params:
                 logger.info(f"Successfully connected to {app_name} using provided API key.")
                 return True
            
            if not oauth_request or not hasattr(oauth_request, 'redirectUrl'):
                raise ConnectionError(f"Failed to generate OAuth URL for {app_name}.")
            
            raise ComposioAuthRequired(app_name=app_name, auth_url=oauth_request.redirectUrl)

        except InvalidParams as e:
            error_str = str(e).lower()
            if 'connected_account_params' in error_str and 'generic_api_key' in error_str:
                logger.info(f"{app_name} requires an API key. Raising challenge.")
                raise ComposioApiKeyRequired(app_name=app_name, required_keys=['generic_api_key'])
            else:
                raise e

        except InvalidParams as e:
            error_str = str(e).lower()
            if 'connected_account_params' in error_str and 'generic_api_key' in error_str:
                logger.info(f"{app_name} requires an API key. Raising challenge.")
                raise ComposioApiKeyRequired(app_name=app_name, required_keys=['generic_api_key'])
            else:
                raise e
    
    # --- The rest of the methods should be okay ---

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