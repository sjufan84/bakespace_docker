""" Define the chat routes.  This is where the API endpoints are defined.
The user will receive a session_id when they first connect to the API.
This session_id will be passed in the headers of all subsequent requests. """
from typing import Union, Annotated
from fastapi import APIRouter, Depends, Query
from ..services.chat_service import ChatService
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..models.chat import InitialMessage, ChefResponse, ChatHistory

# Define a router object
router = APIRouter()


# A new dependency function to get the chat service
# We need to get the session_id from the query parameters
# and pass it to the ChatService
def get_chat_service(store: RedisStore = Depends(get_redis_store)):
    """ Define a function to get the chat service. """
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
@router.post("/initialize_general_chat", response_description="The initial message\
    and the chat history.",
    summary="Initialize a general chat session.",
    description="Initialize a general chat session by passing in context as a string.",
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
        ]
    }
}}})

async def initialize_general_chat(context: Annotated[Union[str, None],
    Query(examples = ["The user is gluten free and has questions about baking.\
    "])] = None, chat_service: ChatService = Depends(get_chat_service)) -> dict:
    """ Define the function to initialize a general chat session.
    Takes in context as a string and returns a json object that includes
    the initial_message, the session_id, and the chat_history. """
    response = chat_service.initialize_general_chat(context=context)
    return {"Initial message succesfully generated for general chat:" : response}

# Create a route to initialize the chat
@router.post("/initialize_recipe_chat",  response_description="The initial message\
    and the chat history.",
    summary="Initialize a recipe chat session.",
    description="Initialize a general chat session by passing in recipe_text as a string.",
    tags=["Chat Endpoints"],
    responses={200: {"model": InitialMessage, "description": "OK", "examples": {
        "application/json": {
            "initial_message": "You are a master chef who has generated a recipe\
                for chicken noodle soup that the user would like to ask questions about.\
                    Your chat history so far is: ",
                    "session_id": "1",
                    "chat_history": [
                        {
                            "role": "ai",
                            "content": "Hello, I'm the recipe chatbot.  How can I help you today?"
                        }
                    ]
                }
            }
        }
    })

async def initialize_recipe_chat(recipe_text: Annotated[str, Query(examples=
    ["The text of the recipe that the user has questions about"])],
    chat_service: ChatService = Depends(get_chat_service)):
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


@router.post("/get_chef_response",  response_description="The response\
    from the chef as a message object and the chat_history as a list of messages.",
    summary="Get a response from the chef to the user's question.",
    description="Get a response from the chef to the user's question by passing in\
        the user's question as a string.",
    tags=["Chat Endpoints"],
    responses={200: {"model": ChefResponse, "description": "OK", "examples": {
        "application/json": {
            "chef_response": {
                "role": "ai",
                "content": "The chef's response to the user's question."
                },
                "session_id": "1",
                "chat_history": [
                    {
                        "role": "ai",
                        "content": "Hello, I'm the recipe chatbot.  How can I help you today?"
                        },
                        {
                            "role": "user",
                            "content": "The user's question."
                        },
                        {
                            "role": "ai",
                            "content": "The chef's response to the user's question."
                        }
                    ]
                }
            }
        }
    })

async def get_chef_response(question: str, chat_service: ChatService
    = Depends(get_chat_service)) -> dict:
    """ Define the function to get a response from the chatbot.
    Takes in a user question and returns a 
    json object that includes the chef_response, the session_id, and the chat_history. """
    response = chat_service.get_chef_response(question=question)
    # The response will be a json object that is the chat history
    return response

@router.get("/view_chat_history", response_description=
        "The chat history returned as a dictionary.", tags=["Chat Endpoints"],
        response_model=ChatHistory,
        responses={200: {"model": ChatHistory, "description": "OK", "examples": {
            "application/json": {
                "chat_history": [
                    {
                        "role": "ai",
                        "content": "Hello, I'm the recipe chatbot.  How can I help you today?"
                        },
                        {
                            "role": "user",
                            "content": "The user's question."
                        },
                        {
                            "role": "ai",
                            "content": "The chef's response to the user's question."
                        }
                    ]
                }
            }
        }
    })

async def view_chat_history(chat_service: ChatService = Depends(get_chat_service)) -> dict:
    """ Define the function to view the chat history.  Takes in the session_id
    in the headers and returns the chat_history. """
    return {"chat_history": chat_service.save_chat_history()}

# Create a route to clear the chat history
@router.delete("/clear_chat_history", response_description="A message confirming\
               that the chat history has been cleared.", tags=["Chat Endpoints"])
async def clear_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    """ Define the function to clear the chat history.
    Takes in the session_id in the headers and returns a message.
    confirming that the chat history has been cleared. """
    chat_service.clear_chat_history()
    return {"detail": "Chat history cleared."}
