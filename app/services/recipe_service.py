""" This module contains the recipe service class. """
import logging
from redis import RedisError
from app.middleware.session_middleware import RedisStore

logging.basicConfig(level=logging.DEBUG)

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
    def __init__(self, store: RedisStore = None):
        self.store = store
        self.session_id = self.store.session_id
        self.recipe = self.load_recipe()
        if not self.recipe:
            self.recipe = None
        self.chef_type = self.store.redis.get(f'{self.session_id}:chef_type')

    # Create a function to be able to load a recipe from the store by the recipe_name
    def load_recipe(self):
        """ Load a recipe from the store by the recipe_name """
        try:
            # Load the recipe hash from redis with all of the keys
            recipe_json = self.store.redis.hgetall(f'{self.session_id}_recipe')
            if recipe_json:
                return recipe_json
            else:
                return None
        except RedisError as e:
            print(f"Failed to load recipe from Redis: {e}")
            return None

    # Create a function to save a recipe to the store by the recipe_name
    def save_recipe(self, recipe):
        """ Save a recipe to the store by the recipe_name """
        try:
            # Save the recipe to redis
            self.store.redis.hmset(f'{self.session_id}_recipe', mapping = recipe)
        except RedisError as e:
            print(f"Failed to save recipe to Redis: {e}")
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
