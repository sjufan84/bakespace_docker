""" Define the chat routes.  This is where the API endpoints are defined.
The user will receive a session_id when they first connect to the API.
This session_id will be passed in the headers of all subsequent requests. """
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query
from app.services.chat_service import ChatService
from app.middleware.session_middleware import RedisStore, get_redis_store
from app.models.chat import InitialMessage
from app.models.recipe import Recipe

# Define a router object
router = APIRouter()

# Set the allowed chef types
allowed_chef_types = ["home_cook", "pro_chef", "adventurous_chef", None]

def get_session_id(session_id: str = Query(...)):
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

# Create a route to initialize a general chat session
@router.post("/initialize_general_chat", response_description="The initial message\
    and the chat history.",
    summary="Initialize a general chat session.",
    description="Initialize a general chat session by passing in context as a string.\
    Optionally, pass in the type of chef as a string. If not passed, the current session\
    chef type will be used. Must be one of ['home_cook', 'pro_chef', 'adventurous_chef', None]",
    tags=["Chat Endpoints"],
    responses={200: {"model": InitialMessage, "description": "OK", "examples": {
    "application/json": {
        "initial_message": "You are  a master chef answering a user's questions about cooking.\
        The context, if any, is: ",
        "session_id": "1",
        "chat_history": [
            {
                "role": "ai",
                "content": "Hello, I'm the recipe chatbot.  How can I help you today?"
            }
        ],
        "chef_type": "home_cook"
    }
}}})
async def initialize_general_chat(context: str = None, chat_service:
    ChatService = Depends(get_chat_service), chef_type:str = None):
    """ Define the function to initialize a general chat session.
    Takes in context as a string and returns a json object that includes
    the initial_message, the session_id, and the chat_history. """
    if chef_type not in allowed_chef_types:
        raise ValueError(f"chef_type must be one of {allowed_chef_types}")
    response = chat_service.initialize_general_chat(context=context, chef_type=chef_type)
    return {"Initial message succesfully generated for general chat:" : response}

# This endpoint initializes a chat session for a recipe.
# It accepts a POST request with the recipe text and the type of chef as parameters.
@router.post(
    "/initialize_recipe_chat", 
    response_description="The initial message and the chat history.",
    tags=["Chat Endpoints"]
)
async def initialize_recipe_chat(
    recipe_text: str,
    chat_service: ChatService = Depends(get_chat_service),
    chef_type: str = None
):
    """
    Initializes a recipe chat session.

    Args:
        recipe_text (str): The text of the recipe to discuss in the chat.
        chat_service (ChatService, optional): The service handling the chat.
        Defaults to the result of get_chat_service().
        chef_type (str, optional): The type of chef involved in the chat.\
        Must be one of the allowed chef types. Defaults to None.

    Raises:
        ValueError: If the provided chef_type is not one of the allowed chef types.

    Returns:
        dict: A dictionary containing the initial message, the session ID, and the chat history.
    """
    if chef_type not in allowed_chef_types:
        raise ValueError(f"chef_type must be one of {allowed_chef_types}")
    initial_message = chat_service.initialize_recipe_chat(recipe_text=recipe_text,
                                                        chef_type=chef_type)
    return initial_message

# This endpoint gets a response from the chef to the user's question.
# It accepts a POST request with the user's question and the type of chef as parameters.
@router.post(
    "/get_chef_response",  
    response_description="The response from the chef as a message object\
    and the chat history as a list of messages.",
    summary="Get a response from the chef to the user's question.",
    description="""Get a response from the chef to the user's
    question by passing in the user's question as a string.
    Optionally, pass in the type of chef as a string. If not passed,
    the current session chef type will be used. Must be one of
    ['home_cook', 'pro_chef', 'adventurous_chef', None]""",
    tags=["Chat Endpoints"]
)
async def get_chef_response(
    question: str,
    chat_service: ChatService = Depends(get_chat_service),
    chef_type: str = None
    ):
    """
    Gets a response from the chatbot to the user's question.

    Args:
        question (str): The user's question.
        chat_service (ChatService, optional): The service
        handling the chat. Defaults to the result of get_chat_service().
        chef_type (str, optional): The type of chef involved in the chat.
        Must be one of the allowed chef types. Defaults to None.

    Raises:
        ValueError: If the provided chef_type is not one of the allowed chef types.

    Returns:
        dict: A dictionary containing the chef's response, the session ID, and the chat history.
    """
    if chef_type not in allowed_chef_types:
        raise ValueError(f"chef_type must be one of {allowed_chef_types}")
    response = chat_service.get_chef_response(question=question, chef_type=chef_type)
    return response

