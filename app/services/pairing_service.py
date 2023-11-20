""" This module defines the pairing service. """
from typing import Union
import os
from dotenv import load_dotenv
import openai
<<<<<<< HEAD
from redis.exceptions import RedisError
from app.middleware.session_middleware import RedisStore
from app.models.recipe import Recipe
=======
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
>>>>>>> 8527395785d28333fd5240a8229180810d928d69

load_dotenv() # Load the .env file

# Create a dictionary to house the chef data to populate the chef model
openai_chat_models = {
    "adventurous_chef": {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:ab-sous-chef:86VMDut4",
        "style": "adventurous chef in the style of Anthony Bourdain"
    },
    "home_cook": {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:rr-sous-chef:86U8O9Fp",
        "style": "home cook in the style of Rachel Ray"
    },
    "pro_chef": {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:gr-sous-chef:86TgiHTW",
        "style": "professional chef in the style of Gordon Ramsey"
    },
    "general": {
        "model_name": "gpt-turbo-0613",
        "style": "master sous chef in the style of the best chefs in the world"
    }
}

# Load the openai api key and organization
openai.api_key = os.getenv("OPENAI_KEY2")
openai.organization = os.getenv("OPENAI_ORG2")

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

<<<<<<< HEAD
    async def generate_pairings(self, recipe: Union[str, Recipe, dict],
                                pairing_type: str, chef_type: str="general") -> list:
        """ Generate pairings for a recipe. """
        # Get the openai api key and organization
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()
        # Determine the model and style based on the chef type
        model = openai_chat_models[chef_type]["model_name"]
        style = openai_chat_models[chef_type]["style"]
        messages = [
            {
                "role": "system", "content": f"""You are a master chef of type {style}.
                You are helping a user generate pairings for a recipe {recipe}
                that you generated for them earlier. The pairing type is {pairing_type}.
                Please answer the question as if you were their personal sous chef, helpful
                and in the style of chef they have chosen. Within your personalized response,
                generate the pairings in the form of a list of strings.
                Please do not break character."""
            },
            {
                "role": "user", "content": """Hi chef, thanks for the recipe you generated
                for me earlier. Can you help me generate pairings for it?"""
            }
        ]
        models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
        for model in models:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=1,
                    top_p=1,
                    max_tokens=500
                )
                pairings = response.choices[0].message.content.split(",")
                return {"response": response.choices[0].message.content, "pairings": pairings}
            except TimeoutError as e:
                print(f"Timeout error: {str(e)}")
                continue
            except RuntimeError as e:
                print(f"Failed to generate pairings: {str(e)}")
=======
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
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
                continue

    def load_pairing(self):
        """ Load the pairing from redis. """
        try:
            pairing = self.store.redis.hgetall(f'{self.session_id}_pairing')
            if pairing:
                return pairing
<<<<<<< HEAD
        except RedisError as e:
            print(f"Failed to load pairing from Redis: {str(e)}")
        return None
=======
            else:
                return None
        except RedisError as e:
            print(f"Failed to load pairing from Redis: {e}")
            return None
>>>>>>> 8527395785d28333fd5240a8229180810d928d69

    def save_pairing(self, pairing: dict):
        """ Save the pairing to redis. """
        try:
<<<<<<< HEAD
            self.store.redis.hmset(f'{self.session_id}_pairing', mapping=pairing)
        except RedisError as e:
            print(f"Failed to save pairing to Redis: {str(e)}")
=======
            self.store.redis.hmset(f'{self.session_id}_pairing', mapping = pairing)
        except RedisError as e:
            print(f"Failed to save pairing to Redis: {e}")

>>>>>>> 8527395785d28333fd5240a8229180810d928d69
        return pairing

    def delete_pairing(self):
        """ Delete the pairing from redis. """
        try:
            self.store.redis.delete(f'{self.session_id}_pairing')
        except RedisError as e:
<<<<<<< HEAD
            print(f"Failed to delete pairing from Redis: {str(e)}")
        return {"message": "Pairing deleted."}
=======
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
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
