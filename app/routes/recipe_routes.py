from fastapi import APIRouter, Depends, Request
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..services.recipe_service import RecipeService
from ..middleware.session_middleware import get_redis_store

# A new dependency function:
def get_recipe_service(session_id: str = None, store: RedisStore = Depends(get_redis_store)) -> RecipeService:
    return RecipeService(session_id=session_id, store=store)

router = APIRouter()

# The main route for the recipe service
@router.post("/generate_recipe")
async def generate_recipe(specifications: str, recipe_service: RecipeService = Depends(get_recipe_service)):
    response = recipe_service.execute_generate_recipe(specifications=specifications)
    return response

# The route for the recipe service to get the recipe by name and session_id
@router.get("/get_recipe_by_name")
async def get_recipe_by_name(recipe_name: str, recipe_service: RecipeService = Depends(get_recipe_service)):
    response = recipe_service.load_recipe(recipe_name=recipe_name)
    return response

# The route to save a recipe by name and session_id
@router.post("/save_recipe_by_name")
async def save_recipe_by_name(recipe_name: str, recipe_service: RecipeService = Depends(get_recipe_service)):
    response = recipe_service.save_recipe(recipe_name=recipe_name)
    return response

# The route to delete a recipe by name and session_id
@router.delete("/delete_recipe_by_name")
async def delete_recipe_by_name(recipe_name: str, recipe_service: RecipeService = Depends(get_recipe_service)):
    response = recipe_service.delete_recipe(recipe_name=recipe_name)
    return response

# The route to view the saved recipes by session_id -- should return a list of recipe dictionaries / json objects
@router.get("/view_recipe_history")
async def view_saved_recipes(recipe_service: RecipeService = Depends(get_recipe_service)):
    response = recipe_service.load_recipe_history()
    return response

# The route to clear the saved recipes by session_id
@router.delete("/clear_recipe_history")
async def clear_saved_recipes(recipe_service: RecipeService = Depends(get_recipe_service)):
    response = recipe_service.delete_recipe_history()
    return response

# The route to save the recipe history to the store
@router.post("/save_recipe_history")
async def save_recipe_history(recipe_service: RecipeService = Depends(get_recipe_service)):
    response = recipe_service.save_recipe_history()
    return response



