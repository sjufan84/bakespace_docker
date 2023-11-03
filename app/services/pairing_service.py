""" This module contains the functions to generate a pairing based on the requested pairing
 type and the recipe text. """
import logging
import openai
import requests
from redis import RedisError
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
)
from app.dependencies import get_openai_api_key, get_openai_org
from app.models.pairing import Pairing
from app.middleware.session_middleware import RedisStore


class PairingService:
    """ A class to represent the pairing service. """
    def __init__(self, store: RedisStore = None):
        self.store = store
        self.session_id = self.store.session_id
        self.recipe = self.store.redis.hgetall(f'{self.session_id}_pairing')
        if not self.recipe:
            self.recipe = None
        self.pairing = self.load_pairing()
        if not self.pairing:
            self.pairing = None

    def get_pairing(self, recipe: str, pairing_type: str):
        """ Generate a pairing based on the requested pairing type and the recipe text. """
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        # Create the output parser -- this takes in the output
        #  from the model and parses it into a Pydantic object that mirrors the schema
        output_parser = PydanticOutputParser(pydantic_object=Pairing)

        # Create the prompt template from langchain to query the model and parse the output
        # We will format system, user, and AI messages separately
        # and then pass the formatted messages to the model to
        # generate the recipe in a specific format using the output parser

        # Define the first system message.  This let's the model know what type of output\
        # we are expecting and in what format it needs to be in.

        system_template = PromptTemplate(
            template = "You are a culinary genius creating a pairing of type\
                            {pairing_type} based on a\
                            generated recipe {recipe}. Include the pairing text, recipe if necessary,\
                            and the reason why it is an appropriate pairing for the recipe {recipe}.\
                            The pairing will have the following format: {format_instructions}.",
            input_variables = ["pairing_type", "recipe"],
            partial_variables = {"format_instructions": output_parser.get_format_instructions()}
        )

        system_message_prompt = SystemMessagePromptTemplate(prompt = system_template)

        # Define the user message.  This is the message that will be
        # passed to the model to generate the recipe.
        human_template = "Create a pairing for the given recipe."
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        # Create the chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                        human_message_prompt])

        # format the messages to feed to the model
        messages = chat_prompt.format_prompt(recipe=recipe, pairing_type=pairing_type).to_messages()

        # Create a list of models to loop through in case one fails
        models = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613",
                "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]

        # Loop through the models and try to generate the recipe
        for model in models:
            try:
                logging.debug("Trying model: %s.", model)
                chat = ChatOpenAI(n=1, model_name=model, temperature=1, max_retries=3)
                pairings = chat(messages).content
                # Parse the output
                parsed_pairings = output_parser.parse(pairings)

                # Convert the keys and values to strings for saving to redis
                redis_dict = {str(key): str(value) for key, value in dict(parsed_pairings).items()}

                # Save the pairing to redis
                self.save_pairing(redis_dict)

                # Return the pairing
                return parsed_pairings

            except (requests.exceptions.RequestException, openai.error.APIError):
                continue

    def load_pairing(self):
        """ Load the pairing from redis. """
        try:
            pairing = self.store.redis.hgetall(f'{self.session_id}_pairing')
            if pairing:
                return pairing
            else:
                return None
        except RedisError as e:
            print(f"Failed to load pairing from Redis: {e}")
            return None

    def save_pairing(self, pairing: dict):
        """ Save the pairing to redis. """
        try:
            self.store.redis.hmset(f'{self.session_id}_pairing', mapping = pairing)
        except RedisError as e:
            print(f"Failed to save pairing to Redis: {e}")

        return pairing

    def delete_pairing(self):
        """ Delete the pairing from redis. """
        try:
            self.store.redis.delete(f'{self.session_id}_pairing')
        except RedisError as e:
            print(f"Failed to delete pairing from Redis: {e}")

        return {"message": "Pairing deleted."}

    def format_recipe_text(self, recipe_text: str):
        """ Format the recipe text into a recipe object. """
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        # Define the messages for the prompt:
        messages = [
            {
            "role": "system", "content": f"Format the recipe text {recipe_text}\
            that has been extracted from\
            a recipe file that the user has uploaded.  Return the formatted recipe text as a string in\
            a standard recipe format.  If there is information that seems missing or unclear,\
            do your best to fill in the missing information."
            },
            {
            "role": "user", "content": f"""Format the recipe text {recipe_text} 
            into a standard recipe format please."""
            }
        ]

        # Create a list of models to loop through in case one fails
        models = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613"]

        # Loop through the models and try to generate the recipe
        for model in models:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.9,
                    max_tokens=1500,
                    top_p=1,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                )

                recipe = response.choices[0].message.content
                return recipe

            except (requests.exceptions.RequestException, openai.error.APIError):
                continue

        return recipe
