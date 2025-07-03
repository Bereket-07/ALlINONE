"""
Service factory for managing external service instances.
"""
import logging
from typing import Optional
from src.config import FIREBASE_CREDENTIALS_PATH

logger = logging.getLogger(__name__)

class ServiceFactory:
    """
    Factory for managing service instances.
    """
    
    _firestore_service = None
    
    @classmethod
    def get_firestore_service(cls):
        """
        Get Firestore service instance, initializing if needed.
        
        Returns:
            FirestoreService instance or None if initialization fails
        """
        if cls._firestore_service is None:
            try:
                from src.infrastructure.firebase.firestore_service import FirestoreService
                if FirestoreService.initialize(FIREBASE_CREDENTIALS_PATH):
                    cls._firestore_service = FirestoreService
                    logger.info("Firestore service initialized successfully")
                else:
                    logger.error("Failed to initialize Firestore service")
                    return None
            except Exception as e:
                logger.error(f"Error initializing Firestore service: {e}")
                return None
        
        return cls._firestore_service
    
    @classmethod
    def reset_services(cls):
        """
        Reset all service instances (useful for testing).
        """
        cls._firestore_service = None
        logger.info("Service instances reset") 