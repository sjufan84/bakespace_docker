""" Image generation routes for the API """
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.image_service import generate_image
router = APIRouter()

class ImageRequest(BaseModel):
  """ Define the request model for the image generation endpoint. """
  prompt: str = Field(..., description="The prompt for the image generation.")

class ImageResponse(BaseModel):
    """ Define the response model for the image generation endpoint. """
    image_url: str = Field(..., description="The url for the generated image.")

# Routes for the image functions -- will return the Image object to the frontend
@router.post(
    "/generate-image-url",
    response_description = "The output url for the generated image.",
    summary = "Generate an image based on the user's specifications.",
    tags = ["Image Endpoints"],
    response_model = ImageResponse
)
async def create_image(prompt: ImageRequest):
  """ Endpoint to generate an image based on the user's specifications. """
  return generate_image(prompt.prompt)
