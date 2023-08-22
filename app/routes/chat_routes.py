""" Define the chat routes.  This is where the API endpoints are defined.
The user will receive a session_id when they first connect to the API.
This session_id will be passed in the headers of all subsequent requests. """
from fastapi import APIRouter, Depends, Query
from ..services.chat_service import ChatService
from ..services.recipe_service import RecipeService
from ..services.extraction_service import ExtractionService
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..models.chat import ChefResponse, ChatHistory


# Define a router object
router = APIRouter()

def get_session_id(session_id: str = Query(...)):
    """ Dependency function to get the session id from the header """
    return session_id

# A new dependency function to get the chat service
# We need to get the session_id from the headers
def get_chat_service(store: RedisStore = Depends(get_redis_store)):
    """ Define a function to get the chat service.  Takes in session_id and store."""
    return ChatService(store=store)

# A new dependency function to get the recipe service
def get_recipe_service(store: RedisStore = Depends(get_redis_store)):
    """ Define a function to get the recipe service. """
    return RecipeService(store=store)

# A new dependecy to get the recipe service
def get_extraction_service(store: RedisStore = Depends(get_redis_store)):
    """ Define a function to get the recipe service. """
    return ExtractionService(store=store)

# Add an endpoint that is a "status call" to make sure the API is working.
# It should return the session_id and the chat history, if any.
@router.get("/status_call")
async def status_call(chat_service: ChatService = Depends(get_chat_service)) -> dict:
    """ Define the function to make a status call.  Will return the session_id
    and the chat_history to the user """
    return chat_service.check_status()

@router.post("/get_new_recipe", response_description="A new recipe based on a user's\
              requested changes as a dict.")
async def get_new_recipe(user_question: str, chef_type: str = "general",
                        chat_service: ChatService = Depends(get_chat_service),
                        recipe_service: RecipeService = Depends(get_recipe_service)):
    """ Define the function to get a new recipe based on a user's requested changes. """
    # Set the original recipe to the recipe in the Redis store
    original_recipe = recipe_service.load_recipe()
    new_recipe = chat_service.get_new_recipe(user_question, original_recipe,
    chef_type=chef_type, recipe_service)
    return new_recipe

@router.post("/get_recipe_chef_response",  response_description="The response\
             is the chat history as a list of messages, the session recipe as a recipe object,\
             and the session_id as a string.",
             summary="Get a response from the chef to the user's question about a recipe",
             description="Get a response from the chef to the user's question about a recipe\
                 by passing in the user's question as a string.",
                 tags=["Chat Endpoints"],
                 responses={200: {"model": ChefResponse, "description": "OK"}}
            )
async def get_recipe_chef_response(question: str, recipe: str = None, chef_type: str = "general", 
    chat_service: ChatService = Depends(get_chat_service), recipe_service:
    RecipeService = Depends(get_recipe_service)):
    """ Define the function to get a response from the chef to the user's question about a recipe.
    Takes in message as a string and returns a json object that includes the chef_response,
    the session_id, and the chat_history. """
    chef_response = chat_service.get_recipe_chef_response(question=question,
                                                          recipe_service=recipe_service,
                                                          recipe=recipe, chef_type=chef_type)
    return chef_response

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
