""" OpenAI and local functions related to recipes """
import logging
import os
import time
import sys
import json
import anthropic
from dotenv import load_dotenv
from openai import OpenAIError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.dependencies import (
    get_anthropic_client, get_openai_client, get_query_filter_client,
)  # noqa: E402
from app.models.recipe import FormattedRecipe, Recipe  # noqa: E402
# from app.services.anthropic_service import AnthropicRecipe  # noqa: E402
# from app.utils.redis_utils import save_recipe  # noqa: E402

# Load environment variables
load_dotenv()

# Set up the client
client = get_openai_client()
anthropic_client = get_anthropic_client()


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
    "gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-4-turbo-preview", "gpt-4-1106-preview"
]

test_models = ["gpt-4-turbo-preview", "gpt-4-1106-preview"]

async def filter_query(text: str) -> bool:
    """ Determine if the text is related to food. """
    client = get_query_filter_client()
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
            logger.info(f"Query {text} is related to food: {is_food}")
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
        logger.debug(f"Query {specifications} is not related to food.")
        raise ValueError("Query is not related to food.")
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

async def claude_recipe(specifications: str, serving_size: str = "4") -> Recipe:
    query = specifications + serving_size
    is_food = await filter_query(query)
    if is_food == "False":
        logger.debug(f"Query {specifications} is not related to food.")
        raise ValueError("Query is not related to food.")
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
        "role": "user",
        "content": f"""Please create a one-of-a-kind, imaginative recipe based on the following
        specifications: '{specifications}' and serving size: '{serving_size}'. Aim to astonish
        and enchant me with your culinary creativity and the recipe's overall appeal.
        The recipe should be unique, engaging, and memorable,
        providing a delightful culinary experience for the user.  Please adhere to the following
        guidelines when creating the recipe:\n\n

        When listing ingredients, follow these guidelines:
        - Highlight ingredients that need advanced work, such as sitting in a marinade or getting thawed,
        chilled, or softened.
        - If an ingredient is used more than once, list the total amount at the place in the ingredient
        list where it is first used, then add "divided." In the method part of the recipe, indicate the
        amount used at each step.
        - Unless a specific size is called for, "eggs" are large, "brown sugar" is light brown sugar,
        "flour" is all-purpose flour, and "sugar" is granulated.

        In the directions, consider the following:
        - Note what prep needs to happen at the beginning and what might
        be saved for later while something is cooking.
        - Provide doneness indicators, such as ways to assess by sight, smell,
        sound, texture, or temperature whether something is cooked correctly.
        - If using the stove-top, indicate the level of heat (e.g., "Simmer over low heat").
        - Be specific with measurements and instructions (e.g., "Scoop out 1
        tablespoon of dough at a time and roll into balls").
        - Mention any specific equipment needed, such as a stand mixer, blender, or food processor.
        - Include storage instructions as the last step, if applicable.

        For the "recipe_name," create a unique and descriptive title that
        captures the essence of the dish
        and intrigues the user. Avoid generic titles and opt
        for something that will stand out and spark curiosity.

        For the "fun_fact," provide an engaging conversation starter,
        such as a fascinating historical tidbit or an unexpected piece of trivia related
        to the recipe or its ingredients. Avoid generic facts and instead opt for something
        that will pique people's interest and spark discussion.

        If the recipe is meant for a child or children's party, make sure that the recipe
        does not have any alcohol or other adult-oriented ingredients.  The recipe should be
        suitable for children and should be fun, engaging, and appropriate for a younger audience.
        The pairing should also be child-friendly and should complement the recipe in a way that
        enhances the overall experience for children.

        When suggesting a pairing for the recipe in the "pairs_with" section,
        think outside the box and propose a creative and exciting accompaniment.
        This could be an unconventional wine pairing, an inventive side dish, or
        any other complementary item that will elevate the overall dining experience.

        Please estimate the calorie count per serving based on your expert judgment,
        and present the recipe in a clear, organized, and detailed manner.
        Kindly return the recipe as a JSON object adhering to the following schema:
        "recipe_name": str,
        "ingredients": List[str],
        "directions": List[str],
        "prep_time": Union[str, int],
        "cook_time": Optional[Union[str, int]],
        "serving_size": Union[str, int],
        "calories": Optional[Union[str, int]],
        "fun_fact": str,
        "pairs_with": str
        """
    },
    {
        "role" : "assistant",
        "content" : '{'
    }
]

    system_message = """You are a master chef with a flair for innovation and creativity in the kitchen.
    Your goal is to create unique, surprising, and delightful recipes that will captivate and inspire users.
    Draw upon your extensive culinary knowledge and imagination to craft recipes that are not only delicious
    but also memorable and conversation-worthy."""

    model = "claude-3-sonnet-20240229"

    try:
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            messages=messages,
            system=system_message,
            temperature=0.75,
        )
        logger.debug(f"Claude Response {response}")
        recipe = '{' + response.content[0].text
        logger.info(f"Claude Recipe generated: {recipe}")

        return recipe

    except anthropic.APIConnectionError as e:
        logger.error("The server could not be reached")
        logger.error(e.__cause__)

    except anthropic.RateLimitError as e:
        logger.error("A 429 status code was received; we should back off a bit.")
        logger.error(f"Response: {e.response}")
        # Implementing a basic backoff strategy
        time.sleep(10)  # Sleep for 10 seconds before retrying or proceeding

    except anthropic.APIStatusError as e:
        logger.error("A non-200-range status code was received")
        logger.error(f"Status code: {e.status_code}")
        logger.error(f"Response: {e.response}")

        # Handling specific status codes with custom messages
        if e.status_code == 400:
            logger.error("BadRequestError: The request was invalid.")
        elif e.status_code == 401:
            logger.error("AuthenticationError: Authentication failed.")
        elif e.status_code == 403:
            logger.error("PermissionDeniedError: Access is forbidden.")
        elif e.status_code == 404:
            logger.error("NotFoundError: The requested resource was not found.")
        elif e.status_code == 422:
            logger.error("UnprocessableEntityError:\
            The request was well-formed but was unable to be followed due to semantic errors.")
        elif e.status_code >= 500:
            logger.error("InternalServerError: Something went wrong on the server side.")

    except Exception as e:
        # A generic catch-all for any other unexpected errors
        logger.error("An unexpected error occurred")
        logger.error(e)


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
        logger.debug(f"Query {recipe_text} is not related to food.")
        raise ValueError("Query is not related to food.")
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
