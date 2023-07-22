""" Define the chat routes.  This is where the API endpoints are defined.
The user will receive a session_id when they first connect to the API.
This session_id will be passed in the headers of all subsequent requests. """
from typing import Union, Annotated
from fastapi import APIRouter, Depends, Header, Query
from ..services.chat_service import ChatService
from ..middleware.session_middleware import RedisStore, get_redis_store

# Define a router object
router = APIRouter()

def get_session_id(session_id: str = Header(...)):
    """ Dependency function to get the session id from the header """
    return session_id

# A new dependency function to get the chat service
# We need to get the session_id from the headers
def get_chat_service(store: RedisStore = Depends(get_redis_store)):
    """ Define a function to get the chat service.  Takes in session_id and store."""
    return ChatService(store=store)

# Add an endpoint that is a "status call" to make sure the API is working.
# It should return the session_id and the chat history, if any.
@router.get("/status_call")
async def status_call(chat_service: ChatService = Depends(get_chat_service)) -> dict:
    """ Define the function to make a status call.  Will return the session_id
    and the chat_history to the user """
    return chat_service.check_status()

# Create a route to add a user message to the chat history
@router.post("/add_user_message", include_in_schema=False)
async def add_user_message(message: str, chat_service: ChatService = Depends(get_chat_service)):
    """ Define the function to add a user message.  Takes in message and chat_service. """
    new_user_message = chat_service.add_user_message(message)
    chat_service.save_chat_history()
    # Return the chat history
    return new_user_message

# Create a route to initialize the chat
@router.post("/initialize_general_chat")
async def initialize_general_chat(context: Annotated[Union[str, None],
    Query(examples = ["The user is gluten free and has questions about baking.\
    "])] = None, chat_service: ChatService = Depends(get_chat_service)) -> dict:
    """ Define the function to initialize a general chat session.
    Takes in context as a string and returns a json object that includes
    the initial_message, the session_id, and the chat_history. """
    response = chat_service.initialize_general_chat(context=context)
    return {"Initial message succesfully generated for general chat:" : response}

# Create a route to initialize the chat
@router.post("/initialize_recipe_chat")
async def initialize_recipe_chat(recipe_text: Annotated[str, "The text of the recipe that the user\
    has questions about"], chat_service: ChatService = Depends(get_chat_service)) -> dict:
    """ Define the function to initialize a recipe chat session.
    Takes in recipe_text as a string and returns a json object that includes
    the initial_message, the session_id, and the chat_history. """
    initial_message = chat_service.initialize_recipe_chat(recipe_text=recipe_text)
    return initial_message


@router.post("/add_chef_message", include_in_schema=False)
async def add_chef_message(message: str, chat_service: ChatService = Depends(get_chat_service)):
    """ Define the function to add a chef message.  Takes in message and chat_service. """
    new_chef_message = chat_service.add_chef_message(message)
    return new_chef_message


@router.post("/get_chef_response")
async def get_chef_response(question: str, chat_service: ChatService
    = Depends(get_chat_service)) -> dict:
    """ Define the function to get a response from the chatbot.
    Takes in a user question and returns a 
    json object that includes the chef_response, the session_id, and the chat_history. """
    response = chat_service.get_chef_response(question=question)
    # The response will be a json object that is the chat history
    return response

@router.get("/view_chat_history")
async def view_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    """ Define the function to view the chat history.  Takes in the session_id
    in the headers and returns the chat_history. """
    return {"chat_history": chat_service.save_chat_history()}

# Create a route to clear the chat history
@router.delete("/clear_chat_history")
async def clear_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    """ Define the function to clear the chat history.
    Takes in the session_id in the headers and returns a message.
    confirming that the chat history has been cleared. """
    chat_service.clear_chat_history()
    return {"detail": "Chat history cleared."}
