""" This module defines the chat routes for the API. """
from typing import List, Optional, Union
import logging
import json
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from app.utils.assistant_utils import (
  poll_run_status, get_assistant_id
)
from app.models.runs import (
  CreateThreadRunRequest, CreateMessageRunRequest,
  CreateThreadRequest, GetChefResponse
)
from app.middleware.session_middleware import RedisStore, get_redis_store
from app.dependencies import get_openai_client 
from app.services.chat_service import ChatService
from app.services.recipe_service import create_recipe

# Define a router object
router = APIRouter()

class StatusCallResponse(BaseModel):  
  """ Return class for the status call endpoint """
  session_id: str = Field(description="The session id for the chat session.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  thread_id: Union[str, None] = Field(None, description="The thread id for the chat session.")

class ClearChatResponse(BaseModel):
  """ Return class for the clear_chat_history endpoint """
  message: str = Field("Chat history cleared", description="The message returned from the endpoint.")
  session_id: str = Field(..., description="The session id for the chat session.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  thread_id: Union[str, None] = Field(None, description="The thread id for the chat session.")

class InitializeChatResponse(BaseModel):
  """ Return class for the initialize_chat endpoint """
  thread_id: str = Field(..., description="The thread id for the run to be added to.")
  message_content: str = Field(..., description="The message content.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  session_id: str = Field(..., description="The session id for the chat session.")

class GetChefRequestResponse(BaseModel):
  """ Return class for the get_chef_response endpoint """
  chef_response: str = Field(..., description="The response from the chef.")
  thread_id: str = Field(..., description="The thread id for the chat session.")
  session_id: str = Field(..., description="The session id for the chat session.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")


class RecipeSpec(BaseModel):
    specifications: str
    serving_size: Optional[str] = "Family-Size"
    chef_type: Optional[str] = None

class CreateRecipeRequest(BaseModel):
    """ Request body for creating a new recipe """
    specifications: str = Field(..., description="The specifications for the recipe.")  
    serving_size: Optional[str] = Field("Family-Size", description="The serving size for the recipe.")
    chef_type: Optional[str] = Field("home_cook", description="The type of chef creating the recipe.")
    session_id: Optional[str] = Field("12345", description="The session id for the chat session.")

class CheckStatusResponse(BaseModel):
    """ Return class for the check_status endpoint """
    message: str = Field(..., description="The message returned from the endpoint.")
    status: str = Field(..., description="The status of the run.")
    session_id: str = Field(..., description="The session id for the chat session.")
    chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
    thread_id: Optional[str] = Field(None, description="The thread id for the chat session.")

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



# Define a function to initialize the chatbot with context and an optional recipe
# Create a route to initialize a general chat session
@router.post("/initialize_general_chat", response_description=
            "The thread id for the run to be added to, the session id, and the message content.",
            summary="Initialize a general chat session.",
            tags=["Chat Endpoints"],
            response_model = InitializeChatResponse,
            responses={200: {"thread_id": "The thread id for the run to be added to.",
            "session_id" : "The session id.", "message_content" : "The message content."}})
async def initialize_general_chat(context: CreateThreadRequest, chat_service=Depends(get_chat_service)):
  logging.debug(f"Received request with context: {context}")
  
  # Existing code to add user message
  chat_service.add_user_message(context.message_content)
  logging.debug("User message added to chat service")

  # Logging client and message content formation
  client = get_openai_client()
  logging.debug("OpenAI client initialized")

  if context.serving_size:
      message_content = context.message_content + " " + "Serving size: " + context.serving_size
  else:
      message_content = context.message_content
  message_content = "The context for this chat thread is " + message_content
  logging.debug(f"Formed message content: {message_content}")

  # Existing code to create message thread
  message_thread = client.beta.threads.create(
    messages=[
      {
        "role": "user",
        "content": f"{message_content}",
        "metadata": context.message_metadata  
      },
    ]
  )  
  
  logging.debug(f"Message thread created with ID: {message_thread.id}")

  # Set the thread_id in the store
  chat_service.set_thread_id(message_thread.id)
  logging.debug(f"Thread ID set in chat service: {message_thread.id}")

  # Before returning, log the session_id and other return values
  session_id = chat_service.session_id
  chat_history = chat_service.load_chat_history()
  logging.debug(f"Returning response with session_id: {session_id}, chat_history: {chat_history}, thread_id: {message_thread.id}")

  return {"thread_id": message_thread.id, "message_content": message_content, "chat_history": chat_history, "session_id": session_id}


  
@router.post("/get_chef_response", response_description=
            "The thread id for the run to be added to, the chef response, and the session id.",
            summary="Get a response from the chef to the user's question.",
            tags=["Chat Endpoints"],
            responses={200: {"thread_id": "The thread id for the run to be added to.",
            "chef_response" : "The response from the chef", "session_id" : "The session id."}},
            #response_model=GetChefRequestResponse))
)
async def get_chef_response(chef_response: GetChefResponse, chat_service: ChatService = Depends(get_chat_service)):
  """ Endpoint to get a response from the chatbot to a user's question. """
  client = get_openai_client()
  
  # Get the assistant id based on the chef type
  assistant_id = get_assistant_id(chef_response.chef_type)

  # Add the user message to the chat history
  chat_service.add_user_message(chef_response.message_content)

  if chef_response.serving_size:
    message_content = chef_response.message_content + " " + "Serving size: " + chef_response.serving_size
  else:
    message_content = chef_response.message_content
  if chef_response.thread_id:
    # Create and send the message
    message = client.beta.threads.messages.create(
        chef_response.thread_id,
        content=message_content,
        role="user",
        metadata=chef_response.message_metadata,
    )
    # Log the message
    logging.info(f"Message created: {message}")

    # Create the run
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=chef_response.thread_id,
    )
    # Poll the run status
    response = await poll_run_status(run_id=run.id, thread_id=run.thread_id)
    
    return response
    if response:      # Add the chef response to the chat history
      chat_service.add_chef_message(response["message"])


    return {"chef_response" : response["message"], "thread_id" : chef_response.thread_id, "chat_history" : chat_service.load_chat_history()}
  
  else:
    run = client.beta.threads.create_and_run(
    assistant_id=assistant_id,
    thread={
      "messages": [
          {
            "role" : "user",
            "content" : message_content, 
            "metadata" : chef_response.message_metadata
      }]}
    )
    # Poll the run status
    response = await poll_run_status(run_id=run.id, thread_id=run.thread_id)
    response = json.dumps(response)

    return response

@router.post("/clear_chat_history", response_description="The chat history is cleared.",
            summary="Clear the chat history.",
            response_model=ClearChatResponse,
            tags=["Chat Endpoints"])
async def clear_chat_history(session_id: str, chat_service:
    ChatService = Depends(get_chat_service)):
    """ Endpoint to clear the chat history. """
    # Clear the chat history
    response = chat_service.clear_chat_history()
    return response
  
@router.get("/view_chat_history", response_description="The chat history returned as a dictionary.",
            tags=["Chat Endpoints"])
async def view_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    """ Endpoint to view the chat history. """
    # Get the chat history from the store
    chat_history = chat_service.load_chat_history()
    return chat_history


# ------------------------------------------------------------------------------------------
# Below we define the endpoints for the assistants API calls.  We want to migrate the
# current end point structure to this one ultimately.
@router.post("/create_thread_run",
            summary="Create a thread and run", 
            include_in_schema=False,
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
          "metadata" : create_run_request.message_metadata
    }]}   
  )
  # Poll the run status
  response = json.dumps(poll_run_status(run_id=run.id, thread_id=run.thread_id))

  return response
  
# Define the endpoint to add a message to the thread and run
@router.post("/add_message_and_run", 
            summary="Add a message to a thread and run", 
            include_in_schema=False,
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
        metadata=message_request.message_metadata,
    )
    # Log the message
    logging.info(f"Message created: {message}")

    # Create the run
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=message_request.thread_id
    )
    # Poll the run status
    response = json.dumps(poll_run_status(run_id=run.id, thread_id=run.thread_id))

    return response

# Create an endpoint to create a new recipe
@router.post("/create-recipe", 
            summary="Create a new recipe", 
            include_in_schema=False,  
            description='This endpoint creates a new recipe.\
            The recipe is created using the provided recipe specifications.')
async def create_new_recipe(recipe_request: CreateRecipeRequest):
  """ Create a new recipe """
  # Create the recipe
  recipe = create_recipe(recipe_request.specifications, recipe_request.serving_size)
  return recipe
