from fastapi import APIRouter
from ..services.pairing_service import get_pairing
from ..models.pairing import Pairing
from typing import List

router = APIRouter()


# Routes for the pairing functions
# Get the pairing type i.e. wine, beer, etc.
#@router.post("/get_pairing_type")
#def get_pairing_type(request: Request, pairing_type: str = Form(...)):
#    request.session['pairing_type'] = pairing_type
    # TODO: Return the correct template/redirect to the correct page on the bakespace frontend


@router.post("/generate_pairing")
# Generate the pairing
async def generate_pairing(recipe_text: str, pairing_type: str) -> Pairing:
    return get_pairing(recipe_text, pairing_type)
    # TODO: Add the pairing to the database
    
