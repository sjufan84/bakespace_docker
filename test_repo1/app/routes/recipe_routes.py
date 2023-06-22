from fastapi import APIRouter

from ..services.recipe_service import execute_generate_recipe

router = APIRouter()

@router.post("/generate_recipe")
async def generate_recipe_endpoint(
    specifications: str,
):
    return execute_generate_recipe(
        specifications=specifications
    )