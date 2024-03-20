""" The routes for the extraction service """
import base64
import logging
import json
from typing import List
from pathlib import Path
from fastapi import (
    APIRouter, UploadFile,
    HTTPException, Request, Depends, File
)
# import google.cloud.vision as vision  # pylint: disable=no-member
from app.dependencies import get_google_vision_credentials, get_openai_client
from app.services.extraction_service import (
    extract_image_text, extract_pdf_file_contents,
    extract_text_file_contents, extract_docx_file_contents
)
from app.services.recipe_service import format_recipe
from app.models.recipe import (
    FormattedRecipeResponse, FormatRecipeTextRequest
)
from app.services.chat_service import ChatService
from app.middleware.session_middleware import RedisStore

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

# Load the environment variables
credentials = get_google_vision_credentials()
client = get_openai_client()

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"

router = APIRouter()

file_handlers = {
    "jpg": (
        "image/jpeg", lambda contents, extraction_service:
        extraction_service.extract_image_text(contents)
    ),  # "image/jpeg
    "jpeg": (
        "image/jpeg", lambda contents, extraction_service:
        extraction_service.extract_image_text(contents)
    ),
    "png": (
        "image/png", lambda contents, extraction_service:
        extraction_service.extract_image_text(contents)
    ),
    "pdf": (
        "application/pdf", lambda contents, extraction_service:
        extraction_service.extract_pdf_file_contents(contents)
    ),
    "txt": (
        "text/plain", lambda contents, extraction_service:
        extraction_service.extract_text_file_contents(contents)
    ),
    "heic": (
        "image/heic", lambda contents, extraction_service:
        extraction_service.extract_image_text(contents)
    ),
    "docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        lambda contents, extraction_service:
        extraction_service.extract_docx_file_contents(contents)
    )
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
    description="Upload one or more files of the following types: pdf, txt, jpg, jpeg, png.\
                 The file contents are extracted and processed.",
    tags=["Extraction Endpoints"],
    response_description="The formatted recipe text as a JSON object and the session_id.",
    response_model=FormattedRecipeResponse
)
async def extract_and_format_recipes(
        files: List[UploadFile] = File(..., description="The list of files to upload."),
        chat_service=Depends(get_chat_service), request: Request = None):
    """
    Endpoint to upload and process multiple files.
    Each file's content is extracted and processed according to its type.
    """
    i = 0
    while i <= 3:
        try:
            logger.info(f"Received {len(files)} files for processing.")

            file_types = set([file.filename.split(".")[-1] for file in files])

            logger.debug(f"File types received: {file_types}")

            if not file_types.issubset(file_handlers.keys()):
                raise HTTPException(status_code=400, detail="Invalid file type")

            if len(file_types) > 1:
                raise HTTPException(status_code=400, detail="Files must be of the same type")

            file_type = file_types.pop()

            logger.info(f"Processing files of type: {file_type}")

            if file_type == "pdf":
                extracted_text = await extract_pdf_file_contents([file.file for file in files])
                logger.info(f"Extracted text from pdf: {extracted_text}")
                formatted_text = await format_recipe(extracted_text)

            elif file_type == "txt":
                extracted_text = extract_text_file_contents(
                    [file.file.read().decode('utf-8', errors='ignore') for file in files]
                )
                formatted_text = await format_recipe(extracted_text)

            elif file_type in ["jpg", "jpeg", "png", "heic"]:
                encoded_images = [base64.b64encode(file.file.read()).decode("utf-8") for file in files]
                logger.info("Encoded images for text extraction")
                extracted_text = await extract_image_text(encoded_images)
                logger.info(f"Extracted text from image: {extracted_text}")
                formatted_text = await format_recipe(extracted_text)

            elif file_type == "docx":
                # Convert the docx files to bytes
                encoded_texts = [file.file.read() for file in files]
                extracted_text = await extract_docx_file_contents(encoded_texts)
                logger.info(f"Extracted text from docx: {extracted_text}")
                formatted_text = await format_recipe(extracted_text)

            logger.info(f"Formatted text: {formatted_text} from extracted text: {extracted_text}")

            return {
                "formatted_recipe": json.loads(formatted_text),
                "session_id": chat_service.session_id,
                "thread_id": chat_service.thread_id
            }
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            logger.debug(f"Retrying... {i + 1} attempt to process files.")
            i += 1
            if i == 3:
                raise HTTPException(status_code=500, detail=str(e))
            continue

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
    i = 0
    while i <= 3:
        try:
            recipe = await format_recipe(recipe_text.recipe_text)
            # Add a user message to the chat history
            chat_service.add_user_message(f"Here is a recipe that I have uploaded and formatted for you:\
                {recipe}")

            # Return the formatted recipe
            return {"formatted_recipe": json.loads(recipe), "session_id": chat_service.session_id,
                    "thread_id": chat_service.thread_id}
        except Exception as e:
            logger.error(f"Error formatting recipe text: {e}")
            logger.debug(f"Retrying... {i + 1} attempt to format recipe text.")
            i += 1
            if i == 3:
                raise HTTPException(status_code=500, detail=str(e))
            continue
