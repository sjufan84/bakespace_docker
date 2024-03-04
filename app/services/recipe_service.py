""" OpenAI and local functions related to recipes """
import logging
import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAIError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.dependencies import get_openai_client  # noqa: E402
from app.models.recipe import FormattedRecipe, Recipe  # noqa: E402
# from app.services.anthropic_service import AnthropicRecipe  # noqa: E402
# from app.utils.redis_utils import save_recipe  # noqa: E402

# Load environment variables
load_dotenv()

# Set up the client
client = get_openai_client()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

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

async def filter_query(text: str) -> bool:
    """ Determine if the text is related to food. """
    messages = [
        {
            "role": "system",
            "content": f"""You are a master chef helping a user determine if a text query is related to food.
            The query is: '{text}'. Return a boolean value indicating whether
            or not the query is related to food.
            This is a filter to ensure that the user is only submitting food-related queries
            to the recipe service
            and not spam, advertisements, or inappropriate content.  Simply return True or False."""
        }
    ]
    models = core_models
    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.5,
                top_p=0.75,
                max_tokens=1000
            )
            is_food = response.choices[0].message.content
            return is_food

        except OpenAIError as e:
            logger.error("Error with model: %s. Error: %s", model, e)
            continue

# ---------------------------------------------------------------------------------------------------------------

async def create_recipe(specifications: str, serving_size: str = "4"):
    """ Generate a recipe based on the specifications provided asynchronously """
    # First check to make sure the query is related to food
    query = specifications + serving_size
    is_food = await filter_query(query)
    if is_food == "False":
        logger.debug("Query is not related to food.")
        return json.dumps(
            {
                "recipe_name": '',
                "ingredients": [],
                "directions": [],
                "prep_time": 0,
                "cook_time": 0,
                "serving_size": '',
                "calories": 0,
                "fun_fact": '',
                "is_food": False
            }
        )
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
            Preparation Time (prep_time): Union[str, int] The time taken for preparation in minutes.
            Cooking Time (cook_time): Optional[Union[str, int]] The cooking time in minutes, if applicable.\
            Will be null if the recipe is raw or doesn't require cooking.
            Serving Size (serving_size): Union[str, int] A description of the serving size.
            Calories (calories): Optional[Union[str, int]] Estimated calories per serving, if known.
            Fun Fact (fun_fact): str An interesting and unique fact about the recipe or its ingredients.\
            Should be a conversation starter, maybe a historical fact\
            or something else that people would find fascinating,\
            not just a generic fact about the ingredients or recipe.
            Pairs With (pairs_with): str A creative pairing for the recipe.  It could be a wine pairing, side\
            dish, etc.  Whatever seems the most appropriate for the recipe and will delight the user.

            Ensure that the recipe is presented in a clear and organized manner,
            adhering to the 'Recipe' {Recipe} class structure
            as outlined above."""
        }
    ]

    models = core_models

    for model in models:
        try:
            logger.info("Trying model: %s for recipe generation.", model)
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
            logger.info(f"New recipe generated: {chef_response}")
            return chef_response

        except OpenAIError as e:
            logger.error("Error with model: %s. Error: %s", model, e)
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
            Preparation Time (prep_time): Union[str, int] The time taken for preparation in minutes.
            Cooking Time (cook_time): Union[str, int] The cooking time in minutes, if applicable.  Null
            for raw recipes or recipes that don't require cooking.
            Serving Size (serving_size): Union[str, int] A description of the serving size.
            Calories (calories): Optional[Union[str, int]] Estimated calories per serving, if known.
            Fun Fact (fun_fact): str An interesting fact about the recipe or its ingredients.
            Should be a conversation starter, maybe a historical fact or something
            else that people would find fascinating.
            Pairs With (pairs_with): str A pairing for the recipe.  It could be a wine pairing, side
            dish, etc.  Whatever seems the most appropriate for the recipe.


            Ensure that the recipe is presented in a clear and organized manner, adhering
            to the 'Recipe' {Recipe} class structure as outlined above."""
        },
    ]

    # models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
    models = core_models
    for model in models:
        logger.info("Trying model: %s for adjusting recipe.", model)
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
          logger.info(f"Adjusted recipe generated: {recipe}")
          return recipe

        except OpenAIError as e:
            logger.error("Error with model: %s. Error: %s", model, e)
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
    is_food = await filter_query(recipe_text)
    if is_food == "False":
        logger.debug("Query is not related to food.")
        return json.dumps(
            {
                "recipe_name": '',
                "ingredients": [],
                "directions": [],
                "prep_time": 0,
                "cook_time": 0,
                "serving_size": '',
                "calories": 0,
                "is_food": False
            }
        )
    messages = [
        {
            "role" : "system", "content" :
            f"""You are a master chef helping a user generate a format a recipe that they have uploaded
            {recipe_text}. As closely as possible,
            reformat the recipe and return it as a JSON object in the following format:\n\
            Recipe Name (recipe_name): str A unique and descriptive title for the recipe.
            Ingredients (ingredients): List[str] A list of ingredients required for the recipe.
            Directions (directions): List[str] Step-by-step instructions for preparing the recipe.
            Preparation Time (prep_time): Union[str, int] The time taken for preparation in minutes.
            Cooking Time (cook_time): Union[str, int] The cooking time in minutes, if applicable.
            Serving Size (serving_size): Union[str, int] A description of the serving size.
            Pairs With (pairs_with): str A creative pairing for the recipe.  It could be a wine pairing, side\
            dish, etc.  Whatever seems the most appropriate for the recipe and will delight the user.
            Calories (calories): Union[str, int] Estimated calories per serving, if known.  If not, do your\
            best to infer the amount of calories per one serving of the recipe.
            Fun Fact (fun_fact): str An interesting and unique fact about the recipe or its ingredients.\
            Should be a conversation starter, maybe a historical fact\
            or something else that people would find fascinating,\
            not just a generic fact about the ingredients or recipe.\n\n
            If you cannot determine all of the values, do your best to infer the value or leave it blank.
            The user will then have the chance to edit any incorrect values.
            Source: Optional[str] The source of the recipe i.e. AllRecipes, Bakespace, etc. if applicable.

            Ensure that the recipe is presented in a clear and organized manner, adhering
            to the 'FormattedRecipe' {FormattedRecipe} class structure as outlined above."""
        }
    ]
    # models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
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
            logger.info(f"Formatted recipe generated: {recipe} with model {model}.")
            return recipe

        except OpenAIError as e:
            logger.error("Error with model: %s. Error: %s", model, e)
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
