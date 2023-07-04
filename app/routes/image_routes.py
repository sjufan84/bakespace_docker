from fastapi import APIRouter
from ..services.image_service import generate_image

router = APIRouter()

# Routes for the image functions -- will return the Image object to the frontend
@router.post("/generate_image_url")
async def create_image(prompt: str):
    output_url = generate_image(prompt)['output_url']
    return output_url


