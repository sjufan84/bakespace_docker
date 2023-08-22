""" The routes for the extraction service """
import base64
from typing import List
from pathlib import Path
from fastapi import APIRouter, UploadFile, Depends, Header, HTTPException, File, Body
from ..services.extraction_service import ExtractionService
from ..middleware.session_middleware import RedisStore, get_redis_store
from ..models.extraction import ExtractedTextResponse
from ..models.recipe import Recipe

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"

# A new dependency function:
def get_extraction_service(store: RedisStore = Depends(get_redis_store)) -> ExtractionService:
    """ Dependency function to get the recipe service """
    return ExtractionService(store=store)


def get_session_id(session_id: str = Header(...)):
    """ Dependency function to get the session id from the header """
    return session_id

router = APIRouter()

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
    "jpg": ("image/jpeg", lambda contents, extraction_service: extraction_service.extract_image_text(contents)),  # "image/jpeg
    "jpeg": ("image/jpeg", lambda contents, extraction_service: extraction_service.extract_image_text(contents)),
    "png": ("image/png", lambda contents, extraction_service: extraction_service.extract_image_text(contents)),
    "pdf": ("application/pdf", lambda contents, extraction_service: extraction_service.extract_pdf_file_contents(contents)),
    "txt": ("text/plain", lambda contents, extraction_service: extraction_service.extract_text_file_contents(contents)),
}

@router.post(
    "/upload-files/",
    response_description="The processed text from uploaded files.",
    summary="Upload and process files.",
    description="Upload one or more files. The files should be of the same type and one of the following: pdf, txt, jpg, jpeg, png. The file contents are extracted and processed.",
    tags=["Recipe Text Extraction Endpoints"],
    responses = {200: {"model": ExtractedTextResponse, "description": "OK", "examples": {
        "application/json": {
            "Files uploaded successfully",
            "Extracted Recipe Text: ",
        }
    }}})

async def create_upload_files(
    files: List[UploadFile] = File(..., description="The list of files to upload."),
    extraction_service: ExtractionService = Depends(get_extraction_service)
):
    """ Define the function to upload files.  Takes in a list of files. """
    # First we need to make sure that the files are of the same type and they are in our list of accepted file types
    file_types = set([file.filename.split(".")[-1] for file in files])
    # Raise an error if the file types are not in our list of accepted file types
    if not file_types.issubset(file_handlers.keys()):
        raise HTTPException(status_code=400, detail="Invalid file type")
    # Check that the file types are the same
    if len(file_types) > 1:
        raise HTTPException(status_code=400, detail="Files must be of the same type")
    # If the file type is pdf, send it to the pdf endpoint with the file.file attribute
    file_type = file_types.pop()
    if file_type== "pdf":
        extracted_text = extraction_service.extract_pdf_file_contents([file.file for file in files])
        formatted_text = extraction_service.format_recipe_text(extracted_text)
        return {"filenames": [file.filename for file in files], "types": file_types,
        "contents" : extracted_text, "formatted_text": formatted_text}
    # If the file type is text, send it to the text endpoint with the file.file attribute
    if file_type == "txt":
        extracted_text = extraction_service.extract_text_file_contents([file.file.read().decode('utf-8',
        errors = 'ignore') for file in files])
        formatted_text = extraction_service.format_recipe_text(extracted_text)
        return {"filenames": [file.filename for file in files], "types": file_types, "contents" :
        extracted_text, "formatted_text": formatted_text}
    # If the file type is an image, send it to the image endpoint with the files encoded as base64
    if file_type in ["jpg", "jpeg", "png"]:
        # Encode the images as base64
        encoded_images = [base64.b64encode(file.file.read()).decode("utf-8") for file in files]
        extracted_text = extraction_service.extract_image_text(encoded_images)
        formatted_text = extraction_service.format_recipe_text(extracted_text)
        return {"filenames": [file.filename for file in files], "types": file_types,
        "contents" : extracted_text, "formatted_text": formatted_text}

@router.post(
    "/format-recipe",
    response_description="The formatted recipe text.",
    summary="Format a raw recipe text.",
    description="Takes the raw recipe text that should have been returned from the\
    extraction methods, and formats it.",
    tags=["Recipe Text Extraction Endpoints"],
    responses = {200: {"model": Recipe, "description": "OK", "examples": {
        "application/json": {
            "name": "Chicken Noodle Soup",
            "ingredients": [
                "1 tablespoon butter",
                "1/2 cup chopped onion",
                "1/2 cup chopped celery",
                "4 (14.5 ounce) cans chicken broth",
            ],
            "instructions": [
                "In a large pot over medium heat, melt butter. Cook onion and celery in butter until just tender, 5 minutes.",
                "Pour in chicken and vegetable broths and stir in chicken, noodles, carrots, basil, oregano, salt and pepper.",
                "Bring to a boil, then reduce heat and simmer 20 minutes before serving."
            ],
            "prep_time": "10 minutes",
            "cook_time": "30 minutes",
            "total_time": "40 minutes",
            "servings": 6,
            "calories": 250
        }
    }}})

async def format_text_endpoint(
    recipe_text: str = Body(..., description="The raw recipe text to format."),
    extraction_service: ExtractionService = Depends(get_extraction_service)
) -> Recipe:
    """ Define the function to format text.  Takes in the raw
    recipe text that should have been returned from the extraction methods. """
    recipe = extraction_service.format_recipe_text(recipe_text)
    # Return the formatted recipe
    return recipe
