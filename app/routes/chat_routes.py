""" This module defines the chat routes for the API. """
from typing import List, Union, Optional
import logging
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from app.utils.assistant_utils import (
    poll_run_status, get_assistant_id
)
from app.models.runs import (
    CreateThreadRequest, GetChefResponse, ClearChatResponse,
    ViewChatResponse, InitializeChatResponse, GetChefRequestResponse
)
from app.middleware.session_middleware import RedisStore
from app.dependencies import get_openai_client
from app.services.chat_service import ChatService
from app.services.recipe_service import create_recipe
from app.models.recipe import (
    CreateRecipeRequest, CreateRecipeResponse
)

logging.basicConfig(level=logging.DEBUG)

# Define a router object
router = APIRouter()

class StatusCallResponse(BaseModel):
  """ Return class for the status call endpoint """
  session_id: Union[str, None] = Field(description="The session id for the chat session.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  thread_id: Union[str, None] = Field(None, description="The thread id for the chat session.")
  chef_type: str = Field("home_cook", description="The type of chef that the user wants to talk to.")

class AddMessageToThread(BaseModel):
    thread_id: str = Field(..., description="The thread id for the run to be added to.")
    message_content: str = Field(..., description="The content of the message to be added to the thread.")
    metadata: Optional[object] = Field({}, description="The metadata for the message.  A mapping of\
        key-value pairs that can be used to store additional information about the message.")

class AddMessageResponse(BaseModel):
    thread_id: str = Field(..., description="The thread id for the run to be added to.")
    message_content: List = Field(..., description="The content of the message to be added to the thread.")
    created_at: int = Field(..., description="The timestamp for when the message was created.")
    metadata: Optional[object] = Field({}, description="The metadata for the message.  A mapping of\
        key-value pairs that can be used to store additional information about the message.")

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

@router.get(
    "/status_call", response_description="The session id, chat history and thread id\
    of the current chat session.", response_model=StatusCallResponse
)
async def status_call(chat_service: ChatService = Depends(get_chat_service)):
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
    response_model=GetChefRequestResponse
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

    if chef_response.save_recipe:
        message_content = "I am ready to save my recipe!  Please use the 'adjust_recipe' tool\
        to make any necessary changes based on the original recipe and our ensuing conversation."
        instructions = "Use the adjust_recipe tool to make any necessary changes to the original recipe\
            based on the user's requests."
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "adjust_recipe",
                    "description": (
                        "Adjust an existing recipe based on the original recipe object and"
                        " the user specifications and interactions to conform to the recipe"
                        " object schema."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "adjusted_recipe": {
                                "type": "object",
                                "description": (
                                    "The adjusted recipe object following the specified"
                                    " Pydantic schema."
                                ),
                                "properties": {
                                    "recipe_name": {"type": "string"},
                                    "ingredients": {"type": "array", "items": {"type": "string"}},
                                    "directions": {"type": "array", "items": {"type": "string"}},
                                    "prep_time": {"type": ["integer", "string"], "nullable": True},
                                    "cook_time": {"type": ["string", "integer"], "nullable": True},
                                    "serving_size": {"type": ["string", "integer"], "nullable": True},
                                    "calories": {"type": ["string", "integer"], "nullable": True},
                                    "fun_fact": {"type": "string", "nullable": True},
                                    "pairs_with": {"type": "string", "nullable": True}
                                },
                                "required": ["recipe_name", "ingredients", "directions"]
                            },
                        },
                        "required": ["adjusted_recipe"]
                    }
                }
            }
        ]

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
            instructions=instructions,
            tools=tools
        )
        # Poll the run status
        response = await poll_run_status(run_id=run.id, thread_id=run.thread_id)

        if response:      # Add the chef response to the chat history
            # chat_service.add_chef_message(response["message"])

            return {
                "chef_response" : response["message"],
                "thread_id" : chef_response.thread_id, "chat_history" : chat_service.load_chat_history(),
                "adjusted_recipe" : response["tool_return_values"], "session_id": chat_service.session_id
            }

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

            return {
                "chef_response" : response["message"],
                "thread_id" : chef_response.thread_id, "chat_history" : chat_service.load_chat_history(),
                "session_id": chat_service.session_id
            }

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

@router.post(
    "/add-message-to-thread",
    response_description="The thread id, message_content, and success message.",
    description="Add a message to a thread.  Pass the thread id and message content in the body.",
    response_model=AddMessageResponse, tags=["Chat Endpoints"]
)
async def add_message_to_thread(message_request: AddMessageToThread):
    """ Endpoint to add a message to a thread. """
    # Add the message to the thread
    client = get_openai_client()
    try:
        message = client.beta.threads.messages.create(
            message_request.thread_id,
            content=message_request.message_content,
            role="user",
            metadata=message_request.metadata,
        )
        # Log the message
        logging.info(f"Message created: {message}")
        return {"thread_id": message.thread_id, "message_content": message.content,
                "created_at" : message.created_at, "metadata": message.metadata}

    except Exception as e:
        logging.error(f"Error in adding message to thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))
