""" OpenAI and local functions related to recipes """
import logging
import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI
from openai import OpenAIError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.recipe import Recipe, FormattedRecipe # noqa: E402
from fastapi import Depends # noqa: E402
from app.services.recipe_service import RecipeService # noqa: E402
from app.middleware.session_middleware import RedisStore, get_redis_store # noqa: E402

# Load environment variables
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_KEY2")
organization = os.getenv("OPENAI_ORG2")

# Set up the client
client = OpenAI(api_key=api_key, organization=organization, max_retries=3, timeout=10)

def get_recipe_service(store: RedisStore = Depends(get_redis_store)):
    """ Define a function to get the recipe service.  Takes in session_id and store."""
    return RecipeService(store=store)

serving_size_dict = {
  "Family-Size": 4,
  "For Two": 2,
  "For One": 1,
  "Potluck-Size": 20
}

# Convert the Recipe model to a dictionary
recipe_dict = Recipe.schema()
# Establish the core models that will be used by the chat service
core_models = ["gpt-3.5-turbo-1106", "gpt-3.5-turbo-1106", 
"gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo"]

# Create Recipe Functions
def create_recipe(specifications: str, serving_size: str):
    """ Generate a recipe based on the specifications provided """
    messages = [
        {
            "role": "system", "content": f"""You are a master chef helping a user
                create a recipe based on their specifications {specifications} and the
                serving size {serving_size_dict[serving_size]}.  Even if the specifications are just a dish name or type,
                go ahead and create a recipe.  Make sure the recipe name is fun and unique. 
                Return the recipe as a JSON object with the same
                schema as the Recipe {recipe_dict} model.  Return only the recipe object.""",
        },
    ]
    # Create a list of models to loop through in case one fails
    models = core_models

    # Loop through the models and try to generate the recipe
    for model in models:
        try:
            logging.debug("Trying model: %s.", model)
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=1,
                top_p=1,
                max_tokens=750,
                response_format = {"type" : "json_object"}
            )
            # Get the chef response
            chef_response = response.choices[0].message.content
  
            # Return the chef response
            return chef_response   
        except OpenAIError as e:
            logging.error("Error with model: %s. Error: %s", model, e)
            continue




        
create_recipe_tool = {
  "name": "create_new_recipe",
  "description": "Create a new recipe for the user based on their specifications.",
  "parameters": {
    "type": "object",
    "properties": {
      "specifications": {
        "type": "string",
        "description": "The specifications for the recipe the user wants you to create."
      },
      "serving_size": {
        "type": "string",
        "description": "The serving size the user would like for the recipe."
      }
    },
    "required": [
      "specifications",
      "serving_size"
    ]
  }
}

# ---------------------------------------------------------------------------------------------------------------

# Adjust recipe functions
def adjust_recipe(recipe: dict, adjustments: str):
        """ Chat a new recipe that needs to be generated based on\
        a previous recipe. """
        # Set the chef style
        messages = [
            {
                "role": "system", "content": f"""You are helping a user adjust a recipe {recipe}\
                that you generated for them earlier.\
                The adjustments are {adjustments}.  Return the adjusted recipe\
                as a JSON object with the same schema as the Recipe {Recipe} model.\
                Return only the recipe object.""",
            },
            {
                "role": "user", "content": "Hi chef, thanks for the recipe you generated\
                for me earlier. Can you help me adjust it?"
            }
        ]

        #models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
        models = core_models
        for model in models:
            try:
                response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.75,
                top_p=0.75,
                max_tokens=1000,
                response_format = {"type" : "json_object"}
            )
                recipe = response.choices[0].message.content
                return recipe

            except TimeoutError as a:
                print(f"Timeout error: {str(a)}")
                continue

# Adjust recipe tool
adjust_recipe_tool = {
  "name": "adjust_recipe",
  "description": "Adjust a recipe for the user based on their specifications.",
  "parameters": {
    "type": "object",
    "properties": {
      "adjustments": {
        "type": "string",
        "description": "The adjustments the user wants you to make to the recipe."
      },
      "recipe": {
        "type": "string",
        "description": "The recipe the user wants you to adjust."
      }
    },
    "required": [
      "adjustments",
      "recipe"
    ]
  }
}

# ---------------------------------------------------------------------------------------------------------------
# Add the function to extract and format recipe text from the user's files
def format_recipe(recipe_text: str):
    """ Extract and format the text from the user's files. """
    messages = [
        {
            "role" : "system", "content" : f"""You are a master chef helping a user
            format a recipe that they have uploaded.  This may be extracted from a photo of a 
            recipe, so you may need to infer or use your knowledge as a master chef to fill out
            the rest of the recipe.  The extracted recipe text is {recipe_text}.
            The recipe should be returned as a JSON object as close to the same schema as the
            Recipe {FormattedRecipe} model.  Mostly we want the user to be able to save our
            recipe in the database, ask questions about it, etc., so we need it to be as close
            to our schema as possible. If you simply cannot format the recipe, create a new recipe
            that you think will be similar to the one the user uploaded.  Return only the recipe object.""",
        }
    ]

    #models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
    models = ["gpt-3.5-turbo-1106", "gpt-4-1106-preview"]
    for model in models:
        try:
            response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            top_p=0.75,
            max_tokens=1000,
            response_format = {"type" : "json_object"}
        )
            recipe = response.choices[0].message.content
            return recipe

        except TimeoutError as a:
            print(f"Timeout error: {str(a)}")
            continue

# Adjust recipe tool
adjust_recipe_tool = {
  "name": "adjust_recipe",
  "description": "Adjust a recipe for the user based on their specifications.",
  "parameters": {
    "type": "object",
    "properties": {
      "adjustments": {
        "type": "string",
        "description": "The adjustments the user wants you to make to the recipe."
      },
      "recipe": {
        "type": "string",
        "description": "The recipe the user wants you to adjust."
      }
    },
    "required": [
      "adjustments",
      "recipe"
    ]
  }
}

# ---------------------------------------------------------------------------------------------------------------
# Add the function to do the initial pass over the raw extracted text to return
# to the user for adjustments
def initial_pass(raw_recipe_text: str):
    """ Initial pass over the raw extracted text to return to the user for adjustments """
    messages = [
        {
            "role" : "system", "content" : f"""You are a master chef helping a user
            format a recipe that they have uploaded.  This is your initial pass over the 
            raw recipe text {raw_recipe_text}.  The goal here is to quickly return the text
            to the user in a format where they can make any adjustments they need to before
            re-submitting.  Return the the recipe as close to the same schema as the
            Recipe {FormattedRecipe} model.  Only return the recipe object.  Do not spend
            too much time on this as this is the first pass.  We will do a second pass
            later for more detailed formatting."""
        }
    ]

    #models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
    models = ["gpt-4", "gpt-3.5-turbo-1106", "gpt-4-1106-preview"]
    for model in models:
        try:
            response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            top_p=0.75,
            max_tokens=1000,
        )
            recipe = response.choices[0].message.content
            return recipe

        except TimeoutError as a:
            print(f"Timeout error: {str(a)}")
            continue
