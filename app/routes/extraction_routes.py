""" The routes for the extraction service """
import base64
import logging
import json
from typing import List, Union, Optional
from pathlib import Path
from fastapi import (
    APIRouter, UploadFile,
    HTTPException, Request, Depends, File
)
from pydantic import BaseModel, Field
# import google.cloud.vision as vision  # pylint: disable=no-member
from app.dependencies import get_google_vision_credentials, get_openai_client
from app.services.extraction_service import (
    extract_image_text, extract_pdf_file_contents,
    extract_text_file_contents
)
from app.services.recipe_service import format_recipe
from app.models.recipe import FormattedRecipe
from app.services.chat_service import ChatService
from app.middleware.session_middleware import RedisStore

logging.basicConfig(level=logging.DEBUG)

# Load the environment variables
credentials = get_google_vision_credentials()
client = get_openai_client()

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"

router = APIRouter()

# Define the request and response models
class UploadFilesRequest(BaseModel):
    """ Define the request model for the upload files endpoint. """
    files: List[UploadFile] = Field(..., description="The list of files to upload.")
    thread_id: Optional[str] = Field(None, description="The thread_id.")

class FormattedRecipeResponse(BaseModel):
    """ Define the response model for the upload files endpoint. """
    formatted_recipe: FormattedRecipe = Field(..., description="The formatted recipe.")
    session_id: Union[str, None] = Field(..., description="The session_id.")
    thread_id: Optional[str] = Field(None, description="The thread_id.")

class FormatRecipeTextRequest(BaseModel):
    """ Define the request model for the format recipe text endpoint. """
    recipe_text: str = Field(..., description="The raw recipe text.")
    thread_id: Optional[str] = Field(None, description="The thread_id.")

""" The basic structure of these endpoints allows for the upload of pdfs, images,
and text files. Using the UploadFile type, the files are uploaded to the endpoint
and then passed to the extraction service to be formatted as bytes and then passed
to the appropriate endpoint.  The endpoints dealing with file uploads expect a
multipart/form-data request containing one or more file fields, where each field
contains the filename and the file content. Clients can use the same field name for
all files if they're sending multiple files.

After the files are uploaded, if they are successfully uploaded, the server will return
a success message.  The uploaded files can then be passed to the appropriate endpoints
for text extraction and recipe formatting.
"""

# Define a function for each file type
file_handlers = {
    "jpg": ("image/jpeg", lambda contents, extraction_service:
            extraction_service.extract_image_text(contents)),  # "image/jpeg
    "jpeg": ("image/jpeg", lambda contents, extraction_service:
            extraction_service.extract_image_text(contents)),
    "png": ("image/png", lambda contents, extraction_service:
            extraction_service.extract_image_text(contents)),
    "pdf": ("application/pdf", lambda contents, extraction_service:
            extraction_service.extract_pdf_file_contents(contents)),
    "txt": ("text/plain", lambda contents, extraction_service:
            extraction_service.extract_text_file_contents(contents)),
}

# Define a function to get the session_id from the headers
def get_session_id(request: Request) -> str:
    """ Define a function to get the session_id from the headers. """
    session_id = request.headers.get("Session-ID")
    return session_id

def get_chat_service(request: Request) -> ChatService:
    """ Define a function to get the chat service. """
    session_id = get_session_id(request)
    redis_store = RedisStore(session_id)
    return ChatService(store=redis_store)

@router.post(
    "/upload-files",
    summary="Upload and process files.",
    description="Upload one or more files. The\
    files should be of the same type and one of the following: pdf, txt, jpg, jpeg, png.\
    The file contents are extracted and processed.",
    tags=["Extraction Endpoints"],
    response_description="The formatted recipe text as a JSON object and the session_id.",
    response_model=FormattedRecipeResponse
)
async def extract_and_format_recipes(
        files: List[UploadFile] = File(..., description="The list of files to upload."),
        chat_service=Depends(get_chat_service), request: Request = None):
    """ Define the function to upload files.  Takes in a list of files. """
    # First we need to make sure that the files are of the same type
    # and they are in our list of accepted file types
    file_types = set([file.filename.split(".")[-1] for file in files])
    # Raise an error if the file types are not in our list of accepted file types
    if not file_types.issubset(file_handlers.keys()):
        raise HTTPException(status_code=400, detail="Invalid file type")
    # Check that the file types are the same
    if len(file_types) > 1:
        raise HTTPException(status_code=400, detail="Files must be of the same type")
    # If the file type is pdf, send it to the pdf endpoint with the file.file attribute
    file_type = file_types.pop()
    if file_type == "pdf":
        extracted_text = await extract_pdf_file_contents([file.file for file in files])
        formatted_text = await format_recipe(extracted_text)
    # formatted_text = format_recipe_text(extracted_text)
    # If the file type is text, send it to the text endpoint with the file.file attribute
    if file_type == "txt":
        extracted_text = extract_text_file_contents(
            [file.file.read().decode('utf-8', errors = 'ignore') for file in files]
        )
        formatted_text = await format_recipe(extracted_text)
    # If the file type is an image, send it to the image endpoint with the files encoded as base64
    if file_type in ["jpg", "jpeg", "png"]:
        # Encode the images as base64
        encoded_images = [base64.b64encode(file.file.read()).decode("utf-8") for file in files]
        extracted_text = await extract_image_text(encoded_images)
        formatted_text = await format_recipe(extracted_text)
    # Return the formatted recipe and the session_id
    return {
        "formatted_recipe": json.loads(formatted_text), "session_id": chat_service.session_id,
        "thread_id": chat_service.thread_id}

@router.post(
    "/format-recipe-text",
    response_description="The formatted recipe text.",
    summary="Format a raw recipe text.",
    description="Takes the raw recipe text that should have been returned from the\
    extraction methods, and formats it.",
    tags=["Extraction Endpoints"],
    response_model=FormattedRecipeResponse)
async def format_text_endpoint(recipe_text: FormatRecipeTextRequest, chat_service=Depends(get_chat_service)):
    """ Define the function to format text.  Takes in the raw
    recipe text that should have been returned from the extraction methods. """
    recipe = await format_recipe(recipe_text.recipe_text)
    # Add a user message to the chat history
    chat_service.add_user_message(f"Here is a recipe that I have uploaded and formatted for you:\
        {recipe}")
    # @TODO add a message to the thread if there is a thread_id

    # Return the formatted recipe
    return {"formatted_recipe": json.loads(recipe), "session_id": chat_service.session_id,
            "thread_id": chat_service.thread_id}
