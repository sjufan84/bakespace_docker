""" Image generation routes for the API """
from fastapi import APIRouter, Depends, Header
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..services.image_service import ImageService
router = APIRouter()

def get_session_id(session_id: str = Header(...)):
    """ Dependency function to get the session id from the header """
    return session_id

# A new dependency function:
def get_image_service(store: RedisStore = Depends(get_redis_store)) -> ImageService:
    """ Dependency function to get the recipe service """
    return ImageService(store=store)

router = APIRouter()

# Routes for the image functions -- will return the Image object to the frontend
@router.post("/generate_image_url")
async def create_image_url(prompt: str, image_service: ImageService = Depends(get_image_service)):
    """ Primary route for the image service. User must pass session_id in the headers."""
    output_url = image_service.generate_image_url(prompt)['output_url']
    return output_url

@router.get("/load_image_url")
async def load_image(image_service: ImageService = Depends(get_image_service)):
    """ Route to load the image. User must pass session_id in the headers. """
    return image_service.load_image_url()

@router.delete("/delete_image_url")
async def delete_image(image_service: ImageService = Depends(get_image_service)):
    """ Route to delete the image. User must pass session_id in the headers. """
    return image_service.delete_image_url()