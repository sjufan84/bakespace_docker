""" Define the chat routes for the FastAPI application. """
from typing import Union
from dotenv import load_dotenv
import openai
from openai import OpenAIError
from app.models.recipe import Recipe
from app.dependencies import get_openai_api_key, get_openai_org

load_dotenv()

# Get the OpenAI API key
openai.api_key = get_openai_api_key()
openai.organization = get_openai_org()

# Parser tool
def parse_recipe(recipe:Union[Recipe, str, dict]) -> Union[Recipe, dict]:
    """ Parse the recipe from the model response. """
    # Format a claude prompt to parse the recipe
    messages = [
        {
            "role": "system", "content": f""" Please
            parse this recipe text {recipe} into a\
            Recipe object {Recipe}.  Make sure to include all of of the required fields.\
            If there are any missing fields, please fill them in with the appropriate\
            values as best you can.  Return only the Recipe object."""
        }
    ]
    models = ["gpt-4-0613", "gpt-4-0613", "gpt-4", "gpt-3.5-turbo-0613"]
    # Iterate through the models until you get a successful response
    for model in models:
        try:
            response = openai.ChatCompletion.create(
                model = model,
                messages = messages,
                temperature = 0,
                max_tokens = 150
            )
            new_recipe = response.choices[0].message.content
            return new_recipe

        except OpenAIError as e:
            print(f"Error with model {model}: {e}")
            continue
