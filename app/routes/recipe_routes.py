""" This module contains the routes for the recipe service """
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Header
<<<<<<< HEAD
from app.dependencies import get_recipe_service, get_session_id
from ..services.recipe_service import RecipeService
from ..models.recipe import Recipe
=======
from app.middleware.session_middleware import RedisStore, get_redis_store
from app.services.recipe_service import RecipeService
from app.models.recipe import Recipe
>>>>>>> 8527395785d28333fd5240a8229180810d928d69

router = APIRouter()

# The main route for the recipe service
@router.post("/generate_recipe", response_description="A recipe object returned as json.",
    summary="Generate a recipe based on the user's specifications.",
    description="Generate a recipe based on the user's specifications. The user must\
<<<<<<< HEAD
        pass session_id in the query.")
async def generate_recipe(specifications: str,
                        chef_type: Optional[str]="general", recipe_service: RecipeService =
                        Depends(get_recipe_service)):
=======
        pass session_id in the headers.",
    tags=["Recipe Endpoints"], responses={200: {"model": Recipe, "description": "OK", "examples": {
        "application/json": {
            "name": "Chicken Noodle Soup",
            "ingredients": [
                "1 tablespoon butter",
                "1/2 cup chopped onion",
                "1/2 cup chopped celery",
                "4 (14.5 ounce) cans chicken broth",
            ],
            "instructions": [
                """In a large pot over medium heat, melt butter. Cook onion
                and celery in butter until just tender, 5 minutes.",
                "Pour in chicken and vegetable broths and stir in chicken,
                noodles, carrots, basil, oregano, salt and pepper.",
                "Bring to a boil, then reduce heat and simmer 20 minutes before serving."""
            ],
            "prep_time": "10 minutes",
            "cook_time": "30 minutes",
            "total_time": "40 minutes",
            "servings": 6,
            "calories": 250
        }
    }}}, include_in_schema=False)
async def generate_recipe(specifications: Annotated[str, "I would love a good\
    recipe for chicken noodle soup"], recipe_service: RecipeService =
    Depends(get_recipe_service), chef_type:str=None):
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
    """ 
    Primary route for the recipe service. 
    Client needs to extract session_id from the response and include it in the headers
    of subsequent requests.
    """
<<<<<<< HEAD
    response = recipe_service.generate_recipe(specifications=specifications, chef_type=chef_type)
=======
    response = recipe_service.create_new_recipe(specifications=specifications,
    chef_type=chef_type)
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
    return response

# The route for the recipe service to get the recipe by name and session_id
@router.get("/load_recipe", include_in_schema=True, tags=["Recipe Endpoints"],
            response_description="A recipe object returned as json.",
            summary="Load the session recipe.",
            description="Load the session recipe. The user must\
                pass session_id in the headers.",
                responses={200: {"model": Recipe, "description": "OK", "examples": {
                    "application/json": {
                        "name": "Chicken Noodle Soup",
                        "ingredients": [
                            "1 tablespoon butter",
                            "1/2 cup chopped onion",
                            "1/2 cup chopped celery",
                            "4 (14.5 ounce) cans chicken broth",
                        ],
                        "instructions": [
                            """In a large pot over medium heat, melt butter.
                            Cook onion and celery in butter until just tender, 5 minutes.",
                            "Pour in chicken and vegetable broths and stir
                            in chicken, noodles, carrots, basil, oregano, salt and pepper.",
                            "Bring to a boil, then reduce heat and
                            simmer 20 minutes before serving."""
                        ],
                        "prep_time": "10 minutes",
                        "cook_time": "30 minutes",
                        "total_time": "40 minutes",
                        "servings": 6,
                        "calories": 250
                    }
                }}})

async def load_recipe(recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    Route for the recipe service to get the recipe by name and session_id. 
    Client must include session_id in the request headers.
    """
    response = recipe_service.load_recipe()
    return response

# The route to delete a recipe by name and session_id
@router.delete("/delete_recipe", include_in_schema=True, tags=["Recipe Endpoints"])
async def delete_recipe(recipe_service: RecipeService = Depends(get_recipe_service)):
    """ 
    Route to delete a recipe by name and session_id. 
    Client must include session_id in the request headers.
    """
    response = recipe_service.delete_recipe()
    return response
