""" This module contains the routes for the recipe service """
from typing import Annotated
from fastapi import APIRouter, Depends, Header
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..services.recipe_service import RecipeService
# from ..models.recipe import Recipe

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
async def generate_recipe(specifications: Annotated[str, "I would love a good recipe for chicken noodle soup"],
                           recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    Primary route for the recipe service. 
    Client needs to extract session_id from the response and include it in the headers of subsequent requests.
    """
    response = recipe_service.execute_generate_recipe(specifications=specifications)
    return response

# The route for the recipe service to get the recipe by name and session_id
@router.get("/load_recipe", include_in_schema=True)
async def get_recipe_by_name(recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    Route for the recipe service to get the recipe by name and session_id. 
    Client must include session_id in the request headers.
    """
    response = recipe_service.load_recipe()
    return response

# The route to delete a recipe by name and session_id
@router.delete("/delete_recipe", include_in_schema=True)
async def delete_recipe(recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    Route to delete a recipe by name and session_id. 
    Client must include session_id in the request headers.
    """
    response = recipe_service.delete_recipe()
    return response






