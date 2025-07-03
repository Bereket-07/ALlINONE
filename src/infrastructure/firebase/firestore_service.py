import firebase_admin
from firebase_admin import firestore
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FirestoreService:
    """
    Simple Firestore service for user storage.
    """
    
    _db: Optional[firestore.Client] = None
    _initialized = False
    
    @classmethod
    def initialize(cls, credentials_path: str) -> bool:
        """
        Initialize Firestore connection.
        """
        try:
            if not firebase_admin._apps:
                cred = firebase_admin.credentials.Certificate(credentials_path)
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
        """Check if Firestore is initialized."""
        return cls._initialized and cls._db is not None
    
    @classmethod
    async def create_user(cls, user_data: Dict[str, Any]) -> bool:
        """
        Create a new user in Firestore users collection.
        """
        if not cls.is_initialized():
            logger.error("Firestore not initialized")
            return False
        
        try:
            # Store user in users collection
            user_ref = cls._db.collection('users').document(user_data['uid'])
            user_ref.set(user_data)
            
            logger.info(f"User created in Firestore: {user_data['uid']}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user in Firestore: {e}")
            return False
    
    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address from users collection.
        """
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
        """
        Get user by UID from users collection.
        """
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
        """
        Update user data in users collection.
        """
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