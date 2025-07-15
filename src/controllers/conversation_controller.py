from fastapi import APIRouter, Body, Query
from src.use_cases import conversation_use_cases

router = APIRouter()

@router.post("/api/conversations")
async def create_conversation(user_id: str = Body(...), title: str = Body(None)):
    conversation_id = await conversation_use_cases.create_conversation_session_uc(user_id, title)
    return {"conversation_id": conversation_id}

@router.get("/api/conversations")
async def get_recent_conversations(user_id: str, limit: int = 10):
    sessions = await conversation_use_cases.get_recent_conversation_sessions_uc(user_id, limit)
    return sessions

@router.post("/api/conversations/{conversation_id}/messages")
async def add_message(conversation_id: str, user_id: str = Body(...), query: str = Body(...), response: str = Body(...)):
    data = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "query": query,
        "response": response
    }
    success = await conversation_use_cases.add_conversation_turn_uc(data)
    return {"success": success}

@router.get("/api/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, user_id: str, limit: int = 20):
    messages = await conversation_use_cases.get_conversation_turns_uc(user_id, conversation_id, limit)
    return messages