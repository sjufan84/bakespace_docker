""" This module defines the chat routes for the API. """
from typing import List, Optional, Union
import logging
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from app.utils.assistant_utils import (
    poll_run_status, get_assistant_id
)
from app.models.runs import (
    CreateThreadRequest, GetChefResponse
)
from app.middleware.session_middleware import RedisStore
from app.dependencies import get_openai_client
from app.services.chat_service import ChatService
from app.services.recipe_service import create_recipe
from app.models.recipe import Recipe

logging.basicConfig(level=logging.DEBUG)

# Define a router object
router = APIRouter()

class StatusCallResponse(BaseModel):
  """ Return class for the status call endpoint """
  session_id: Union[str, None] = Field(description="The session id for the chat session.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  thread_id: Union[str, None] = Field(None, description="The thread id for the chat session.")

class ClearChatResponse(BaseModel):
  """ Return class for the clear_chat_history endpoint """
  message: str = Field("Chat history cleared", description="The message returned from the endpoint.")
  session_id: Union[str, None] = Field(..., description="The session id for the chat session.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  thread_id: Union[str, None] = Field(None, description="The thread id for the chat session.")

class ViewChatResponse(BaseModel):
  """ Return class for the view_chat_history endpoint """
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  session_id: str = Field(..., description="The session id for the chat session.")
  thread_id: Union[str, None] = Field(None, description="The current thread id for the chat session.")

class InitializeChatResponse(BaseModel):
  """ Return class for the initialize_chat endpoint """
  thread_id: str = Field(..., description="The thread id for the run to be added to.")
  message_content: str = Field(..., description="The message content.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  session_id: Union[str, None] = Field(..., description="The session id for the chat session.")

class GetChefRequestResponse(BaseModel):
  """ Return class for the get_chef_response endpoint """
  chef_response: str = Field(..., description="The response from the chef.")
  thread_id: str = Field(..., description="The thread id for the chat session.")
  session_id: Union[str, None] = Field(..., description="The session id for the chat session.")
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
    thread_id: Optional[str] = Field(None, description="The thread id for the chat session.")

class CreateRecipeResponse(BaseModel):
    recipe: Recipe = Field(..., description="The recipe object.")
    session_id: Union[str, None] = Field(..., description="The session id for the chat session.")
    thread_id: Union[str, None] = Field(None, description="The thread id for the chat session.")

class CheckStatusResponse(BaseModel):
    """ Return class for the check_status endpoint """
    message: str = Field(..., description="The message returned from the endpoint.")
    status: str = Field(..., description="The status of the run.")
    session_id: Union[str, None] = Field(..., description="The session id for the chat session.")
    chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
    thread_id: Optional[str] = Field(None, description="The thread id for the chat session.")

class NewGetChefResponse(BaseModel):
  """ Get Chef Response Model """
  message_content: str = Field(..., description="The content of the message to be added to the thread.")
  message_metadata: Optional[object] = Field({}, description="The metadata for the message.  A mapping of\
    key-value pairs that can be used to store additional information about the message.")
  chef_type: Optional[str] = Field(
      "home_cook", description="The type of chef that the user wants to talk to.")

class NewChefResponse(BaseModel):
    """ Return class for the get_chef_response endpoint """
    chef_response: str = Field(..., description="The response from the chef.")
    session_id: Union[str, None] = Field(..., description="The session id for the chat session.")
    chat_history: List[dict] = Field(..., description="The chat history for the chat session.")

# Define a function to get the session_id from the headers
def get_session_id(request: Request) -> str:
    """ Define a function to get the session_id from the headers. """
    session_id = request.headers.get("Session-ID")
    return session_id

def get_chat_service(request: Request) -> ChatService:
    """ Define a function to get the chat service. """
    session_id = get_session_id(request)
    redis_store = RedisStore(session_id)
    return ChatService(store=redis_store)

@router.get("/status_call")
async def status_call(chat_service: ChatService = Depends(get_chat_service)) -> dict:
    logging.debug("Status call endpoint hit")
    try:
        status = chat_service.check_status()
        logging.debug(f"Status call response: {status}")
        return status
    except Exception as e:
        logging.error(f"Error in status call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize_general_chat", response_description=
             "The thread id, session id, chat history and message content.",
             response_model=InitializeChatResponse, tags=["Chat Endpoints"])
async def initialize_general_chat(context: CreateThreadRequest, chat_service=Depends(get_chat_service)):
    logging.debug(f"Initializing general chat with context: {context}")

    try:
        # Add user message to chat service
        chat_service.add_user_message(context.message_content)
        logging.debug("User message added to chat service")

        # Initialize OpenAI client
        client = get_openai_client()
        logging.debug("OpenAI client initialized")

        # Construct message content
        message_content = "The context for this chat thread is " + context.message_content
        if context.serving_size:
            message_content += " Serving size: " + context.serving_size
        logging.debug(f"Formed message content: {message_content}")

        # Create message thread
        message_thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": message_content,
                    "metadata": context.message_metadata
                },
            ]
        )
        logging.debug(f"Message thread created with ID: {message_thread.id}")

        # Set the thread_id in the store and prepare response
        chat_service.set_thread_id(message_thread.id)
        session_id = chat_service.session_id
        chat_history = chat_service.load_chat_history()

        # Log and return the response
        response = {"thread_id": message_thread.id, "message_content": message_content,
                    "chat_history": chat_history, "session_id": session_id}
        logging.debug(f"Returning response: {response}")
        return response

    except Exception as e:
        logging.error(f"Error in initializing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/get_chef_response",
    response_description="The thread id for the run to be added to, the chef response, and the session id.",
    summary="Get a response from the chef to the user's question.",
    tags=["Chat Endpoints"],
    responses={
        200: {
            "thread_id": "The thread id for the run to be added to.",
            "chef_response": "The response from the chef",
            "session_id": "The session id."
        }
    },
)
async def get_chef_response(chef_response: GetChefResponse, chat_service:
                            ChatService = Depends(get_chat_service)):
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

    if response:      # Add the chef response to the chat history
      chat_service.add_chef_message(response["message"])

    return {"chef_response" : response["message"],
            "thread_id" : chef_response.thread_id, "chat_history" : chat_service.load_chat_history()}

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

