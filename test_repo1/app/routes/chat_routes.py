# routes/chat_routes.py

from fastapi import APIRouter, Depends
from ..services.chat_service import ChatService

router = APIRouter()

# Routes for the chat functions -- will return the ChatMessageHistory object to the frontend
# By utilizing the langchain library, we can provide teh LLM with "memory", which can include
# recipe text, chat history, or any other information that we want to provide to the model.
# Initialize the chat -- provides the first message to the model to start the conversation
# So that it can be used as context for the next message.  There are various ways to optimize
# for token use, but for now we can just use the gpt-3.5-turbo-16k model which will give us more
# than enough tokens to work with.
@router.post("/initialize_chat")
async def initialize_chat_endpoint(initial_message: str, chat_service: ChatService = Depends(ChatService)):
    chat_service.initialize_chat(initial_message)
    return {"detail": "Chat initialized."}

# Add a message to the chat -- provides the next message to the model to continue the conversation.  @TODO create an enum for the role with the values of "user" and "ai"
@router.post("/add_message_to_chat")
async def add_message_endpoint(message: str, role: str, chat_service: ChatService = Depends(ChatService)):
    chat_service.add_message_to_chat(message, role)
    return {"detail": "Message added to chat."}

@router.get("/get_chef_response")
async def get_chef_response(question: str):
    chat_service = ChatService()
    response = chat_service.get_chef_response(question)
    return {"response": response}
