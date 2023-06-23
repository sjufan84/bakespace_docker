from fastapi import APIRouter
from ..services.pairing_service import get_pairing
from ..models.pairing import Pairing

router = APIRouter()

# Create a route to take in a recipe and return a pairing
@router.post("/generate_pairing")
# Generate the pairing
async def generate_pairing(recipe_text: str, pairing_type: str) -> Pairing:
    return get_pairing(recipe_text, pairing_type)
    # TODO: Figure out how we want to parse the data 
    # on the backend and if we want to return multiple pairings
    