@router.post(
    "/clear_chat_history",
    response_description="The thread id, session id, chat history and success message.",
    description="Clear the chat history for the current session.  Pass the session id in the headers.",
    summary="Clear the chat history.",
    response_model=ClearChatResponse,
    tags=["Chat Endpoints"]
)
async def clear_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    # Clear the chat history
    response = chat_service.clear_chat_history()
    return response

@router.get("/view_chat_history", response_description="The chat history, session id and current thread id.",
            summary="View the chat history.", response_model=ViewChatResponse,
            tags=["Chat Endpoints"])
async def view_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    """ Endpoint to view the chat history. """
    # Get the chat history from the store
    chat_history = chat_service.load_chat_history()
    thread_id = chat_service.thread_id
    session_id = chat_service.session_id
    return {"chat_history": chat_history, "session_id": session_id, "thread_id": thread_id}


@router.post(
    "/get-chef-response",
    response_description="The thread id for the run to be added to, the chef response, and the session id.",
    summary="Get a response from the chef to the user's question.",
    tags=["Chat Endpoints"], include_in_schema=False,
    responses={
        200: {
            # "thread_id": "The thread id for the run to be added to.",
            "chef_response": "The response from the chef",
            "session_id": "The session id.",
            "chat_history": "The chat history for the chat session."
        }
    },
    response_model=NewChefResponse
)
async def new_get_chef_response(
    new_chef_response: NewGetChefResponse, chat_service:
        ChatService = Depends(get_chat_service)):
    """ Endpoint to get a response from the chatbot to a user's question. """

    logging.info("Starting new_get_chef_response")

    client = get_openai_client()

    # Get the assistant id based on the chef type
    assistant_id = get_assistant_id(new_chef_response.chef_type)
    logging.debug(f"Got assistant_id: {assistant_id}")

    # Add the user message to the chat history
    chat_service.add_user_message(new_chef_response.message_content)

    message_content = f"Can you help answer my question {new_chef_response.message_content}.\
        Our chat history so far is {chat_service.load_chat_history()}"

    logging.debug(f"Message content: {message_content}")

    run = client.beta.threads.create_and_run(
        assistant_id=assistant_id,
        thread={
            "messages": [
                {
                    "role" : "user",
                    "content" : message_content,
                    "metadata" : new_chef_response.message_metadata
                }]})

    logging.debug(f"Created and ran thread with id: {run.id}")

    # Poll the run status
    response = await poll_run_status(run_id=run.id, thread_id=run.thread_id)

    logging.debug(f"Got response: {response}")

    if response:      # Add the chef response to the chat history
        chat_service.add_chef_message(response["message"])

    logging.info("Finished new_get_chef_response")

    return {"chef_response" : response["message"],
            "chat_history" : chat_service.load_chat_history(),
            "session_id" : chat_service.session_id}

# Create an endpoint to generate a recipe
@router.post(
    "/create-recipe",
    response_description="The thread id for the run to be added to, the chef response, and the session id.",
    summary="Get a response from the chef to the user's question.",
    tags=["Recipe Endpoints"],
    responses={
        200: {
            "thread_id": "The thread id for the run to be added to.",
            "recipe": "The recipe object",
            "session_id": "The session id."
        }
    },
    response_model=CreateRecipeResponse
)
async def create_new_recipe(recipe_request: CreateRecipeRequest,
                            chat_service: ChatService = Depends(get_chat_service)):
    """ Endpoint to get a response from the chatbot to a user's question. """
    recipe = await create_recipe(specifications = recipe_request.specifications,
                                 serving_size = recipe_request.serving_size)

    if recipe_request.thread_id:
        # Add the recipe to the thread
        client = get_openai_client()
        message = client.beta.threads.messages.create(
            recipe_request.thread_id,
            content=f"You have create a recipe {recipe} for a user based on the specifications\
            {recipe_request.specifications}\
                and serving size {recipe_request.serving_size} they provided.\
                They may want to ask questions about or make changes to the recipe.",
            role="user",
            metadata={},
        )
        # Log the message
        logging.info(f"Message created: {message}")

    return {"recipe": json.loads(recipe), "session_id": chat_service.session_id,
            "thread_id": recipe_request.thread_id}
