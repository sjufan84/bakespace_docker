from fastapi import HTTPException
from typing import List
from google.cloud import vision
from spellchecker import SpellChecker
from fastapi import UploadFile, File
from io import BytesIO
import pdfplumber
import openai
from ..dependencies import get_openai_api_key, get_openai_org, get_google_vision_credentials
import requests
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
        PromptTemplate,
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate
)
from ..models.recipe import Recipe
from dotenv import load_dotenv
import os

load_dotenv()

class ExtractionService:
    @staticmethod
    def get_google_vision_credentials():
        # return your Google Vision API credentials
        pass


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
    def extract_text_file_contents(uploaded_files: List[bytes]) -> List[str]:
        # Initialize an empty list to hold the extracted texts
        extracted_texts = []
        
        # Loop over each file
        for uploaded_file in uploaded_files:
            # Decode the file contents from bytes to string
            file_contents = uploaded_file.decode()

            # Perform spellcheck on the file contents
            file_contents = ExtractionService.spellcheck_text(file_contents)

            # Add the file contents to the list
            extracted_texts.append(file_contents)

        # Return the list of file contents
        return extracted_texts


    @staticmethod
    def extract_pdf_file_contents(uploaded_files: List[UploadFile] = File(...)) -> List[str]:
        # Initialize an empty list to hold the extracted texts
        extracted_texts = []
        
        # Loop over each file
        for uploaded_file in uploaded_files:
            # Read the file with PdfFileReader
            pdf = pdfplumber.open(uploaded_file.file)

            # Extract the text from each page
            file_contents = ""

            for page in pdf.pages:
                file_contents += page.extract_text()


            # Perform spellcheck on the file contents
            file_contents = ExtractionService.spellcheck_text(file_contents)

            # Add the file contents to the list
            extracted_texts.append(file_contents)

        # Return the list of file contents as a string
        return extracted_texts

    @staticmethod
    def extract_image_text(uploaded_images: List[bytes]) -> List[str]:
        # Get the Google Vision credentials
        credentials = get_google_vision_credentials()
        # Initialize the Google Vision client
        client = vision.ImageAnnotatorClient(credentials=credentials)
        
        # Initialize a list to hold the extracted texts
        extracted_texts = []

        # Performs text detection on the image file
        for image in uploaded_images:

            image = vision.Image(content=image)
            response = client.document_text_detection(image=image)

            # Extract the text from the response
            response_text = response.full_text_annotation.text
            # Perform spellcheck on the extracted text
            response_text = ExtractionService.spellcheck_text(response_text)
            # Add the extracted text to the list
            extracted_texts.append(response_text)

            # Check for errors
            if response.error.message:
                raise Exception(
                    '{}\nFor more info on error messages, check: '
                    'https://cloud.google.com/apis/design/errors'.format(
                        response.error.message))

        

        return extracted_texts




    #@staticmethod
    #def extract_text_from_txt(file: io.BytesIO) -> str:
        # Extract text from a text file
    #    text = file.read()
    #    # Ensure text is decoded if it's in bytes
    #    if isinstance(text, bytes):
    #        text = text.decode("utf-8")
    #    return text

    @staticmethod
    def get_model_for_editing(file_type: str) -> str:
        allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
        if file_type in allowed_image_types:
            return "gpt-4"
        else:
            return "gpt-3.5-turbo"

    @staticmethod
    def format_recipe_text(recipe_text: str) -> Recipe:
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        # Create the output parser -- this takes in the output from the model and parses it into a Pydantic object that mirrors the schema
        output_parser = PydanticOutputParser(pydantic_object=Recipe)

        
        # Create the prompt template from langchain to query the model and parse the output
        # We will format system, user, and AI messages separately and then pass the formatted messages to the model to
        # generate the recipe in a specific format using the output parser

        # Define the first system message.  This let's the model know what type of output\
        # we are expecting and in what format it needs to be in.
        prompt = PromptTemplate(
            template = "You are a master chef helping a user reformat a recipe from recipe text {recipe_text} that\
                    has been extracted from an uploaded recipe that may contain errors and / or be in a different format.\
                    The formatted recipe text {recipe_text} should be returned in this format{format_instructions}.",
            input_variables = ["recipe_text"],
            partial_variables = {"format_instructions": output_parser.get_format_instructions()}
        )

            # Generate the system message prompt
        system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)

        # Define the user message.  This is the message that will be passed to the model to generate the recipe.
        human_template = "Help me format the recipe text {recipe_text} I have uploaded.  Please ensure the returned prep time, cook time, and total time are integers in minutes.  If any of the times are n/a\
                    as in a raw dish, return 0 for that time.  Round the times to the nearest 5 minutes to provide a cushion and make for a more readable recipe.  Estimate the number of calories per serving if not provided."
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)    
        
        # Create the chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        # format the messages to feed to the model
        messages = chat_prompt.format_prompt(recipe_text=recipe_text).to_messages()

        # Create a list of models to loop through in case one fails
        models = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo"]

        # Loop through the models and try to generate the recipe
        for model in models:
            try:
                chat = ChatOpenAI(model_name = model, temperature = 1, max_retries=3)

                recipe = chat(messages).content

                parsed_recipe = output_parser.parse(recipe)
                
                # We need to create a "recipe_text" field for the recipe to be returned to the user
                # This will be a string that includes all of the recipe information so that we can
                # Use it for functions downstream
                parsed_recipe.recipe_text = f"{parsed_recipe.name}\n\n{parsed_recipe.desc}\n\n{parsed_recipe.ingredients}\n\n{parsed_recipe.directions}\n\nPrep Time: {parsed_recipe.preptime}\nCook Time: {parsed_recipe.cooktime}\nTotal Time: {parsed_recipe.totaltime}\n\nServings: {parsed_recipe.servings}\n\nCalories: {parsed_recipe.calories}"

                return parsed_recipe

            except (requests.exceptions.RequestException, openai.error.APIError):
                continue




