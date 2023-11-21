""" Image generation routes for the API """
from fastapi import APIRouter, Depends
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..services.image_service import ImageService
router = APIRouter()


# A new dependency function:
def get_image_service(store: RedisStore = Depends(get_redis_store)) -> ImageService:
    """ Dependency function to get the recipe service """
    return ImageService(store=store)

router = APIRouter()

# Routes for the image functions -- will return the Image object to the frontend
@router.post("/generate_image_url", response_description = 
             "The output url for the generated image.",
            summary = "Generate an image based on the user's specifications.",
            tags = ["Image Endpoints"]
            )
async def create_image_url(prompt: str, image_service: ImageService = 
                           Depends(get_image_service)) -> str:
