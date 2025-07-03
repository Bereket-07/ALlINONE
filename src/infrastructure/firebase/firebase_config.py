import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_admin.exceptions import FirebaseError
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseConfig:
    """
    Firebase configuration and initialization class.
    Handles Firebase Admin SDK setup and provides access to Firebase services.
    """
    
    def __init__(self):
        self._app = None
        self._db = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize Firebase Admin SDK with service account credentials.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Get Firebase credentials path from environment
            credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            
            if not credentials_path:
                logger.error("FIREBASE_CREDENTIALS_PATH not found in environment variables")
                return False
                
            if not os.path.exists(credentials_path):
                logger.error(f"Firebase credentials file not found at: {credentials_path}")
                return False
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(credentials_path)
            self._app = firebase_admin.initialize_app(cred)
            
            # Initialize Firestore
            self._db = firestore.client()
            
            self._initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
            return True
            
        except FirebaseError as e:
            logger.error(f"Firebase initialization error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during Firebase initialization: {e}")
            return False
    
    @property
    def is_initialized(self) -> bool:
        """Check if Firebase is initialized."""
        return self._initialized
    
    @property
    def app(self):
        """Get Firebase app instance."""
        if not self._initialized:
            raise RuntimeError("Firebase not initialized. Call initialize() first.")
        return self._app
    
    @property
    def db(self):
        """Get Firestore database instance."""
        if not self._initialized:
            raise RuntimeError("Firebase not initialized. Call initialize() first.")
        return self._db
    
    def get_collection(self, collection_name: str):
        """
        Get a Firestore collection reference.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            CollectionReference: Firestore collection reference
        """
        if not self._initialized:
            raise RuntimeError("Firebase not initialized. Call initialize() first.")
        return self._db.collection(collection_name)
    
    def verify_token(self, id_token: str) -> Optional[dict]:
        """
        Verify Firebase ID token and return user info.
        
        Args:
            id_token (str): Firebase ID token
            
        Returns:
            dict: User information if token is valid, None otherwise
        """
        try:
            if not self._initialized:
                raise RuntimeError("Firebase not initialized. Call initialize() first.")
            
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
            
        except FirebaseError as e:
            logger.error(f"Token verification error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            return None
    
    def create_user(self, email: str, password: str, display_name: str = None) -> Optional[str]:
        """
        Create a new Firebase user.
        
        Args:
            email (str): User email
            password (str): User password
            display_name (str, optional): User display name
            
        Returns:
            str: User UID if successful, None otherwise
        """
        try:
            if not self._initialized:
                raise RuntimeError("Firebase not initialized. Call initialize() first.")
            
            user_properties = {
                'email': email,
                'password': password,
                'email_verified': False
            }
            
            if display_name:
                user_properties['display_name'] = display_name
            
            user_record = auth.create_user(**user_properties)
            logger.info(f"Created user with UID: {user_record.uid}")
            return user_record.uid
            
        except FirebaseError as e:
            logger.error(f"User creation error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {e}")
            return None

# Global Firebase configuration instance
firebase_config = FirebaseConfig() 