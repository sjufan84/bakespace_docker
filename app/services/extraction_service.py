""" 
The extraction service that handles the extraction of text from pdf, image, and text files.
It also handles the spellcheck of the extracted text. The extracted text is then passed to 
the formatting service to be formatted into a recipe and then returned to the user as a 
Recipe object in the same format as the Bakespace data model.
"""
from typing import List
import os
from dotenv import load_dotenv
from fastapi import HTTPException
#from google.cloud import vision
#from spellchecker import SpellChecker
#import pdfplumber
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
from app.models.recipe import Recipe
from app.middleware.session_middleware import RedisStore

load_dotenv()

# Load the environment variables
openai.api_key = os.getenv("OPENAI_KEY2")
openai.organization = os.getenv("OPENAI_ORG2")

class ExtractionService:
    def __init__(self, store: RedisStore = None):
        self.store = store
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
                    The formatted recipe should be returned in as close to the following format as possible: {format_instructions}.  If any of\
                    the fields are not specificied in the recipe text {recipe_text}, do your best to estimate the values.",
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

                parsed_recipe = output_parser.parse(recipe)

            except (requests.exceptions.RequestException, openai.error.APIError):
                continue
        
        return parsed_recipe

        
    def extract_text_file_contents(self, files) -> str:
        """ Extract the text from the text file."""
        total_file_contents = ''
        for file in files:
            file_contents = file
            file_contents = self.spellcheck_text(file_contents)
            total_file_contents += file_contents
        return file_contents

    def extract_pdf_file_contents(self, files) -> str:
        file_contents = ''
        for file in files:
            pdf = pdfplumber.open(file)
            for page in pdf.pages:
                file_contents += page.extract_text()
                file_contents = self.spellcheck_text(file_contents)
        return file_contents

    def extract_image_text(self, files: List[bytes]) -> str:
        credentials = get_google_vision_credentials() # pylint: disable=no-member
        client = vision.ImageAnnotatorClient(credentials=credentials) # pylint: disable=no-member
        total_response_text = ''
        for file in files:
            image = vision.Image(content=file) # pylint: disable=no-member
            response = client.document_text_detection(image=image)# pylint: disable=no-member
            response_text = response.full_text_annotation.text # pylint: disable=no-member
            response_text = self.spellcheck_text(response_text) # pylint: disable=no-member
            total_response_text += response_text
        return response_text