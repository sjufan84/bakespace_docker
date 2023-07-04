# routes/chat_routes.py

from fastapi import APIRouter, Depends
from ..services.chat_service import ChatService
from typing import List
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str

class ChefRequest(BaseModel):
    question: str
    chat_messages: List[ChatMessage]


# Define a router object
router = APIRouter()

# Routes for the chat functions -- will return the ChatMessageHistory object to the frontend
# By utilizing the langchain library, we can provide teh LLM with "memory", which can include
# recipe text, chat history, or any other information that we want to provide to the model.
# Initialize the chat -- provides the first message to the model to start the conversation
# So that it can be used as context for the next message.  There are various ways to optimize
# for token use, but for now we can just use the gpt-3.5-turbo-16k model which will give us more
# than enough tokens to work with.

# Initialize the chat with the initial context -- the context could be a recipe to reference or some other
# information that we want to provide to the model to start the conversation.  This will return the appropriately 
# formatted message to the frontend to display to the user as a json object with the role and content keys.
@router.post("/initialize_chat")
async def initialize_chat(context: str, chat_service: ChatService = Depends(ChatService)):
    initial_message = chat_service.initialize_chat(context)
    # Return the initial message
    return initial_message

# Add a user message to the chat -- this will return the chat history to the frontend as a json object
# that can be parsed and added to the chat history
@router.post("/add_user_message")
async def add_user_message(message: str, chat_service: ChatService = Depends(ChatService)):
    new_user_message = chat_service.add_user_message(message)
    # Return the chat history
    return new_user_message


# Add a chef message to the chat -- this will return the chat history to the frontend as a json object
# that can be parsed and added to the chat history
@router.post("/add_chef_message")
async def add_chef_message(message: str, chat_service: ChatService = Depends(ChatService)):
    new_chef_message = chat_service.add_chef_message(message)
    # Return the chat history
    return new_chef_message


# Get a response from the chef from a user question.  This will be the primary function that we use to get a response
# As it will automatically add the user question and chef response to the chat history automatically.  It takes in
# the user question and the chat history formatted as a dictionary or list of dictionaries with the keys "role" and "content". 
# The data is parsed based on the ChefReques object, which is a list of ChatMessage objects. T.  This will return the chef response 
# to the frontend as a string and update the chat history.
@router.post("/get_chef_response")
async def get_chef_response(chef_request: ChefRequest, chat_service: ChatService = Depends(ChatService)):
    response = chat_service.get_chef_response(question=chef_request.question, chat_messages=chef_request.chat_messages)
    return response


# Create a route to view the chat history -- this takes in the chat service and returns the chat history as a json object
@router.get("/view_chat_history")
async def view_chat_history(chat_service: ChatService = Depends(ChatService)):
    return {"chat_history": chat_service.save_chat_history_dict()}

# Create a route to clear the chat history -- TBD if we want to do this or not
@router.delete("/clear_chat_history")
async def clear_chat_history(chat_service: ChatService = Depends(ChatService)) -> str:
    chat_service.clear_chat_history()
    return {"detail": "Chat history cleared."}
