""" This module defines the pairing service. """
from typing import Union
import os
from dotenv import load_dotenv
import openai
from redis.exceptions import RedisError
from app.middleware.session_middleware import RedisStore
from app.models.recipe import Recipe

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
                continue

    def load_pairing(self):
        """ Load the pairing from redis. """
        try:
            pairing = self.store.redis.hgetall(f'{self.session_id}_pairing')
            if pairing:
                return pairing
        except RedisError as e:
            print(f"Failed to load pairing from Redis: {str(e)}")
        return None

    def save_pairing(self, pairing: dict):
        """ Save the pairing to redis. """
        try:
            self.store.redis.hmset(f'{self.session_id}_pairing', mapping=pairing)
        except RedisError as e:
            print(f"Failed to save pairing to Redis: {str(e)}")
        return pairing

    def delete_pairing(self):
        """ Delete the pairing from redis. """
        try:
            self.store.redis.delete(f'{self.session_id}_pairing')
        except RedisError as e:
            print(f"Failed to delete pairing from Redis: {str(e)}")
        return {"message": "Pairing deleted."}
