# routes/chat_routes.py

from fastapi import APIRouter, Depends
from ..services.chat_service import ChatService

router = APIRouter()

@router.post("/initialize_chat")
async def initialize_chat_endpoint(initial_message: str, chat_service: ChatService = Depends(ChatService)):
    chat_service.initialize_chat(initial_message)
    return {"detail": "Chat initialized."}

@router.post("/add_message_to_chat")
async def add_message_endpoint(message: str, role: str, chat_service: ChatService = Depends(ChatService)):
    chat_service.add_message_to_chat(message, role)
    return {"detail": "Message added to chat."}

@router.get("/get_chef_response")
async def get_chef_response(question: str):
    chat_service = ChatService()
    response = chat_service.get_chef_response(question)
    return {"response": response}