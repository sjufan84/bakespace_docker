""" Image generation routes for the API """
from fastapi import APIRouter
from app.services.image_service import generate_image
router = APIRouter()

# Routes for the image functions -- will return the Image object to the frontend
@router.post("/generate_image_url", response_description = 
             "The output url for the generated image.",
            summary = "Generate an image based on the user's specifications.",
            tags = ["Image Endpoints"]
            )
async def create_image(prompt: str):
  """ Endpoint to generate an image based on the user's specifications. """
  return generate_image(prompt)
