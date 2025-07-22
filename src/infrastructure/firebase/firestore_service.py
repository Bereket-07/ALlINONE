import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone  # ✅ MERGED: Added timezone for consistency
import logging
import uuid

logger = logging.getLogger(__name__)

class FirestoreService:
    """
    ✅ MERGED: Service for all Firestore interactions, including user auth, 
    conversations, and Allin1 task trees.
    """
    
    _db: Optional[firestore.Client] = None
    _initialized = False
    
    @classmethod
    def initialize(cls, credentials_path: str) -> bool:
        """
        Initialize Firestore connection. (No changes from your original code)
        """
        if cls._initialized:
            logger.info("Firestore already initialized.")
            return True
            
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            
            cls._db = firestore.client()
            cls._initialized = True
            logger.info("Firestore client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            return False
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if Firestore is initialized. (No changes from your original code)"""
        return cls._initialized and cls._db is not None
    
    # --- Existing User Methods (Unchanged) ---
    @classmethod
    async def create_user(cls, user_data: Dict[str, Any]) -> bool:
        """Create a new user in Firestore users collection."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized")
            return False
        try:
            user_ref = cls._db.collection('users').document(user_data['uid'])
            user_ref.set(user_data)
            logger.info(f"User created in Firestore: {user_data['uid']}")
            return True
        except Exception as e:
            logger.error(f"Error creating user in Firestore: {e}")
            return False
    
    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address from users collection."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized")
            return None
        try:
            users_ref = cls._db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            docs = query.stream()
            for doc in docs:
                user_data = doc.to_dict()
                user_data['uid'] = doc.id
                return user_data
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    @classmethod
    async def get_user_by_uid(cls, uid: str) -> Optional[Dict[str, Any]]:
        """Get user by UID from users collection."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized")
            return None
        try:
            user_ref = cls._db.collection('users').document(uid)
            user_doc = user_ref.get()
            if not user_doc.exists:
                return None
            user_data = user_doc.to_dict()
            user_data['uid'] = uid
            return user_data
        except Exception as e:
            logger.error(f"Error getting user by UID: {e}")
            return None
    
    @classmethod
    async def update_user(cls, uid: str, updates: Dict[str, Any]) -> bool:
        """Update user data in users collection."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized")
            return False
        try:
            user_ref = cls._db.collection('users').document(uid)
            user_ref.update(updates)
            logger.info(f"User updated in Firestore: {uid}")
            return True
        except Exception as e:
            logger.error(f"Error updating user in Firestore: {e}")
            return False 

    # --- Existing Conversation Methods (Unchanged) ---
    @classmethod
    async def add_conversation_turn(cls, conversation_data: Dict[str, Any]) -> bool:
        """Adds a new conversation turn to the conversations collection."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized")
            return False
        if 'conversation_id' not in conversation_data:
            logger.error("conversation_id is required in conversation_data")
            return False
        try:
            doc_id = str(uuid.uuid4())
            conversation_data['created_at'] = datetime.now(timezone.utc)
            convo_ref = cls._db.collection('conversations').document(doc_id)
            convo_ref.set(conversation_data)
            logger.info(f"Conversation turn saved for user: {conversation_data.get('user_id')} in conversation: {conversation_data.get('conversation_id')}")
            return True
        except Exception as e:
            logger.error(f"Error saving conversation turn to Firestore: {e}")
            return False

    @classmethod
    async def get_last_n_conversations(cls, user_id: str, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves the last N conversation turns for a given user and conversation."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized")
            return []
        try:
            convo_ref = cls._db.collection('conversations')
            query = (convo_ref
                     .where('user_id', '==', user_id)
                     .where('conversation_id', '==', conversation_id)
                     .order_by('created_at', direction=firestore.Query.DESCENDING)
                     .limit(limit))
            docs = query.stream()
            history = [doc.to_dict() for doc in docs]
            history.reverse()
            return history
        except Exception as e:
            logger.error(f"Error getting conversation history for user {user_id} in conversation {conversation_id}: {e}")
            return []

    @classmethod
    def create_new_conversation_id(cls) -> str:
        """Generates a new unique conversation ID."""
        return str(uuid.uuid4())
    
    @classmethod
    async def create_conversation_session(cls, user_id: str, title: str = None) -> Optional[str]:
        """Creates a new conversation session document."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized")
            return None
        try:
            conversation_id = str(uuid.uuid4())
            session_data = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'created_at': datetime.now(timezone.utc),
                'title': title or "New Chat"
            }
            session_ref = cls._db.collection('conversation_sessions').document(conversation_id)
            session_ref.set(session_data)
            logger.info(f"Created new conversation session {conversation_id} for user {user_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"Error creating conversation session: {e}")
            return None

    @classmethod
    async def get_last_n_conversation_sessions(cls, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves the last N conversation sessions for a user."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized")
            return []
        try:
            sessions_ref = cls._db.collection('conversation_sessions')
            query = (sessions_ref
                     .where('user_id', '==', user_id)
                     .order_by('created_at', direction=firestore.Query.DESCENDING)
                     .limit(limit))
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Error getting conversation sessions for user {user_id}: {e}")
            return []

    # --- ✅ MERGED: NEW METHOD FOR ALLIN1 TASK TREES ---
    @classmethod
    async def save_task_tree(cls, user_id: str, task_tree_data: Dict[str, Any]) -> Optional[str]:
        """
        Saves a generated Allin1 task tree to the 'task_trees' collection.
        """
        if not cls.is_initialized():
            logger.error("Firestore not initialized, cannot save task tree.")
            return None
        
        try:
            document_data = {
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc),
                **task_tree_data
            }
            update_time, doc_ref =  cls._db.collection('task_trees').add(document_data)
            logger.info(f"Successfully saved task tree {doc_ref.id} for user {user_id}")
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"Error saving task tree to Firestore for user {user_id}: {e}")
            return None
    @classmethod
    async def get_task_tree(cls, task_tree_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific task tree by its ID."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized, cannot get task tree.")
            return None
        try:
            doc_ref = cls._db.collection('task_trees').document(task_tree_id)
            doc = await doc_ref.get() # Use await for async get
            if doc.exists:
                data = doc.to_dict()
                data['task_tree_id'] = doc.id # Ensure ID is included
                return data
            logger.warning(f"Task tree with ID {task_tree_id} not found.")
            return None
        except Exception as e:
            logger.error(f"Error getting task tree {task_tree_id}: {e}")
            return None

    @classmethod
    async def update_task_tree(cls, task_tree_id: str, updates: Dict[str, Any]) -> bool:
        """Updates an existing task tree document in Firestore."""
        if not cls.is_initialized():
            logger.error("Firestore not initialized, cannot update task tree.")
            return False
        try:
            doc_ref = cls._db.collection('task_trees').document(task_tree_id)
            updates['updated_at'] = datetime.now(timezone.utc)
            await doc_ref.update(updates) # Use await for async update
            logger.info(f"Successfully updated task tree {task_tree_id}.")
            return True
        except Exception as e:
            logger.error(f"Error updating task tree {task_tree_id} in Firestore: {e}")
            return False