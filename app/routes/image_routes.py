""" Image generation routes for the API """
from fastapi import APIRouter, Depends
from ..middleware.session_middleware import RedisStore
from ..services.image_service import ImageService
router = APIRouter()

# A new dependency function:
def get_image_service(store: RedisStore = Depends(RedisStore)):
    """ Define a function to get the chat service. """
    return ImageService(store=store)


router = APIRouter()

# Routes for the image functions -- will return the Image object to the frontend
@router.post("/generate_image_url", response_description = "The output url for the generated image.",
            summary = "Generate an image based on the user's specifications.",
            tags = ["Image Endpoints"]
            )
async def create_image_url(prompt: str, image_service: ImageService = Depends(get_image_service)) -> str:
    """ Primary route for the image service. User must pass session_id in the headers."""
    output_url = image_service.generate_image_url(prompt)['output_url']
    return output_url

@router.get("/load_image_url", include_in_schema=True, tags=["Image Endpoints"])
async def load_image(image_service: ImageService = Depends(get_image_service)) -> str:
    """ Route to load the image. User must pass session_id in the headers. """
    return image_service.load_image_url()

@router.delete("/delete_image_url", include_in_schema=True, tags=["Image Endpoints"])
async def delete_image(image_service: ImageService = Depends(get_image_service)):
    """ Route to delete the image. User must pass session_id in the headers. """
    return image_service.delete_image_url()