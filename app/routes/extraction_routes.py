""" The routes for the extraction service """
from typing import List, Union, Annotated
from fastapi import APIRouter, UploadFile, Depends, Header, File
from ..models.recipe import Recipe 
from ..services.extraction_service import ExtractionService
from ..middleware.session_middleware import RedisStore, get_redis_store

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

@router.post("/extract-text-from-text-files", include_in_schema=False)
async def extract_text_from_text_files_endpoint(file: UploadFile = File(...),
    extraction_service: ExtractionService = Depends(get_extraction_service)):
    """ Define the function to extract text from text files.  Takes in text files, confirms
    that they are text files, converts them to bytes if necessary, and then returns the
    extracted text as a string. """
    extracted_text = extraction_service.extract_text_file_contents(file)
    # Pass the files to the extraction service
    #extracted_text = extraction_service.extract_text_file_contents(file)
    # If successful, return the extracted text
    return extracted_text

@router.post("/extract-text-from-pdf-files", include_in_schema=False)
async def extract_text_from_pdf_files_endpoint(files: List[UploadFile],
    extraction_service: ExtractionService = Depends(get_extraction_service)) -> str:
    """ Define the function to extract text from pdf files.  Takes in pdfs, confirms
    that they are pdfs, converts them to bytes if necessary, and then returns the 
    extracted text as a string. """
    # Convert the files to a list if they are not already
    files_list = [files] if not isinstance(files, list) else files
    # Pass the files to the extraction service
    extracted_text = extraction_service.extract_pdf_file_contents(files_list)
    # If successful, return the extracted text
    return extracted_text

@router.post("/extract-text-from-images", include_in_schema=False)
async def extract_text_from_images_endpoint(images: List[UploadFile],
    extraction_service: ExtractionService = Depends(get_extraction_service)):
    """ Define the function to extract text from images.  Takes in images and passes them to the extraction service. """
    # Convert the files to a list if they are not already
    images_list = [images] if not isinstance(images, list) else images
    # The images must be in bytes format to be uploaded
    extracted_text = extraction_service.extract_image_text(images_list)
    # If successful, return the extracted text
    return extracted_text

@router.post("/format-recipe", include_in_schema=False)
async def format_text_endpoint(recipe_text: str, 
    extraction_service: ExtractionService = Depends(get_extraction_service)) -> Recipe:
    """ Define the function to format text.  Takes in the raw
    recipe text that should have been returned from the extraction methods. """
    recipe = extraction_service.format_recipe_text(recipe_text)
    # Return the formatted recipe
    return recipe
