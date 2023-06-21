from fastapi import APIRouter
from ..services.image_service import generate_image
from ..models.image import Image

router = APIRouter()

@router.post("/generate_image_url")

# Generate the image object that will be used to display the image
async def create_image_url(prompt: str):
    output_url = generate_image(prompt)['output_url']
    image = Image(url=output_url, name=prompt)
    return image

