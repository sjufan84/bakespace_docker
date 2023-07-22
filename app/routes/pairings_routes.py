""" Pairings routes for the API """
from fastapi import APIRouter, Depends, Header
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..services.pairing_service import PairingService
router = APIRouter()

def get_session_id(session_id: str = Header(...)):
    """ Dependency function to get the session id from the header """
    return session_id

# A new dependency function:
def get_pairing_service(store: RedisStore = Depends(get_redis_store)) -> PairingService:
    """ Dependency function to get the recipe service """
    return PairingService(store=store)

@router.post("/generate_pairing")
# Generate the pairing
async def generate_pairing(recipe_text: str, pairing_type: str, pairing_service:
    PairingService = Depends(get_pairing_service)):
    """ Primary route for the pairing service. User must pass session_id in the headers. """
    return pairing_service.get_pairing(recipe=recipe_text, pairing_type=pairing_type)
    # @TODO: Figure out how we want to parse the data
    # on the backend and if we want to return multiple pairings

@router.get("/load_pairing")
# Load the pairing
async def load_pairing(pairing_service: PairingService = Depends(get_pairing_service)):
    """ Route to load the pairing. User must pass session_id in the headers. """
    return pairing_service.load_pairing()

@router.delete("/delete_pairing")
# Delete the pairing
async def delete_pairing(pairing_service: PairingService = Depends(get_pairing_service)):
    """ Route to delete the pairing. User must pass session_id in the headers. """
    return pairing_service.delete_pairing()