# Endpoint for initiating a cookbook chat session
@router.post("/initialize_cookbook_chat", response_description=
"Initialize the chatbot with a cookbook.", tags=["Chat Endpoints"])
async def initialize_cookbook_chat(recipes_list:
    List[str] = None, chat_service: ChatService = Depends(get_chat_service),
    chef_type: str = None) -> dict:
    """
    Initializes a chat session with a cookbook.

    Args:
        recipes_list (List[str]): The list of recipes in the cookbook. Defaults to None.
        chat_service (ChatService, optional): The service handling the chat.
        Defaults to the result of get_chat_service().
        chef_type (str, optional): The type of chef involved in the chat. Defaults to None.

    Returns:
        dict: A dictionary containing the initial message, the session ID, and the chat history.
    """
    return chat_service.initialize_cookbook_chat(
    recipes_list=recipes_list, chef_type=chef_type)

@router.post("/adjust_recipe", response_description="Create a new recipe\
that needs to be generated based on a previous recipe with adjustments.",
tags=["Recipe Endpoints"])
async def adjust_recipe(adjustments: str, recipe_text: Union[str, dict, Recipe],
chat_service: ChatService = Depends(get_chat_service), chef_type: str = "home_cook"):
    """
    Adjusts a recipe based on user input.

    Args:
        adjustments (str): The adjustments to be made to the recipe.
        recipe (Union[str, dict, Recipe]): The original recipe.
        chat_service (ChatService, optional): The service
        handling the chat. Defaults to the result of get_chat_service().
        chef_type (str, optional): The type of chef involved in the chat. Defaults to "home_cook".

    Returns:
        dict: A dictionary containing the chef's response and the new recipe in the format of 
        {"response" : str = "The chef's response", "recipe" : dict = the new recipe}
    """
    return chat_service.adjust_recipe(adjustments=adjustments,
    recipe=recipe_text, chef_type=chef_type)

@router.post("/create_new_recipe", response_description=
"Generate a recipe based on the specifications provided.", tags=["Recipe Endpoints"])
async def create_new_recipe(specifications: str, serving_size: str = "Family-Size", chat_service:
    ChatService = Depends(get_chat_service), chef_type: Optional[str] = None):
    """
    Generates a new recipe based on the specifications provided.

    Args:
        specifications (str): The specifications for the new recipe.
        chat_service (ChatService, optional): The service handling the chat.
        Defaults to the result of get_chat_service().
        chef_type (str, optional): The type of chef involved in the chat. Defaults to None.
        serving_size (str, optional): The serving size of the recipe. Defaults to "Family-Size"\
        Should be one of ["Family-Size", "Just Me", "For Two", "Potluck-Size"].

    Returns:
        dict: A dictionary containing the chef's response, the session ID, and the formatted recipe.
    """
    return chat_service.create_new_recipe(specifications=specifications,
    chef_type=chef_type, serving_size=serving_size)

@router.get("/view_chat_history", response_description=
"View the chat history.", tags=["Chat Endpoints"])
async def view_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    """ Define the function to view the chat history.  Takes in the session_id
    in the headers and returns the chat_history. """
    return {"chat_history": chat_service.load_chat_history()}

# Create a route to clear the chat history
@router.delete("/clear_chat_history", response_description="A message confirming\
               that the chat history has been cleared.", tags=["Chat Endpoints"])
async def clear_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    """ Define the function to clear the chat history.
    Takes in the session_id in the headers and returns a message.
    confirming that the chat history has been cleared. """
    chat_service.clear_chat_history()
    return {"detail": "Chat history cleared."}
