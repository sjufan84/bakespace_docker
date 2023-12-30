from fastapi import HTTPException, File, UploadFile, APIRouter
from pydantic import BaseModel
from typing import List
from app.services.redis_service import RedisService
from app.services.anthropic_service import AnthropicRecipe

# Define a router object
router = APIRouter()

@router.get("/chat_history", summary="Load chat history", tags=["Redis Routes"])
async def get_chat_history():
    service = RedisService()
    try:
        return service.load_chat_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''@router.post("/chat_history", summary="Save chat history", tags=["Redis Routes"])
async def save_chat_history(chat_history: List[str]):
    service = RedisService()
    try:
        return service.save_chat_history(chat_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recipe/{recipe_name}", summary="Get a recipe", tags=["Redis Routes"])
async def get_recipe(recipe_name: str):
    service = RedisService()
    try:
        return service.get_recipe(recipe_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recipe", summary="Save a recipe", tags=["Redis Routes"])
async def save_recipe(recipe: AnthropicRecipe):
    service = RedisService()
    return recipe.dict()
    try:
        return service.save_recipe(recipe.recipe_name, recipe.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class Pairings(BaseModel):
    pairings: List[str]

@router.post("/recipe/{recipe_name}/image", summary="Save a recipe image", tags=["Redis Routes"])
async def save_recipe_image(recipe_name: str, image: UploadFile = File(...)):
    service = RedisService()
    try:
        return service.save_recipe_image(recipe_name, await image.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recipe/{recipe_name}/image", summary="Get a recipe image", tags=["Redis Routes"])
async def get_recipe_image(recipe_name: str):
    service = RedisService()
    try:
        return service.get_recipe_image(recipe_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recipe/{recipe_name}/pairings", summary="Save a recipe pairings", tags=["Redis Routes"])
async def save_recipe_pairings(recipe_name: str, pairings: Pairings):
    service = RedisService()
    try:
        return service.save_recipe_pairings(recipe_name, pairings.pairings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recipe/{recipe_name}/pairings", summary="Get a recipe pairings", tags=["Redis Routes"])
async def get_recipe_pairings(recipe_name: str):
    service = RedisService()
    try:
        return service.get_recipe_pairings(recipe_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''