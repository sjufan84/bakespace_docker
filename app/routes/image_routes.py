from fastapi import APIRouter
import logging
from pydantic import BaseModel, Field
from typing import Union
from app.services.image_service import get_image_prompt, create_image_string
from models.recipe import Recipe, FormattedRecipe

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

router = APIRouter()

class ImageRequest(BaseModel):
    """ Define the request model for the image generation endpoint. """
    recipe: Union[dict, Recipe, FormattedRecipe] = Field(
        ..., description="The recipe to generate an image for.")

class ImageResponse(BaseModel):
    """ Define the response model for the image generation endpoint. """
    image_string: str = Field(..., description="The base64 encoded image string.")

@router.post(
    "/generate-image",
    response_description = "A base64 encoded image generated from a prompt generated from\
    a recipe.",
    summary = "Generate an image based on a recipe that a user created.",
    tags = ["Image Endpoints"],
    response_model = ImageResponse
)
async def create_image(recipe: ImageRequest) -> ImageResponse:
    """ Endpoint to generate an image based on the given recipe. """
    logger.debug(f"Received recipe: {recipe.recipe}")
    prompt = await get_image_prompt(recipe.recipe)
    logger.debug(f"Generated prompt: {prompt}")
    image_string = await create_image_string(prompt)
    logger.debug("Image string created")
    return ImageResponse(image_string=image_string)
