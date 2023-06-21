# routes/recipe_routes.py

from fastapi import APIRouter, Depends
from typing import List, Optional

from ..services.recipe_service import execute_generate_recipe
from ..main import get_openai_api_key, get_openai_org

router = APIRouter()

@router.post("/generate_recipe")
async def generate_recipe_endpoint(
    # User's specifications for the recipe
    specifications: str,
    # Additional messages to be added to the recipe -- useful for adding additional / variables such as skill level, etc.
    additional_messages: Optional[List[str]] = None,
    openai_api_key: str = Depends(get_openai_api_key),
    openai_org: str = Depends(get_openai_org),
):
    return execute_generate_recipe(
        specifications, additional_messages, openai_api_key, openai_org
    )