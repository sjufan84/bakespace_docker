from fastapi import UploadFile, HTTPException
from typing import List
from google.cloud import vision
from spellchecker import SpellChecker
import pdfplumber
import io
import openai
from ..dependencies import get_openai_api_key, get_openai_org, get_google_vision_credentials
import requests
from dotenv import load_dotenv
import os

load_dotenv()

class ExtractionService:
    # Get the OpenAI API key from the .env file and the Google Vision credentials
    openai.api_key = get_openai_api_key()
    openai.organization = get_openai_org()

    @staticmethod
    def extract_pdf(pdf_file: io.BytesIO) -> str:
        # Here we are going to use the pdfplumber library to extract the text from the PDF file
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text

    @staticmethod
    def detect_document(uploaded_image: io.BytesIO) -> str:
        # Get the Google Vision credentials
        credentials = get_google_vision_credentials()
        # Initialize the Google Vision client
        client = vision.ImageAnnotatorClient(credentials=credentials)

        # Performs text detection on the image file
        response = client.document_text_detection(image=uploaded_image)

        # Extract the text from the response
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                print('\nBlock confidence: {}\n'.format(block.confidence))
                for paragraph in block.paragraphs:
                    print('Paragraph confidence: {}'.format(
                        paragraph.confidence))
                    for word in paragraph.words:
                        word_text = ''.join([
                            symbol.text for symbol in word.symbols
                        ])
                        print('Word text: {} (confidence: {})'.format(
                            word_text, word.confidence))
                        for symbol in word.symbols:
                            print('\tSymbol: {} (confidence: {})'.format(
                                symbol.text, symbol.confidence))
        
        response_text = response.full_text_annotation.text

        # Check for errors
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        
        # Perform spellcheck on the extracted text
        response_text = ExtractionService.spellcheck_text(response_text)

        return response_text

    @staticmethod
    def spellcheck_text(text: str) -> str:
        # Load the custom domain-specific list
        file_path = "./resources/new_ingredients.txt"
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail=f"File {file_path} not found.")

        with open(file_path, "r") as file:
            cooking_terms = [line.strip() for line in file]

        # Initialize the spell-checker
        spell = SpellChecker(language='en')
        spell.word_frequency.load_words(cooking_terms)

        # Tokenize the returned text from the Vision model
        tokens = text.split()

        # Correct the misspelled words
        corrected_tokens = []
        for token in tokens:
            if token not in cooking_terms:
                corrected = spell.correction(token)
                if corrected:
                    corrected_tokens.append(corrected)
                else:
                    corrected_tokens.append(token)
            else:
                corrected_tokens.append(token)

        # Reconstruct the corrected text
        corrected_text = ' '.join(corrected_tokens)

        return corrected_text

    @staticmethod
    def extract_text_from_txt(file: io.BytesIO) -> str:
        # Extract text from a text file
        text = file.read()
        # Ensure text is decoded if it's in bytes
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        return text

    @staticmethod
    def get_model_for_editing(file_type: str) -> str:
        allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
        if file_type in allowed_image_types:
            return "gpt-4"
        else:
            return "gpt-3.5-turbo"

    @staticmethod
    # @ TODO -- fix the parsing on the backend to align with the BakeSpace API Recipe format
    def edit_recipe_text(recipe: str) -> str:
        # Create the messages to send to the OpenAI API
        messages = [
            {"role": "system", "content": "You are a helpful Chef who edits user's recipes to make them more readable."},
            {"role": "user", "content": f"Reformat and clean up the following extracted recipe text {recipe}, ensuring that the ingredient names are correct..."}
        ]
        model_names = ['gpt-4', 'gpt-3.5-turbo']
        for model in model_names:

            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=750,
                    frequency_penalty=0.1,
                    presence_penalty=0.1,
                    temperature=0.6,
                    n=1,
                    top_p=1
                )
                edited_recipe = response.choices[0].message.content
                return edited_recipe
            except (requests.exceptions.RequestException, openai.error.APIError):
                if model == model_names[-1]:
                    raise HTTPException(status_code=500, detail="Unable to connect to the OpenAI API.")
                else:
                    continue



                


    @staticmethod
    def extract_and_concatenate_text(recipe_files: List[UploadFile], recipe_text_area: str) -> str:
        allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
        full_recipe_text = ""

        for recipe_file in recipe_files:
            content = recipe_file.file.read()
            if recipe_file.content_type == "application/pdf":
                recipe_text = ExtractionService.extract_pdf(io.BytesIO(content))
            elif recipe_file.content_type == "text/plain":
                recipe_text = ExtractionService.extract_text_from_txt(io.BytesIO(content))
            elif recipe_text_area != "":
                recipe_text = recipe_text_area
            elif recipe_file.content_type in allowed_image_types:
                recipe_text = ExtractionService.detect_document(io.BytesIO(content))
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {recipe_file.content_type}")

            full_recipe_text += recipe_text + "\n\n"

        return full_recipe_text

    @staticmethod
    def edit_recipe(full_recipe_text: str, recipe_files: List[UploadFile]) -> str:
        # Depending on the file type, use a different model to edit the recipe
        last_uploaded_file = recipe_files[-1]
        model_name = ExtractionService.get_model_for_editing(last_uploaded_file.content_type)
        return ExtractionService.edit_recipe_text(full_recipe_text, model_name)



