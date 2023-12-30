""" This module defines the chat routes for the API. """
from typing import List, Optional, Union
import logging
import json
from fastapi import APIRouter, Depends, Query, HTTPException, Request
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

def get_chat_service(request: Request) -> ChatService:
    """ Define a function to get the chat service. """
    session_id = request.headers.get("Session-ID")
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
             "The thread id for the run to be added to, the session id, and the message content.")
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

    return response
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
    response_description="The chat history is cleared.",
    summary="Clear the chat history.",
    response_model=ClearChatResponse,
    tags=["Chat Endpoints"]
)
async def clear_chat_history(
        session_id: str, chat_service: ChatService = Depends(get_chat_service)):
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
