""" Utility functions for extracting text from images and text files. """
from typing import List
from fastapi import UploadFile
import google.cloud.vision as vision # pylint: disable=no-member
import pdfplumber
from app.dependencies import get_google_vision_credentials, get_openai_client

# Load the environment variables
credentials = get_google_vision_credentials()
client = get_openai_client()

async def extract_text_file_contents(files) -> str:
    """ Extract the text from the text file."""
    total_file_contents = ''
    for file in files:
        file_contents = file
        #file_contents = self.spellcheck_text(file_contents)
        total_file_contents += file_contents
    return file_contents

async def extract_pdf_file_contents(files: List[UploadFile]) -> str:
    """ Extract the text from the pdf file. """
    file_contents = ''
    for file in files:
        pdf = pdfplumber.open(file)
        for page in pdf.pages:
            file_contents += page.extract_text()
            #file_contents = spellcheck_text(file_contents)
    return file_contents

async def extract_image_text(files: List[bytes]) -> str:
    """ Extract the text from the image file. """
    client = vision.ImageAnnotatorClient(credentials=credentials) # pylint: disable=no-member
    total_response_text = ''
    for file in files:
        image = vision.Image(content=file) # pylint: disable=no-member
        response = client.document_text_detection(image=image)# pylint: disable=no-member
        response_text = response.full_text_annotation.text # pylint: disable=no-member
        total_response_text += response_text
    return response_text

# Define a function to route user uploads to the relevant tool
# If the user uploads a text, pdf, docx, etc. file we want to pass it to the
# OpenAI Files API to extract the text.  If the user uploads an image file
# we want to pass it to the Google Cloud Vision API to extract the text.
def route_files(files: List[UploadFile]) -> str:
    """ Upload the files to the relevant tool. """
    # Get the file extension
    file_extension = files[0].filename.split(".")[-1]
    # If the file extension is a text file, pdf, docx, etc. pass it to the
    # OpenAI Files API to extract the text
    if file_extension in ["txt", "pdf", "docx"]:
        return "openai"
    # If the file extension is an image file, pass it to the Google Cloud
    # Vision API to extract the text
    elif file_extension in ["png", "jpg", "jpeg"]:
        return "gcp"
    # If the file extension is not supported, return an error
    else:
        return "File type not supported.  Please upload a text, pdf, docx, png, jpg, or jpeg file."

def is_image_file(file: UploadFile) -> bool:
    """
    Determines if the uploaded file is an image based on its MIME type.

    Args:
    file (UploadFile): The file uploaded by the user.

    Returns:
    bool: True if the file is an image, False otherwise.
    """
    image_mime_types = {"image/jpeg", "image/png", "image/gif"}
    text_mime_types = {"text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if file.content_type in image_mime_types:
        return True
    elif file.content_type in text_mime_types:
        return False
    else:
        raise ValueError("File type not supported.  Please upload a text, pdf, docx, png, jpg, or jpeg file.")