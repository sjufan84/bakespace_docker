<<<<<<< HEAD
""" This module defines the chat routes for the API. """
import logging
from typing import Optional, Union
from fastapi import APIRouter, Depends
from app.dependencies import get_chat_service, get_recipe_service
from app.models.recipe import Recipe
=======
""" Define the chat routes.  This is where the API endpoints are defined.
The user will receive a session_id when they first connect to the API.
This session_id will be passed in the headers of all subsequent requests. """
from typing import List, Optional, Union
import logging
import json
from fastapi import APIRouter, Depends, Query, File, UploadFile
from pydantic import BaseModel
from app.services.chat_service import ChatService
from app.services.run_service import RunService
from app.utils.assistant_utils import poll_run_status, get_assistant_id, upload_files
from app.middleware.session_middleware import RedisStore, get_redis_store
from app.models.chat import InitialMessage
from app.models.recipe import Recipe
from app.models.runs import (
  CreateThreadRunRequest, CreateMessageRunRequest
)
from app.dependencies import get_openai_client  
>>>>>>> 8527395785d28333fd5240a8229180810d928d69

# Define a router object
router = APIRouter()

<<<<<<< HEAD
=======
class RecipeSpec(BaseModel):
    specifications: str
    serving_size: Optional[str] = "Family-Size"
    chef_type: Optional[str] = None

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

def get_run_service(store: RedisStore = Depends(get_redis_store)):
    """ Define a function to get the chat service.  Takes in session_id and store."""
    return RunService(store=store)

# Add an endpoint that is a "status call" to make sure the API is working.
# It should return the session_id and the chat history, if any.
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
@router.get("/status_call")
async def status_call(chat_service = Depends(get_chat_service)):
    """ Endpoint to check the API status, including session_id and chat history. """
    logging.info("Received status call.")
    return chat_service.check_status()

<<<<<<< HEAD
@router.post("/get_new_recipe", response_description=
            "A new recipe based on a user's requested changes as a dict.", tags=["Chat Endpoints"],
            responses={200: {"model": Recipe, "description": "OK"}})
async def get_new_recipe(adjustments: str, chef_type: Optional[str] = None,
                        chat_service = Depends(get_chat_service),
                        recipe_service = Depends(get_recipe_service)):
    """ Endpoint to get a new recipe based on user's requested changes. """
    new_recipe = await chat_service.get_new_recipe(adjustments, recipe_service, chef_type=chef_type)
    return new_recipe

@router.post("/get_recipe_chef_response", response_description="""
            The response is the chat history as a list of messages, the session
            recipe as a recipe object, and the session_id as a string.",
            summary="Get a response from the chef to the user's question about a recipe",
            tags=["Chat Endpoints"], responses={200: {"model": ChefResponse,
            "description": "OK"}})""")
async def get_recipe_chef_response(question: str, recipe: Union[str, Recipe, dict] = None,
        chef_type: Optional[str] = None, chat_service = Depends(get_chat_service),
        recipe_service = Depends(get_recipe_service)):
    """ Endpoint to get a response from the chef to the user's question about a recipe. """
    if not recipe:
        try:
            recipe = recipe_service.load_recipe()
        except FileNotFoundError as exc:
            recipe = None
            # Raise the error if the recipe is not found
            raise f'No recipe found. {exc}'
    chef_response = await chat_service.recipe_chat(recipe, question, chef_type=chef_type)
    return chef_response

@router.post("/get_chef_response", response_description=
            "The response from the chef as a message object and\
            the chat_history as a list of messages.",
            summary="Get a response from the chef to the user's question.",
            tags=["Chat Endpoints"],
            responses={200: {"description": "OK"}})
async def get_chef_response(question: str,
                            chat_service = Depends(get_chat_service),
                            chef_type: Optional[str] = None):
    """ Endpoint to get a response from the chatbot to a user's question. """
    response = await chat_service.general_chat(question, chef_type)
    return response

@router.get("/view_chat_history", response_description="The chat history returned as a dictionary.",
            tags=["Chat Endpoints"])
async def view_chat_history(chat_service = Depends(get_chat_service),
    session_id: Optional[str] = None):
    """ Endpoint to view the chat history. """
    logging.info("Viewing chat history.")
    return {"chat_history": chat_service.load_chat_history(session_id)}

@router.delete("/clear_chat_history",
            response_description="A message confirming that the chat history has been cleared.",
            tags=["Chat Endpoints"])
async def clear_chat_history(chat_service = Depends(get_chat_service)):
    """ Endpoint to clear the chat history. """
    logging.info("Clearing chat history.")
=======
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

