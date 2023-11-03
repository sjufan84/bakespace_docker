""" Pairings routes for the API """
from fastapi import APIRouter, Depends
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..services.pairing_service import PairingService
from ..models.pairing import Pairing
router = APIRouter()


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
# Load the pairing
async def load_pairing(pairing_service: PairingService = Depends(get_pairing_service)):
    """ Route to load the pairing. User must pass session_id in the headers. """
    return pairing_service.load_pairing()

@router.delete("/delete_pairing", include_in_schema=True, tags=["Pairing Endpoints"])
# Delete the pairing
async def delete_pairing(pairing_service: PairingService = Depends(get_pairing_service)):
    """ Route to delete the pairing. User must pass session_id in the headers. """
    return pairing_service.delete_pairing()
