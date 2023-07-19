""" This module contains the routes for the recipe service """
from typing import Annotated
from fastapi import APIRouter, Depends, Header
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..services.recipe_service import RecipeService
from ..models.recipe import Recipe

# A new dependency function:
def get_recipe_service(store: RedisStore = Depends(get_redis_store)) -> RecipeService:
    """ Dependency function to get the recipe service """
    return RecipeService(store=store)


def get_session_id(session_id: str = Header(...)):
    """ Dependency function to get the session id from the header """
    return session_id

router = APIRouter()

# The main route for the recipe service
@router.post("/generate_recipe")
async def generate_recipe(specifications: Annotated[str, "I would love a good recipe for chicken noodle soup"], recipe_service: RecipeService = Depends(get_recipe_service)) -> Recipe:
    """ 
    Primary route for the recipe service. 
    Client needs to extract session_id from the response and include it in the headers of subsequent requests.
    """
    response = recipe_service.execute_generate_recipe(specifications=specifications)
    return response

# The route for the recipe service to get the recipe by name and session_id
@router.get("/get_recipe_by_name")
async def get_recipe_by_name(recipe_name: str, recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    Route for the recipe service to get the recipe by name and session_id. 
    Client must include session_id in the request headers.
    """
    response = recipe_service.load_recipe(recipe_name=recipe_name)
    return response

# The route to delete a recipe by name and session_id
@router.delete("/delete_recipe_by_name")
async def delete_recipe_by_name(recipe_name: str, recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    Route to delete a recipe by name and session_id. 
    Client must include session_id in the request headers.
    """
    response = recipe_service.delete_recipe(recipe_name=recipe_name)
    return response

@router.get("/view_recipe_history")
async def view_saved_recipes(recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    The route to view the saved recipes by session_id -- should return a list of recipe dictionaries / json objects. 
    Client must include session_id in the request headers.
    """
    response = recipe_service.load_recipe_history()
    return response

@router.delete("/clear_recipe_history")
async def clear_saved_recipes(recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    The route to clear the saved recipes by session_id. 
    Client must include session_id in the request headers.
    """
    response = recipe_service.delete_recipe_history()
    return response

# The route to save the recipe history to the store
@router.post("/save_recipe_history")
async def save_recipe_history(recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    The route to save the recipe history to the store. 
    Client must include session_id in the request headers.
    """
    response = recipe_service.save_recipe_history()
    return response




