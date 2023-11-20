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

<<<<<<< HEAD
@router.get("/load_pairing", include_in_schema=True, tags=["Pairing Endpoints"])
=======
# A new dependency function:
def get_pairing_service(store: RedisStore = Depends(get_redis_store)) -> PairingService:
    """ Dependency function to get the recipe service """
    return PairingService(store=store)

@router.post("/generate_pairing", response_description = "A json object containing the pairing.",
             summary = "Generate a pairing based on the user's specifications.",
             tags = ["Pairing Endpoints"], responses = {200: {"model":
                    Pairing, "description": "OK", "examples": {
                    "application/json": {
                        "pairing_text": "For a pairing with a recipe for chicken noodle soup\
                        , I would recommend a nice chardonnay.",
                        "pairing_reason": "The pairing is appropriate because the wine is light\
                        and will not overpower the soup."
                    }
                }}})

async def generate_pairing(recipe_text: str, pairing_type: str, pairing_service:
    PairingService = Depends(get_pairing_service)):
    """ Primary route for the pairing service. User must pass session_id in the headers. """
    return pairing_service.get_pairing(recipe=recipe_text, pairing_type=pairing_type)
    # @TODO: Figure out how we want to parse the data
    # on the backend and if we want to return multiple pairings

@router.get("/load_pairing", include_in_schema=True, tags=["Pairing Endpoints"],
            responses = {200: {"model": Pairing, "description": "OK", "examples": {
            "application/json": {
                "pairing_text": "For a pairing with a recipe for chicken noodle soup\
                , I would recommend a nice chardonnay.",
                "pairing_reason": "The pairing is appropriate because the wine is light\
                and will not overpower the soup."
            }
        }}})
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
# Load the pairing
async def load_pairing(pairing_service: PairingService = Depends(get_pairing_service)):
    """ Route to load the pairing. User must pass session_id in the headers. """
    return pairing_service.load_pairing()

@router.delete("/delete_pairing", include_in_schema=True, tags=["Pairing Endpoints"])
# Delete the pairing
async def delete_pairing(pairing_service: PairingService = Depends(get_pairing_service)):
    """ Route to delete the pairing. User must pass session_id in the headers. """
    return pairing_service.delete_pairing()
