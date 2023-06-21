# services/recipe_service.py

import openai
import os
import requests
from ..utils.recipe_extract import (
    extract_recipe_name,
    extract_ingredients,
    extract_times,
    extract_steps,
    is_valid_recipe,
)
from typing import List, Optional
from ..models.recipe import Recipe

def execute_generate_recipe(specifications: str, additional_messages: Optional[List[str]] = None, openai_api_key: str, openai_org: str):
    # Set your API key
    openai.api_key = openai_api_key
    openai.organization = openai_org

    # Initialize variables
    recipe = ''
    ingredients = []
    recipe_name = "Invalid Recipe"
    steps = []
    cook_time, prep_time, total_time = 0, 0, 0

    # TODO: We need to rework the model to parse the output to align with
    # the Recipe class model.  We should try to use Pydantic Output Parsing
    # to do this for efficiency and accuracy. We can also look into OpenAI's
    # new API to see if it can help us with this.
    
    
    # Messages for model
    messages = [
        # @TODO Add messages here...
    ]
    if additional_messages:
        messages += additional_messages

    while not is_valid_recipe(recipe):
        try:
            # Generate recipe and extract its elements here...

        except (requests.exceptions.RequestException, openai.error.APIError):
            # Try another model in case of failure...

    return {
        "recipe": recipe,
        "recipe_name": recipe_name,
        "ingredients": ingredients,
        "cook_time": cook_time,
        "prep_time": prep_time,
        "total_time": total_time,
        "steps": steps,
    }

