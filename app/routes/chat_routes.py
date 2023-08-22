""" This module defines the chat routes for the API. """
import logging
from fastapi import APIRouter, Depends, Query
from app.services.chat_service import ChatService
from app.services.recipe_service import RecipeService
from app.services.extraction_service import ExtractionService
from app.middleware.session_middleware import RedisStore, get_redis_store
from app.models.chat import ChefResponse, ChatHistory

logging.basicConfig(level=logging.DEBUG)

# Define a router object
router = APIRouter()

def get_session_id(session_id: str = Query(...)):
    """ Dependency function to get the session id from the header """
    return session_id

def get_chat_service(store: RedisStore = Depends(get_redis_store)):
    """ Dependency function to get the chat service. Takes in session_id and store. """
    logging.debug("Initializing chat service.")
    return ChatService(store=store)

def get_recipe_service(store: RedisStore = Depends(get_redis_store)):
    """ Dependency function to get the recipe service. """
    logging.debug("Initializing recipe service.")
    return RecipeService(store=store)

def get_extraction_service(store: RedisStore = Depends(get_redis_store)):
    """ Dependency function to get the extraction service. """
    logging.debug("Initializing extraction service.")
    return ExtractionService(store=store)

@router.get("/status_call")
async def status_call(chat_service: ChatService = Depends(get_chat_service)) -> dict:
    """ Endpoint to check the API status, including session_id and chat history. """
    logging.info("Received status call.")
    return chat_service.check_status()

@router.post("/get_new_recipe", response_description="A new recipe\
              based on a user's requested changes as a dict.")
async def get_new_recipe(user_question: str, chef_type: str = "general",
                        chat_service: ChatService = Depends(get_chat_service),
                        recipe_service: RecipeService = Depends(get_recipe_service)):
    """ Endpoint to get a new recipe based on user's requested changes. """
    logging.info(f"Getting new recipe for user's question: {user_question}.")
    original_recipe = recipe_service.load_recipe()
    new_recipe = chat_service.get_new_recipe(user_question, original_recipe,
    chef_type=chef_type, recipe_service=recipe_service)
    return new_recipe
@router.post("/get_recipe_chef_response",
            response_description="The response is the chat history as a list\
            of messages, the session recipe as a recipe object, and the session_id as a string.",
            summary="Get a response from the chef to the user's question about a recipe",
            tags=["Chat Endpoints"],
            responses={200: {"model": ChefResponse, "description": "OK"}})
async def get_recipe_chef_response(question: str, recipe: str = None, chef_type: str = "general",
                                    chat_service: ChatService = Depends(get_chat_service),
                                    recipe_service: RecipeService = Depends(get_recipe_service)):
    """ Endpoint to get a response from the chef to the user's question about a recipe. """
    logging.info(f"Getting chef response to question about recipe: {question}.")
    chef_response = chat_service.get_recipe_chef_response(question=question,
                                                          recipe_service=recipe_service,
                                                          recipe=recipe, chef_type=chef_type)
    return chef_response

@router.post("/get_chef_response",
            response_description="The response from the chef as a message\
            object and the chat_history as a list of messages.",
            summary="Get a response from the chef to the user's question.",
            tags=["Chat Endpoints"],
            responses={200: {"model": ChefResponse, "description": "OK"}})
async def get_chef_response(question: str, chat_service:
    ChatService = Depends(get_chat_service)) -> dict:
    """ Endpoint to get a response from the chatbot to a user's question. """
    logging.info(f"Getting chef response to question: {question}.")
    response = chat_service.get_chef_response(question=question)
    return response

@router.get("/view_chat_history", response_description="The chat\
            history returned as a dictionary.",
            tags=["Chat Endpoints"], response_model=ChatHistory)
async def view_chat_history(chat_service:
    ChatService = Depends(get_chat_service)) -> dict:
    """ Endpoint to view the chat history. """
    logging.info("Viewing chat history.")
    return {"chat_history": chat_service.load_chat_history()}  # Changed from save_chat_history to load_chat_history

@router.delete("/clear_chat_history", response_description="A\
            message confirming that the chat history has been cleared.",
            tags=["Chat Endpoints"])
async def clear_chat_history(chat_service: ChatService = Depends(get_chat_service)):
    """ Endpoint to clear the chat history. """
    logging.info("Clearing chat history.")
    chat_service.clear_chat_history()
    return {"detail": "Chat history cleared."}