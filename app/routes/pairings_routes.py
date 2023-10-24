""" Pairings routes for the API """
import logging
from typing import Union
from fastapi import APIRouter, Depends
from app.dependencies import get_pairing_service
from app.services.pairing_service import PairingService
from app.models.recipe import Recipe

router = APIRouter()

@router.post("/generate_pairings", response_description="The pairings returned as a dictionary.")
async def chat_recipe_pairings(recipe: Union[str, Recipe, dict],
                            pairing_type: str, chef_type: str="general",
                            pairing_service: PairingService = Depends(get_pairing_service)):
    """ Chat about questions related to a specific recipe that
    does not involve the creation of a new recipe. """
    response = await pairing_service.generate_pairings(recipe, pairing_type, chef_type)
    # Log the response
    logging.info("Chat recipe pairings response: %s", response)
    # Return the response
    return response

@router.get("/load_pairing", include_in_schema=True, tags=["Pairing Endpoints"])
# Load the pairing
async def load_pairing(pairing_service: PairingService = Depends(get_pairing_service)):
    """ Route to load the pairing. User must pass session_id in the headers. """
    return pairing_service.load_pairing()

@router.delete("/delete_pairing", include_in_schema=True, tags=["Pairing Endpoints"])
# Delete the pairing
async def delete_pairing(pairing_service: PairingService = Depends(get_pairing_service)):
    """ Route to delete the pairing. User must pass session_id in the headers. """
    return pairing_service.delete_pairing()
