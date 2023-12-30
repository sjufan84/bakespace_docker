""" OpenAI and local functions related to recipes """
import logging
import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAIError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.dependencies import get_openai_client  # noqa: E402
from services.anthropic_service import AnthropicRecipe  # noqa: E402
from app.utils.redis_utils import save_recipe  # noqa: E402

# Load environment variables
load_dotenv()

# Set up the client
client = get_openai_client()

serving_size_dict = {
    "Family-Size": 4,
    "For Two": 2,
    "For One": 1,
    "Potluck-Size": 20
}

# Establish the core models that will be used by the chat service
core_models = [
    "gpt-3.5-turbo-1106", "gpt-4-1106-preview", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo"
]

def create_recipe(specifications: str, serving_size: str):
    """ Generate a recipe based on the specifications provided asynchronously """
    if serving_size in serving_size_dict.keys():
        serving_size = serving_size_dict[serving_size]
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert chef helping to create a unique recipe.
            Please consider the user's specifications: '{specifications}'
            and their desired serving size: '{serving_size}'.
            Generate a creative and appealing recipe and format the output
            as a JSON object following this schema:
            Recipe Name (recipe_name): A unique and descriptive title for the recipe.
            Ingredients (ingredients): A list of ingredients required for the recipe.
            Directions (directions): Step-by-step instructions for preparing the recipe.
            Preparation Time (prep_time): Optional[Union[str, int] The time taken for preparation in minutes.
            Cooking Time (cook_time): Optional[Union[str, int]] The cooking time in minutes, if applicable.
            Serving Size (serving_size): Optional[Union[str, int]] A description of the serving size.
            Calories (calories): Optional[Union[str, int]] Estimated calories per serving, if known.
            Fun Fact (fun_fact): Optional[str] An interesting fact about the recipe or its ingredients.

            Ensure that the recipe is presented in a clear and organized manner,
            adhering to the 'AnthropicRecipe' {AnthropicRecipe} class structure
            as outlined above."""
        },
    ]

    models = core_models

    for model in models:
        try:
            logging.debug("Trying model: %s.", model)
            # Assuming client has an async method for chat completions
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.75,
                top_p=1,
                max_tokens=750,
                response_format={"type": "json_object"}
            )
            chef_response = response.choices[0].message.content
            try:
              recipe = json.loads(chef_response)
              save_recipe(recipe["recipe_name"], chef_response)
            except Exception as e:
              print(f"Error saving recipe to Redis: {str(e)}")
            return chef_response
        except OpenAIError as e:
            logging.error("Error with model: %s. Error: %s", model, e)
            continue

    return None  # Return None or a default response if all models fail

# Create recipe tool
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

# ---------------------------------------------------------------------------------------------------------------'''

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
            as a JSON object with the following schema:\n\n
            Recipe Name (recipe_name): A unique and descriptive title for the recipe.
            Ingredients (ingredients): A list of ingredients required for the recipe.
            Directions (directions): Step-by-step instructions for preparing the recipe.
            Preparation Time (prep_time): Optional[Union[str, int] The time taken for preparation in minutes.
            Cooking Time (cook_time): Optional[Union[str, int]] The cooking time in minutes, if applicable.
            Serving Size (serving_size): Optional[Union[str, int]] A description of the serving size.
            Calories (calories): Optional[Union[str, int]] Estimated calories per serving, if known.
            Fun Fact (fun_fact): Optional[str] An interesting fact about the recipe or its ingredients.

            Ensure that the recipe is presented in a clear and organized manner, adhering
            to the 'AnthropicRecipe' {AnthropicRecipe} class structure as outlined above."""
        },
    ]

    # models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
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
                "type": "object",
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
async def format_recipe(recipe_text: str):
    """ Extract and format the text from the user's files. """
    messages = [
        {
            "role" : "system", "content" : f"""You are a master chef helping a user
            format a recipe that they have uploaded.  This may be extracted from a photo of a
            recipe, so you may need to infer or use your knowledge as a master chef to fill out
            the rest of the recipe.  The extracted recipe text is {recipe_text}.  The goal is
            to return the recipe as a JSON object in the following format:\n\n
            Recipe Name (recipe_name): A unique and descriptive title for the recipe.
            Ingredients (ingredients): A list of ingredients required for the recipe.
            Directions (directions): Step-by-step instructions for preparing the recipe.
            Preparation Time (prep_time): The time taken for preparation in minutes.
            Cooking Time (cook_time): The cooking time in minutes, if applicable.
            Serving Size (serving_size): A description of the serving size.
            Calories (calories): Estimated calories per serving, if known.
            Fun Fact (fun_fact): An interesting fact about the recipe or its ingredients.\n\n
            as in the AnthropicRecipe {AnthropicRecipe.schema()} schema\n\n
            If you cannot fill out the entire schema, that is okay.  Just fill out as much as you
            can and infer the rest or leave it blank.  The user will then have the chance to have
            you adjust the recipe later.  Return only the recipe object.""",
        }
    ]

    # models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
    models = ["gpt-4-1106-preview", "gpt-4"]
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
