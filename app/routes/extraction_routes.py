from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from ..services.extraction_service import ExtractionService 
from ..models.recipe import Recipe 
from typing import List




class TextData(BaseModel):
    text: str

router = APIRouter()

# The basic structure of these endpoints allows for the upload of pdf, image, or text file(s)
# that can then be passed to the extraction service as a list of bytes objects.  The extraction service will
# return a list of strings containing the extracted text from each pdf that can then be 
# concatenated into a single string and passed to the formatting service.  Along the way,
# the extraction service will perform spellcheck on the text to try to correct any spelling errors before
# passing the text to the formatting service.

@router.post("/extract-pdf")
async def extract_pdf_endpoint(pdfs: List[UploadFile] = File(...)) -> List[str]:
    # Upload the pdf files and pass them to the extraction service
    extracted_texts = ExtractionService.extract_pdf_file_contents(pdfs)
    
    return extracted_texts

# This will most likely not be used outside of the extraction service, but it is here for testing purposes
@router.post("/spellcheck-text")
async def spellcheck_text_endpoint(text_data: TextData):
    corrected_text = ExtractionService.spellcheck_text(text_data.text)
    return {"corrected_text": corrected_text}

@router.post("/extract-text-from-txt")
async def extract_text_from_txt_endpoint(text_files: List[UploadFile] = File(...)) -> List[str]:
    # Extract the text from the txt files
    txt_files = [await text_file.read() for text_file in text_files]
    extracted_texts = ExtractionService.extract_text_file_contents(txt_files)

    return extracted_texts
    
# Define a route to extract text from images.  This uses the Google Vision API to extract the text from images
# to be passed to the formatting service
@router.post("/extract-text-from-images")
async def extract_text_from_images_endpoint(images: List[UploadFile] = File(...)) -> List[str]:
    # Upload the images and pass them to the extraction service
    images = [await image.read() for image in images]
    # The images must be in bytes format to be uploaded
    extracted_texts = ExtractionService.extract_image_text(images)
    
    return extracted_texts

# Define a route to format the text.  This intakes a string of text that is the raw extracted text from the
# extraction service and returns a Recipe object that is the formatted recipe
@router.post("/format-recipe")
async def format_text_endpoint(raw_text: str) -> Recipe:
    # Pass the raw text to the extraction service
    recipe = ExtractionService.format_recipe_text(raw_text)
    # Return the formatted recipe
    return recipe
