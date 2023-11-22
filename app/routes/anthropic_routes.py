from fastapi import APIRouter
from app.services.anthropic_service import (
  ChatRequest, 
  RecipeRequest, 
  chat, 
  create_recipe,
  adjust_recipe,
  AdjustRecipeRequest,
  PairingRequest,
  generate_pairing
)
router = APIRouter()

@router.post("/anthropic_chat")
async def chat_endpoint(request: ChatRequest):
    """
    POST /chat
    Description: This endpoint allows you to chat with the Anthropic API.
    Parameters:
    - request: A ChatRequest object that contains the prompt, chef_type, and optionally the chat history.
    
    Returns:
    The response from the Anthropic API.
    """
    return chat(request)

@router.post("/create_recipe")
async def create_recipe_endpoint(request: RecipeRequest):
    """
    POST /create_recipe
    Description: This endpoint allows you to create a recipe with the Anthropic API.
    Parameters:
    - request: A RecipeRequest object that contains the specifications, serving_size, chef_type, and optionally the chat history.
    
    Returns:
    The response from the Anthropic API.
    """
    return create_recipe(request)

@router.post("/adjust_recipe")
async def adjust_recipe_endpoint(request: AdjustRecipeRequest):
    """
    POST /adjust_recipe
    Description: This endpoint allows you to adjust a recipe with the Anthropic API.
    Parameters:
    - request: An AdjustRecipeRequest object that contains the recipe, adjustments, chef_type, and optionally the chat history.
    
    Returns:
    The response from the Anthropic API.
    """
    return adjust_recipe(request)

@router.post("/generate_pairing")
async def generate_pairing_endpoint(request: PairingRequest):
    """
    POST /generate_pairing
    Description: This endpoint allows you to generate a pairing for a recipe with the Anthropic API.
    Parameters:
    - request: A PairingRequest object that contains the recipe and chef_type.
    
    Returns:
    The response from the Anthropic API.
    """
    return generate_pairing(request)