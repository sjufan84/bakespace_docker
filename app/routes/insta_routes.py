""" Routes related to Instalicious """
import logging
from typing import List, Optional
from fastapi import (
    APIRouter, UploadFile,
    HTTPException, Request, Depends, File
)
from pydantic import BaseModel, Field
from app.middleware.session_middleware import RedisStore
from app.services.insta_service import (
    generate_dalle2_images, generate_dalle3_image, create_post
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Define a function to get the session_id from the headers
def get_session_id(request: Request) -> str:
    """ Define a function to get the session_id from the headers. """
    session_id = request.headers.get("Session-ID")
    return session_id

class PostRequest(BaseModel):
    """ Post Request Model """
    prompt: str = Field(..., title="prompt", description="The prompt to use for generating the post.")
    image_file: Optional[UploadFile] = File(
        None, title="image_file", description="The image file to use for generating the post."
    )
    model_choice: str = Field(
        "dall-e-2", title="model_choice", description="The model to use for generating the post.\
        Options are dall-e-2 and dall-e-3."
    )
    num_images: int = Field(
        1, title="num_images", description="The number of images to generate.\
        If model is dall-e-3, number must be 1."
    )
    image_size: str = Field(
        "1024x1024", title="image_size", description="The size of the image to generate.\
        If model is dall-e-3, size can be one of 256x256, 512x512, or 1024x1024.  If dall-e-2, must be one of\
        256x256, 512x512, 1024x1024, 2048x2048, or 4096x4096."
    )


# Create an endpoint to generate an instagram post
# Will take in a prompt and a optionally an image file
@router.post("/generate-post")
async def generate_post(
    request: Request,
    prompt: str,
    image_file: UploadFile = File(None),
    store: RedisStore = Depends(get_session_id)
):
    """ Create an endpoint to generate an instagram post. """
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"Image file: {image_file}")
    logger.debug(f"Session ID: {store.session_id}")
    # Get the chat service
    chat_service = get_chat_service(request=request)
    # Get the messages
    messages = await chat_service.get_messages(
        post_option="with_image",
        prompt=prompt
    )
    # Return the messages
    return messages