@router.post("/create_new_recipe", response_description="Generate a recipe\
based on the specifications provided.", tags=["Recipe Endpoints"])
async def create_new_recipe(recipe_spec: RecipeSpec, chat_service: ChatService = Depends(get_chat_service)):
    """
    Generates a new recipe based on the specifications provided.
    Returns a json object that includes the parsed recipe, the chef response,
    and the session id.
    {"Recipe" : parsed_recipe, "chef_response":
    chef_response, "session_id": self.session_id}
    """
    return chat_service.create_new_recipe(specifications=recipe_spec.specifications,
    chef_type=recipe_spec.chef_type, serving_size=recipe_spec.serving_size)

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
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
    chat_service.clear_chat_history()
    return {"detail": "Chat history cleared."}

# ------------------------------------------------------------------------------------------
# Below we define the endpoints for the assistants API calls.  We want to migrate the
# current end point structure to this one ultimately.
@router.post("/create_thread_run",
            summary="Create a thread and run", 
            description='This endpoint creates a new thread and runs it using\
            the provided assistant_id and thread. The run status is then polled\
            and the response is returned.  The response is a JSON object formatted as\
            {"message" : "The message response from the run", "tool_return_values" :\
            "A JSON object containing the tools used and their return values"}')
async def create_thread_run(create_run_request: CreateThreadRunRequest):
  """ Create a thread and run """
  client = get_openai_client()
  if create_run_request.serving_size:
    message_content = create_run_request.message_content + " " + "Serving size: " + create_run_request.serving_size
  else:
    message_content = create_run_request.message_content
  run = client.beta.threads.create_and_run(
  assistant_id=get_assistant_id(create_run_request.chef_type),  
  thread={
    "messages": [
        {
          "role" : "user",
          "content" : message_content, 
    }]}   
  )
  # Poll the run status
  response = json.dumps(poll_run_status(run_id=run.id, thread_id=run.thread_id))

  return response
  
# Define the endpoint to add a message to the thread and run
@router.post("/add_message_and_run", 
            summary="Add a message to a thread and run", 
            description='This endpoint adds a message to an existing\
            thread and runs it. The message is created with the provided\
            thread_id, role, content, and file_ids. The run status\
            is then polled and the response is returned. The response\
            is a JSON object formatted as\
            {"message" : "The message response from the run", "tool_return_values" :\
            "A JSON object containing the tools used and their return values"}')
async def add_message_and_run(message_request: CreateMessageRunRequest):
    """ Add a message to the thread and run """
    client = get_openai_client()
    # Get the assistant id based on the chef type
    assistant_id = get_assistant_id(message_request.chef_type)

    # Create and send the message
    message = client.beta.threads.messages.create(
        message_request.thread_id,
        content=message_request.message_content,
        role="user",
    )
    # Log the message
    logging.info(f"Message created: {message}")

    # Create the run
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=message_request.thread_id
    )
    # Poll the run status
    response = poll_run_status(run_id=run.id, thread_id=run.thread_id)

    return response

# Define an endpoint allow the user to upload an image file and return extracted text
@router.post("/extract_text_from_image", 
            summary="Extract text from an image", 
            description='This endpoint extracts text from an image.\
            The image is uploaded and the text is extracted using\
            Google Cloud Vision. The extracted text is returned.')
async def extract_text_from_image(files: List[UploadFile] = File(None)):
    """ Extract text from an image """
    # If there are uploaded files, pass them to the upload_files function
    #if files:
    #    file_contents = [await file.read() for file in files]
    # Extract the text from the image
    #extracted_text = await extract_image_text(file_contents)
    # Format the extracted text
    #formatted_text = format_recipe(extracted_text)

    #return formatted_text

# Create upload_files endpoint
@router.post("/upload_files", 
            summary="Upload files", 
            description='This endpoint uploads files to the cloud.\
            The files are uploaded and the file IDs are returned.')
async def upload_assistant_files(files: List[UploadFile] = File(None)):
  """ Upload files to OpenAI and return the file IDs """
  file_contents = [await file.read() for file in files]
  file_ids = await upload_files(file_contents)
  return file_ids

# Create an endpoint to retrieve the run steps from a run
@router.get("/list_run_steps", 
            summary="List the steps from a run", 
            description='This endpoint lists the steps from a run.\
            The steps are returned as a JSON object.')
async def list_run_steps(thread_id: str = None, run_id: str = None, limit: int = 20, order: str = "desc"):
  """ List the steps from a run """
  client = get_openai_client()
  # Check to see if there is a thread_id in the call, if not,
  # load the thread_id from the store
  if not thread_id:
      raise ValueError("Thread ID is required.")
  # Check to see if there is a run_id in the call, if not,
  # load the run_id from the store
  if not run_id:
      raise ValueError("Run ID is required.")
  # Load the steps from redis
  run_steps = client.beta.threads.runs.steps.list(
      thread_id=thread_id,
      run_id=run_id,
      limit=limit,
      order=order
  )
  return run_steps