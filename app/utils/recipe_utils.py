""" Define the chat routes for the FastAPI application. """
import os
from typing import Union
from dotenv import load_dotenv
from anthropic import Anthropic, APIConnectionError
from app.models.recipe import Recipe
from app.utils.chat_utils import format_claude_prompt   

load_dotenv()

anthropic = Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

# Parser tool
def parse_recipe(recipe:Union[Recipe, str, dict]) -> Union[Recipe, dict]:
    """ Parse the recipe from the model response. """
    try:
        # Format a claude prompt to parse the recipe
        parse_prompt = f""" Please parse this recipe text {recipe} into a\
        Recipe object {Recipe}.  Make sure to include all of of the required fields.\
        If there are any missing fields, please fill them in with the appropriate\
        values as best you can.  Return only the Recipe object.
        """
        prompt = format_claude_prompt(parse_prompt)
        completion = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=300,
        prompt=f"{prompt}",
        temperature=0
        )
        formatted_recipe = completion.completion
        return formatted_recipe
    except APIConnectionError as k:
        print("A connection error occurred: ", k)
        return {"unparsed_recipe": recipe, "error": "Could not parse recipe"}
        