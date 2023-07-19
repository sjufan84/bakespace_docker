""" This module contains the functions to generate a pairing based on the requested pairing
 type and the recipe text. """
import json
import openai
import requests
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
)
from ..dependencies import get_openai_api_key, get_openai_org
from ..models.pairing import Pairing
from ..middleware.session_middleware import RedisStore


class PairingService:
    """ A class to represent the pairing service. """
    def __init__(self, store: RedisStore = None):
        self.store = store or RedisStore()
        self.session_id = self.store.session_id
        pairing_history = self.store.redis.get(f'{self.session_id}_pairing_history')
        if pairing_history:
            self.pairing_history = pairing_history
        else:
            self.pairing_history = []


    def get_pairing(self, recipe: str, pairing_type: str):
        """ Generate a pairing based on the requested pairing type and the recipe text. """
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()
        
        # Create the output parser -- this takes in the output from the model and parses it into a Pydantic object that mirrors the schema
        output_parser = PydanticOutputParser(pydantic_object=Pairing)
        
        # Create the prompt template from langchain to query the model and parse the output
        # We will format system, user, and AI messages separately and then pass the formatted messages to the model to
        # generate the recipe in a specific format using the output parser

        # Define the first system message.  This let's the model know what type of output\
        # we are expecting and in what format it needs to be in.
        
        system_template = PromptTemplate(
            template = "You are a culinary genius creating a pairing of type {pairing_type} based on a\
                            generated recipe {recipe}. Include the pairing text, recipe if necessary,\
                            and the reason why it is an appropriate pairing for the recipe {recipe}. The pairing will have the\
                            following format: {format_instructions}.",
            input_variables = ["pairing_type", "recipe"],
            partial_variables = {"format_instructions": output_parser.get_format_instructions()}      
        )
        
        system_message_prompt = SystemMessagePromptTemplate(prompt = system_template)

        # Define the user message.  This is the message that will be passed to the model to generate the recipe.
        human_template = "Create a pairing for the given recipe."
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)    
        
        # Create the chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        # format the messages to feed to the model
        messages = chat_prompt.format_prompt(recipe=recipe, pairing_type=pairing_type).to_messages()

        # Create a list of models to loop through in case one fails
        models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"]

        # Loop through the models and try to generate the recipe
        for model in models:
            try:
                chat = ChatOpenAI(n=1, model_name = model, temperature = 1, max_retries=3)
                pairings = chat(messages).content
                # Parse the output
                parsed_pairings = output_parser.parse(pairings)

                # Save the pairing to the pairing history
                self.store.redis.append(f'{self.session_id}_pairing_history', json.dumps(dict(parsed_pairings)))

                 # Return the pairing
                return parsed_pairings

            except (requests.exceptions.RequestException, openai.error.APIError):
                continue

       
    
    def get_pairing_history(self):
        """ Get the pairing history for the current session. """
        return self.pairing_history