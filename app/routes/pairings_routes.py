""" Pairings routes for the API """
from fastapi import APIRouter
from app.services.pairing_service import generate_pairings

router = APIRouter()

@router.post("/generate_pairings", response_description="The pairings returned as a dictionary.")
async def get_pairings(pairing_type: str, recipe: dict):
    """
    POST /generate_pairings
    Description: This endpoint generates a list of pairings based on the pairing type and recipe provided.
    Parameters:
    - pairing_type: A string that represents the type of pairing. This is a required field.
    - recipe: A dictionary that represents the recipe. This is a required field.
    
    Returns:
    A dictionary containing the generated pairings.
    
    Example:
    Request:
    {
        "pairing_type": "wine",
        "recipe": {
            "name": "Spaghetti Bolognese",
            "ingredients": ["spaghetti", "minced beef", "tomato sauce"]
        }
    }
    
    Response:
    {
        "pairings": ["Merlot", "Cabernet Sauvignon"]
    }
    """
    return generate_pairings(pairing_type, recipe)
