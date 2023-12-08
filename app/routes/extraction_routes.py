""" The routes for the extraction service """
import base64
from typing import List
from pathlib import Path
from fastapi import (
  APIRouter, UploadFile, Query,
  HTTPException, File
)
import google.cloud.vision as vision # pylint: disable=no-member
from app.dependencies import get_google_vision_credentials, get_openai_client

from app.services.extraction_service import (
  extract_image_text, extract_pdf_file_contents,
  extract_text_file_contents
)
#from app.services.recipe_service import format_recipe
from app.services.anthropic_service import AnthropicRecipe, format_recipe


# Load the environment variables
credentials = get_google_vision_credentials()
client = get_openai_client()

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"

def get_session_id(session_id: str = Query(...)):
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
    response_description=f"The processed text from uploaded files.  Will be returned\
    as a JSON object with the fields of {AnthropicRecipe.schema()['properties'].keys()}.",
    summary="Upload and process files.",
    description="Upload one or more files. The\
    files should be of the same type and one of the following: pdf, txt, jpg, jpeg, png.\
    The file contents are extracted and processed.",\
    tags=["Recipe Text Extraction Endpoints"],
    responses={200: {"model": AnthropicRecipe}},
)
async def extract_and_format_recipes(
    files: List[UploadFile] = File(..., description="The list of files to upload.")):
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
      extracted_text = extract_pdf_file_contents([file.file for file in files])
      formatted_text = format_recipe(extracted_text)
      #formatted_text = format_recipe_text(extracted_text)
    # If the file type is text, send it to the text endpoint with the file.file attribute
    if file_type == "txt":
      extracted_text = extract_text_file_contents([file.file.read().decode('utf-8',
      errors = 'ignore') for file in files])
      formatted_text = format_recipe(extracted_text)
    # If the file type is an image, send it to the image endpoint with the files encoded as base64
    if file_type in ["jpg", "jpeg", "png"]:
      # Encode the images as base64
      encoded_images = [base64.b64encode(file.file.read()).decode("utf-8") for file in files]
      extracted_text = await extract_image_text(encoded_images)
      formatted_text = format_recipe(extracted_text)
    # Return the extracted text
    return formatted_text


@router.post(
    "/format-recipe",
    response_description="The formatted recipe text.",
    summary="Format a raw recipe text.",
    description="Takes the raw recipe text that should have been returned from the\
    extraction methods, and formats it.",
    tags=["Recipe Text Extraction Endpoints"])
async def format_text_endpoint(
    recipe_text: str):
    """ Define the function to format text.  Takes in the raw
    recipe text that should have been returned from the extraction methods. """
    recipe = format_recipe(recipe_text)
    # Return the formatted recipe
    return recipe


@router.post("/upload-images")
async def upload_images(files: List[UploadFile] = File(...)):
    client = vision.ImageAnnotatorClient()

    responses = []
    for file in files:
        contents = await file.read()
        image = vision.Image(content=contents)
        
        # Using object localization (object detection)
        response = client.object_localization(image=image)
        objects = response.localized_object_annotations
        detected_objects = [{'name': obj.name, 'confidence': obj.score} for obj in objects]
        responses.append(detected_objects)

    # You can process responses further as needed...
    return {"responses": responses}


