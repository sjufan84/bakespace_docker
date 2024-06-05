""" This module defines the chat routes for the API. """
from typing import List, Union, Optional
import logging
import json
import markdown
from openai import OpenAIError
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
from app.services.recipe_service import create_recipe, claude_recipe
from app.models.recipe import (
    CreateRecipeRequest, CreateRecipeResponse
)
from app.models.chat import ResponseMessage

logging.basicConfig(level=logging.DEBUG)
# Get the "main" logger
logger = logging.getLogger("main")

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
    logger.info("Status call endpoint hit")
    try:
        status = chat_service.check_status()
        # logger.debug(f"Status call response: {status}")
        return status
    except Exception as e:
        logger.error(f"Error in status call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize_general_chat", response_description=
             "The thread id, session id, chat history and message content.",
             response_model=InitializeChatResponse, tags=["Chat Endpoints"])
async def initialize_general_chat(context: CreateThreadRequest, chat_service=Depends(get_chat_service)):
    logger.info(f"Initializing general chat with context: {context}")

    try:
        # Add user message to chat service
        chat_service.add_user_message(message=context.message_content)
        logger.info("User message added to chat service")

        # Initialize OpenAI client
        client = get_openai_client()

        # Construct message content
        message_content = "The context for this chat thread is " + context.message_content
        logger.info(f"Formed message content: {message_content}")

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
        logger.info(f"Chat successfully initialized with message thread: {message_thread}")

        # Set the thread_id in the store and prepare response
        chat_service.set_thread_id(message_thread.id)
        session_id = chat_service.session_id
        # chat_history = chat_service.load_chat_history()

        # Log and return the response
        response = {"thread_id": message_thread.id, "message_content": message_content,
                    "session_id": session_id}
        return response

    except OpenAIError as e:
        logger.error(f"Error in initializing chat: {e}")
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
    logger.info(f'Assistant ID: {assistant_id}')

    # Add the user message to the chat history
    chat_service.add_user_message(message=chef_response.message_content, thread_id=chef_response.thread_id)
    logger.info(f"User message added to chat history: {chef_response.message_content}")

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
                                    "prep_time": {"type": ["integer", "string"]},
                                    "cook_time": {"type": ["string", "integer"], "nullable": True},
                                    "serving_size": {"type": ["string", "integer"], "nullable": True},
                                    "calories": {"type": ["string", "integer"], "nullable": True},
                                    "fun_fact": {"type": "string"},
                                    "pairs_with": {"type": "string"}
                                },
                                "required": [
                                    "recipe_name", "ingredients", "directions", "fun_fact", "pairs_with",
                                    "prep_time", "cook_time", "serving_size", "calories"
                                ]
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
        logger.info(f"Message {message.content} added to thread {chef_response.thread_id}")

        # Create the run
        run = client.beta.threads.runs.create(
            assistant_id=assistant_id,
            thread_id=chef_response.thread_id,
            instructions=instructions,
            tools=tools,
            model="gpt-4o",
            timeout=6000,
        )
        # Poll the run status
        response = await poll_run_status(run_id=run.id, thread_id=run.thread_id)

        if response:      # Add the chef response to the chat history
            # chat_service.add_chef_message(response["message"])

            return {
                "chef_response" : ResponseMessage(
                    content=response["message"], role="ai", thread_id=chef_response.thread_id
                ),
                "thread_id" : chef_response.thread_id,
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
        logger.info(f"Message {message.content} added to thread {chef_response.thread_id}")

        # Create the run
        run = client.beta.threads.runs.create(
            assistant_id=assistant_id,
            thread_id=chef_response.thread_id,
        )
        # Poll the run status
        response = await poll_run_status(run_id=run.id, thread_id=run.thread_id)

        if response:      # Add the chef response to the chat history
            chat_service.add_chef_message(
                message=response["message"], thread_id=chef_response.thread_id
            )
            logger.info(f"Chef response added to chat history: {response['message']}")

            # Response HMTL conversion
            try:
                response_html = markdown.markdown(response["message"])
            except Exception as e:
                response_html = response["message"]
                logger.error(f"Error in converting response to HTML: {e}")

            return {
                "chef_response" : ResponseMessage(
                    content=response["message"], role="ai", thread_id=chef_response.thread_id,
                    html = response_html
                ),
                "thread_id" : chef_response.thread_id,
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
    "/clear-chat-history",
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

@router.get(
    "/view-chat-history", response_description="The chat history, session id and current thread id.",
    summary="View the chat history.", response_model=ViewChatResponse,
    tags=["Chat Endpoints"]
)
async def view_chat_history(
        chat_service: ChatService = Depends(get_chat_service)):
    """ Endpoint to view the chat history. """
    # Get the chat history from the store
    chat_history = chat_service.view_chat_history()
    return chat_history

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
    try:
        recipe = await claude_recipe(
            specifications = recipe_request.specifications, serving_size = recipe_request.serving_size
        )
        logger.info(f"Recipe created: {recipe}")
    except Exception as e:
        logger.error(f"Error creating recipe: {e} with Claude, retrying with GPT")
        recipe = await create_recipe(
            specifications = recipe_request.specifications, serving_size = recipe_request.serving_size
        )

    if recipe_request.thread_id:
      client = get_openai_client()
      message = client.beta.threads.messages.create(
        recipe_request.thread_id,
        content=f"""Your task is to assist a user with their recipe {recipe},
        which was created based on their initial specifications {recipe_request.specifications}
        and serving size {recipe_request.serving_size}. Users may have queries about
        the recipe or wish to modify it. Your role is to engage in a natural,
        sous-chef style conversation, providing expert advice and suggestions
        tailored to their needs. When users request changes or have questions,
        clarify their requirements through engaging dialogue. Once changes are confirmed,
        display the updated format clearly and concisely in the same format as the original
        recipe {recipe} so that they can make sure it looks correct before saving.
        They may also want to ask you about wine pairings, general cooking questions,
        etc.  Graciously answer those questions as well. Remember,
        your role is crucial in ensuring clarity,
        offering culinary expertise, and confirming the changes during the interaction.
        Although your role is listed as 'user' due to API constraints.
        Keep the conversation flowing
        until it is clear that the user is satisfied with the recipe.  In other words,
        you are the AI sous chef in this conversation.""",
        role="user",
        metadata={},
      )
      # Log the message
      logger.info(f"Message {message.content} added to thread {recipe_request.thread_id}")
      # Check to see if the recipe is already a JSON object
      if isinstance(recipe, dict):
          return {
              "recipe": recipe, "session_id": chat_service.session_id,
              "thread_id": recipe_request.thread_id
          }
      else:
          return {
              "recipe": json.loads(recipe), "session_id": chat_service.session_id,
              "thread_id": recipe_request.thread_id
          }
    else:
        return {
            "recipe": json.loads(recipe), "session_id": chat_service.session_id
        }


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
        logger.info(f"Message {message.content} added to thread {message_request.thread_id}")
        return {"thread_id": message.thread_id, "message_content": message.content,
                "created_at" : message.created_at, "metadata": message.metadata}

    except OpenAIError as e:
        logger.error(f"Error in adding message to thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    '/create-recipe-test',
)
async def create_recipe_test(recipe_request: CreateRecipeRequest):
    """ Endpoint to create a recipe. """
    recipe = await claude_recipe(
        specifications = recipe_request.specifications, serving_size = recipe_request.serving_size
    )
    return recipe
