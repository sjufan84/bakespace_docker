# routes/chat_routes.py

from fastapi import APIRouter, Depends
from ..services.chat_service import ChatService
from ..middleware.session_middleware import RedisStore, get_redis_store

# Define a router object
router = APIRouter()


# A new dependency function:
def get_chat_service(session_id: str = None, store: RedisStore = Depends(get_redis_store)) -> ChatService:
    return ChatService(session_id=session_id, store=store)


# Create a route to add a user message to the chat history
@router.post("/add_user_message/")
async def add_user_message(message: str, chat_service: ChatService = Depends(get_chat_service)):
    new_user_message = chat_service.add_user_message(message)
    chat_service.save_chat_history()
    # Return the chat history
    return new_user_message

# Create a route to initialize the chat
@router.post("/initialize_chat")
async def initialize_chat(context: str, chat_service: ChatService = Depends(get_chat_service)):
    initial_message = chat_service.initialize_chat(context)
    chat_service.save_chat_history()
    return {"initial_message": initial_message}


@router.post("/add_chef_message/")
async def add_chef_message(message: str, chat_service: ChatService = Depends(get_chat_service)):
    new_chef_message = chat_service.add_chef_message(message)
    chat_service.save_chat_history()
    return new_chef_message


# Get a response from the chef from a user question.  
@router.post("/get_chef_response/")
async def get_chef_response(question: str, chat_service: ChatService = Depends(get_chat_service)):
    response = chat_service.get_chef_response(question=question)
    # The response will be a json object that is the chat history
    return response

# Create a route to view the chat history -- this takes in the chat service and returns the chat history as a json object
@router.get("/view_chat_history")
async def view_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    return {"chat_history": chat_service.save_chat_history()}

# Create a route to clear the chat history
@router.delete("/clear_chat_history/{session_id}")
async def clear_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    chat_service.clear_chat_history()
    return {"detail": "Chat history cleared."}
