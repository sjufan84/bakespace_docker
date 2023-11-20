""" This module contains the recipe service class. """
import logging
<<<<<<< HEAD
import os
from dotenv import load_dotenv
import openai
from anthropic import Anthropic, APIConnectionError
from redis.exceptions import RedisError
from app.models.recipe import Recipe
from app.middleware.session_middleware import RedisStore
from app.utils.chat_utils import format_claude_prompt
from app.utils.recipe_utils import parse_recipe

load_dotenv() # Load the .env file
=======
from redis import RedisError
from app.middleware.session_middleware import RedisStore
>>>>>>> 8527395785d28333fd5240a8229180810d928d69

logging.basicConfig(level=logging.DEBUG)
# Create a dictionary to house the chef data to populate the chef model
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

# Create a chat-gpt object
openai.api_key = os.getenv("OPENAI_KEY2")
openai.organization = os.getenv("OPENAI_ORG2")

anthropic = Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

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
        "model_name" : "ft:gpt-3.5-turbo-0613:david-thomas:gr-sous-chef:86TgiHTW",
        "style": "professional chef in the style of Gordon Ramsey"
    },
    "general": {
        "model_name": "gpt-turbo-0613",
        "style": "master sous chef in the style of the best chefs in the world"
    }
}

# Establish the core models that will be used by the chat service
core_models = ["gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo"]

# Create a class for the recipe service
class RecipeService:
    """ A class to represent the recipe service. """
    def __init__(self, store: RedisStore = None, chef_choice: str = None):
        self.store = store
        self.session_id = self.store.session_id
        self.recipe = self.load_recipe()
        if not self.recipe:
            self.recipe = None
<<<<<<< HEAD
        self.chef_choice = chef_choice
        if not self.chef_choice:
            self.chef_choice = "general"

    # Create a function to be able to load a recipe from the store by the recipe_name
    def load_recipe(self):
        """ Load the session recipe from the store"""
=======
        self.chef_type = self.store.redis.get(f'{self.session_id}:chef_type')

    # Create a function to be able to load a recipe from the store by the recipe_name
    def load_recipe(self):
        """ Load a recipe from the store by the recipe_name """
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
        try:
            # Load the recipe hash from redis with all of the keys
            recipe_json = self.store.redis.hgetall(f'{self.session_id}_recipe')
            if recipe_json:
                return recipe_json
<<<<<<< HEAD
            return None
=======
            else:
                return None
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
        except RedisError as e:
            print(f"Failed to load recipe from Redis: {e}")
            return None

    # Create a function to save a recipe to the store by the recipe_name
    def save_recipe(self, recipe):
<<<<<<< HEAD
        """ Save a recipe to the store by session_id """
        try:
            # Save the recipe to redis as a dictionary
            self.store.redis.hmset(f'{self.session_id}_recipe', mapping=recipe)
        except AttributeError as e:
            # Save the recipe as a string
            self.store.redis.set(f'{self.session_id}_recipe', recipe)
            print(f"Failed to save recipe dict to Redis: {e}.  Saving as string.")
=======
        """ Save a recipe to the store by the recipe_name """
        try:
            if isinstance(recipe, dict):
                # Save the recipe to redis
                self.store.redis.hmset(f'{self.session_id}_recipe', mapping = recipe)
            else:
                return {"message": "Recipe must be a dictionary."}
        except RedisError as e:
            print(f"Failed to save recipe to Redis: {e}")
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
        return recipe

    # Create a function to delete a recipe from the store by the recipe_name
    def delete_recipe(self):
        """ Delete a recipe from the store by the recipe_name """
        try:
            # Delete the recipe from redis
            self.store.redis.delete(f'{self.session_id}_recipe')
        except RedisError as e:
            print(f"Failed to delete recipe from Redis: {e}")
        return {"message": "Recipe deleted."}
<<<<<<< HEAD

    def generate_recipe(self, specifications: str, chef_type: str = "general"):
        """ Generate a recipe based on the user's specifications. """
        #claude_prompt = format_claude_prompt(f""" 
        #Please generate a recipe for the user based on the following\
        #specifications: {specifications}.  You are a master chef of type {chef_type}.\
        #acting as the user's personal chef. Have fun with the interaction with the user and blow\
        #them away with a great recipe!\
        #The recipe in your response should be formatted\
        #as {Recipe}. Please make sure to include all of the required fields in the recipe.""")

        # Create the chat object
        #try:
        #    response = anthropic.completions.create(
        #        model="claude-2",
        #        prompt=claude_prompt,
        #        max_tokens_to_sample=300,
        #        timeout=60,
        #        temperature=1,
        #        top_p=1,
        #    )
            # Parse the recipe
        #    recipe = parse_recipe(response.completion)
            # Create a dictionary to house the recipe data to populate the recipe model
            # Save the recipe to the store
        #    self.save_recipe(recipe)

        #    return {"recipe": recipe, "response": response.completion}
        #except APIConnectionError as e:
        #    print(f"A connection error {e} occurred")
        models = ["gpt-4-0613", "gpt-4"]
        messages = [
            {
                "role": "system", "content": f"""You are a master chef of\
                type {openai_chat_models[chef_type]["style"]}\
                generating a recipe for a user based on their specifications {specifications}.\
                Make sure that the recipe that you generate is formatted as a Recipe object\
                {Recipe}.  Please make sure to include all of the required fields in the recipe\
                and have fun with the interaction with the user and blow them away with a great\
                recipe!"""
            },
            {
                "role": "user", "content": "Hi Chef, create a recipe for me based on my specifications."
            }
        ]
        for model in models:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=1,
                    top_p=1,
                    max_tokens=500
                )
                # Parse the recipe'
                recipe = parse_recipe(response.choices[0].message.content)
                # Save the recipe to the store
                self.save_recipe(recipe)

                return {"recipe": recipe, "response": response.choices[0].message.content}
            except TimeoutError as a:
                print(f"Timeout error: {str(a)}")
                continue
            except APIConnectionError as error:
                print(f"A connection error {error} occurred")
                continue
=======
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
