""" This module defines the chat routes for the API. """
import logging
from typing import Optional, Union
from fastapi import APIRouter, Depends
from app.dependencies import get_chat_service, get_recipe_service
from app.models.recipe import Recipe

# Define a router object
router = APIRouter()

@router.get("/status_call")
async def status_call(chat_service = Depends(get_chat_service)):
    """ Endpoint to check the API status, including session_id and chat history. """
    logging.info("Received status call.")
    return chat_service.check_status()

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
    chat_service.clear_chat_history()
    return {"detail": "Chat history cleared."}
