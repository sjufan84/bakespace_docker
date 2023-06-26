from fastapi import UploadFile
from typing import List
import io
import openai
from ..dependencies import get_openai_api_key, get_openai_org, get_google_vision_credentials
from google.cloud import vision
from spellchecker import SpellChecker
import pdfplumber
import requests
from dotenv import load_dotenv
load_dotenv()

class ExtractionService:
    # Get the OpenAI API key from the .env file and the Google Vision credentials\
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
    def detect_document(uploaded_image):
        
        # Get the Google Vision credentials
        credentials = get_google_vision_credentials()

        # Initialize the Google Vision client
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
    def spellcheck_text(text: str) -> str:


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
        # Create the messages to send to the OpenAI API
        messages = [
            {"role": "system", "content": "You are a helpful Chef who edits user's recipes to make them more readable."},
            {"role": "user", "content": f"Reformat and clean up the following extracted recipe text {recipe}, ensuring that the ingredient names are correct..."}
        ]
        # Create a list of models to try -- will need to stay updated as the models change and become deprecated
        models = ["gpt-3.5-turbo", "gpt-3.5-turbo", "gpt-3.5-turbo-0301"]
        for model in models:
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
                continue

        return "Recipe editing failed."

    @staticmethod
    def photo_recipe_edit(recipe: str) -> str:
        # Create the messages to send to the OpenAI API for the photo recipe editing
        messages = [
            {"role": "system", "content": "You are a helpful Chef who edits user's recipes to make them more readable."},
            {"role": "user", "content": f"Reformat and clean up the following extracted recipe text {recipe}, ensuring that the ingredient names are correct..."}
        ]
        # Create a list of models to try -- will need to stay updated as the models change and become deprecated
        models = ["gpt-4", "gpt-4-0314", "gpt-3.5-turbo"]
        for model in models:
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
                continue

        return "Recipe editing failed."

    @staticmethod
    def get_recipe_sos_answer(recipe: str, question: str) -> str:
        # Create the messages to send to the OpenAI API for the recipe SOS
        messages = [
            {"role": "system", "content": "You are a helpful Chef who answers user's questions about recipes."},
            {"role": "user", "content": f"I have this recipe {recipe}, and I was hoping you could answer my question {question} about it."}
        ]
        # Create a list of models to try -- will need to stay updated as the models change and become deprecated
        models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0301"]
        for model in models:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=750,
                    frequency_penalty=0.5,
                    presence_penalty=0.75,
                    temperature=1,
                    n=1
                )
                answer = response.choices[0].message.content
                return answer
            except (requests.exceptions.RequestException, openai.error.APIError):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-0301",
                        messages=messages,
                        max_tokens=500,
                        frequency_penalty=0.2,
                        temperature=1,
                        n=1,
                        presence_penalty=0.2
                    )
                    answer = response.choices[0].message.content
                    return answer
                except (requests.exceptions.RequestException, openai.error.APIError):
                     return "Failed to extract an answer."

    @staticmethod
    # Extract the text from all of the files and concatenate if necessary
    def extract_and_concatenate_text(recipe_files: List[UploadFile], recipe_text_area: str) -> str:
        allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
        full_recipe_text = ""

        for recipe_file in recipe_files:
            if recipe_file.type == "application/pdf":
                recipe_text = ExtractionService.extract_pdf(recipe_file)
            elif recipe_file.type == "text/plain":
                recipe_text = ExtractionService.extract_text_from_txt(recipe_file)
            elif recipe_text_area != "":
                recipe_text = recipe_text_area
            elif recipe_file.type in allowed_image_types:
                recipe_text = ExtractionService.detect_document(recipe_file)
                recipe_text = ExtractionService.spellcheck_text(recipe_text)
            else:
                print(f"Unsupported file type: {recipe_file.type}")
                continue

            full_recipe_text += recipe_text + "\n\n"

        return full_recipe_text


    def edit_recipe(full_recipe_text: str, recipe_files: List[UploadFile]) -> str:
        # Depending on the file type, use a different model to edit the recipe
        allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
        last_uploaded_file = recipe_files[-1]

        if last_uploaded_file.type in allowed_image_types:
            return ExtractionService.photo_recipe_edit(full_recipe_text)
        else:
            return ExtractionService.text_recipe_edit(full_recipe_text)

