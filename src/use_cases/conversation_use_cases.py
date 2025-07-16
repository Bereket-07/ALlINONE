from src.infrastructure.services.service_factory import ServiceFactory

async def create_conversation_session_uc(user_id: str, title: str = None):
    firestore_service = ServiceFactory.get_firestore_service()
    if firestore_service is None:
        return None
    return await firestore_service.create_conversation_session(user_id, title)

async def get_recent_conversation_sessions_uc(user_id: str, limit: int = 10):
    firestore_service = ServiceFactory.get_firestore_service()
    if firestore_service is None:
        return []
    return await firestore_service.get_last_n_conversation_sessions(user_id, limit)

async def add_conversation_turn_uc(conversation_data: dict):
    firestore_service = ServiceFactory.get_firestore_service()
    if firestore_service is None:
        return False
    return await firestore_service.add_conversation_turn(conversation_data)

async def get_conversation_turns_uc(user_id: str, conversation_id: str, limit: int = 10):
    firestore_service = ServiceFactory.get_firestore_service()
    if firestore_service is None:
        return []
    return await firestore_service.get_last_n_conversations(user_id, conversation_id, limit)