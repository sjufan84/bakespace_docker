""" 
The extraction service that handles the extraction of text from pdf, image, and text files.
It also handles the spellcheck of the extracted text. The extracted text is then passed to 
the formatting service to be formatted into a recipe and then returned to the user as a 
Recipe object in the same format as the Bakespace data model.
"""
from typing import List
import os
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile
from google.cloud import vision
from spellchecker import SpellChecker
import pdfplumber
import openai
import requests
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
        PromptTemplate,
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate
)
from ..dependencies import get_openai_api_key, get_openai_org, get_google_vision_credentials
from ..models.recipe import Recipe
from ..middleware.session_middleware import RedisStore



load_dotenv()

class ExtractionService:
    """ A class to represent the extraction service.  Will be initiated with file(s) that the user
    has uploaded for text extraction."""
    def __init__(self, store: RedisStore = None):
        # Initialize the store
        self.store = store or RedisStore()
        # Initialize the session_id
        self.session_id = self.store.session_id
        
    def spellcheck_text(self, text: str) -> str:
        """ Spellcheck the text. """
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
    
    def format_recipe_text(self, recipe_text: str) -> Recipe:
        """ Format the recipe text into a recipe object. """
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
        models = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613"]

        # Loop through the models and try to generate the recipe
        for model in models:
            try:
                chat = ChatOpenAI(model_name = model, temperature = 1, max_retries=3)

                recipe = chat(messages).content

                try:
                    parsed_recipe = output_parser.parse(recipe)
                
                    # We need to create a "recipe_text" field for the recipe to be returned to the user
                    # This will be a string that includes all of the recipe information so that we can
                    # Use it for functions downstream
                    parsed_recipe.recipe_text = f"{parsed_recipe.name}\n\n{parsed_recipe.desc}\n\n{parsed_recipe.ingredients}\n\n{parsed_recipe.directions}\n\nPrep Time: {parsed_recipe.preptime}\nCook Time: {parsed_recipe.cooktime}\nTotal Time: {parsed_recipe.totaltime}\n\nServings: {parsed_recipe.servings}\n\nCalories: {parsed_recipe.calories}"

                    return parsed_recipe
                except Exception as e:
                    print(e)
                    continue

            except (requests.exceptions.RequestException, openai.error.APIError):
                continue

    def extract_file_contents(self, uploaded_files: List[UploadFile]) -> List[bytes]:
        """Ensure the files are in bytes and return them."""
        # Convert the file to bytes if it's not already
        uploaded_files_bytes = [file.file.read() if not isinstance(file.file, bytes) else file.file for file in uploaded_files]
        return uploaded_files_bytes

    def extract_text_file_contents(self, uploaded_files: List[UploadFile]) -> str:
        """ Extract the text from a text file. Expects a list of text files. """
        # Confirm the file type is text
        for file in uploaded_files:
            if file.content_type != "text/plain":
                raise HTTPException(status_code=400, detail=f"File type {file.content_type} not supported.")
        # Get the bytes content of the files
        uploaded_files_bytes = self.extract_file_contents(uploaded_files)
        
        # Initialize an empty list to hold the extracted texts
        extracted_texts = []
        
        # Loop over each file and decode the contents
        for uploaded_file_bytes in uploaded_files_bytes:
            # Ensure text is decoded if it's in bytes
            file_contents = uploaded_file_bytes.decode("utf-8")
            
            # Perform spellcheck on the file contents
            file_contents = self.spellcheck_text(file_contents)

            # Add the file contents to the list
            extracted_texts.append(file_contents)

        # Concatenate the extracted texts into a single string
        extracted_text = "\n\n".join(extracted_texts)

        return extracted_text



    def extract_pdf_file_contents(self, uploaded_files: List[UploadFile]) -> str:
        """ Extract the text from a pdf file. Expects a list of pdf files. """

        # Initialize an empty list to hold the extracted texts
        extracted_texts = []

        # Confirm the file type is pdf
        for file in uploaded_files:
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail=f"File type {file.content_type} not supported.")

        # Convert the file to bytes if it's not already
        uploaded_files = [file.file.read() if isinstance(file.file, bytes) else file.file for file in uploaded_files]
        
        # Loop over each file and extract the text
        for uploaded_file in uploaded_files:
            # Read the file with PdfFileReader
            pdf = pdfplumber.open(uploaded_file.file)

            # Extract the text from each page
            file_contents = ""

            for page in pdf.pages:
                file_contents += page.extract_text()


            # Perform spellcheck on the file contents
            file_contents = self.spellcheck_text(file_contents)

            # Add the file contents to the list
            extracted_texts.append(file_contents)

            # Concatenate the extracted texts into a single string
            extracted_text = "\n\n".join(extracted_texts)

        # Return the list of file contents as a string
        return extracted_text

    def extract_image_text(self, uploaded_images: List[UploadFile]) -> str:
        """ Extract the text from an image. Expects a list of images."""
        # Check to ensure that the file type is an image
        for file in uploaded_images:
            if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
                raise HTTPException(status_code=400, detail=f"File type {file.content_type} not supported.")
        # Get the Google Vision credentials
        credentials = get_google_vision_credentials()
        # Initialize the Google Vision client
        client = vision.ImageAnnotatorClient(credentials=credentials)
    
        # Initialize a list to hold the extracted texts
        extracted_texts = []

        # Convert the images to bytes if they're not already
        uploaded_images = [image.file.read() if isinstance(image.file, bytes) else image.file for image in uploaded_images]

        # Performs text detection on the image file
        for image in uploaded_images:

            image = vision.Image(content=image)
            response = client.document_text_detection(image=image)

            # Extract the text from the response
            response_text = response.full_text_annotation.text
            # Perform spellcheck on the extracted text
            response_text = self.spellcheck_text(response_text)
            # Add the extracted text to the list
            extracted_texts.append(response_text)

            # Check for errors
            if response.error.message:
                raise HTTPException(
                    status_code=400, detail=f"Error: {response.error.message}"
                )
    # @TODO - is this how we want the texts returned?
        # Concatenate the texts into a single string
        extracted_texts = " ".join(extracted_texts)

        return extracted_texts
