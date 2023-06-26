from fastapi import UploadFile
from typing import List
import io
import openai
import os
from google.cloud import vision
from google.oauth2 import service_account
from spellchecker import SpellChecker
import pdfplumber
from dotenv import load_dotenv

class RecipeService:

    @staticmethod
    def extract_pdf(pdf_file: io.BytesIO) -> str:
        # Here we are going to use the pdfplumber library to extract the text from the PDF file
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text

    @staticmethod
    def detect_document(uploaded_image):

        client = vision.ImageAnnotatorClient(credentials=credentials)

        #with io.BytesIO(uploaded_image) as image_file:
        #    content = image_file

        #image = vision.Image(uploaded_image)

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
        
        return response_text
    
    # Define a function to run the extracted text through a spellchecker
    def spellcheck_text(text):

        # Load the custom domain-specific list
        with open("./resources/new_ingredients.txt", "r") as file:
            cooking_terms = [line.strip() for line in file]

        # Initialize the spell-checker
        spell = SpellChecker(language='en')
        spell.word_frequency.load_words(cooking_terms)

        # Tokenize the returned text from the Vision model`)
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
        return file.read()

    @staticmethod
    def text_recipe_edit(recipe: str) -> str:
        # Your text editing function here
        pass

    @staticmethod
    def photo_recipe_edit(recipe: str) -> str:
        # Your photo editing function here
        pass

    @staticmethod
    def get_recipe_sos_answer(recipe: str, question: str) -> str:
        # Your answer extraction function here
        pass

    @staticmethod
    def extract_and_concatenate_text(recipe_files: List[UploadFile], recipe_text_area: str) -> str:
        # Your text extraction function here
        pass

    @staticmethod
    def edit_recipe(full_recipe_text: str, recipe_files: List[UploadFile]) -> str:
        # Your editing function here
        pass

