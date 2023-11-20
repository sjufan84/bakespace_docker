""" Define the chat routes for the FastAPI application. """
<<<<<<< HEAD
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
        
=======
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

# Create a dictionary to house the chef data to populate the chef model
openai_chat_models = {
  "adventurous_chef": {
    "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:ab-sous-chef:86VMDut4",
    "style": "snarky chef in the style of Anthony Bourdain.  Should 'yank the user's chain'\
        in a fun and playful manner, while also pushing them to test and try new things."
  },
    "home_cook": {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:rr-sous-chef:86U8O9Fp",
        "style": "home cook in the style of Rachel Ray"
    },
    "pro_chef": {
        "model_name" : "ft:gpt-3.5-turbo-0613:david-thomas:gr-sous-chef:86TgiHTW",
        "style": "pro chef in the style of Gordon Ramsay.  Should have high expectations,\
        elevated suggestions, and push the user to test the boundaries of their skills"
    },
    None: {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:rr-sous-chef:86U8O9Fp",
        "style": "home cook in the style of Rachel Ray.  The goal is to be helpful, warm,\
        friendly and encouraging.  This is the default chef type."
    }
}

# Establish the core models that will be used by the chat service
#core_models = ["gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo"]
core_models = ["gpt-4-1106-preview", "gpt-3.5-turbo-1106", "gpt-4-1106-preview", 
"gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo"]
# Parser tool
def parse_recipe(response:Union[Recipe, str, dict]):
    """ Parse the recipe from the model response. """
    # Format a claude prompt to parse the recipe
    messages = [
        {
            "role": "system", "content": f""" Please
            parse recipe from this response {response} into a JSON object with the same values as a\
            Recipe object {Recipe}.  Make sure to include all of of the required fields.\
            If there are any missing fields, please fill them in with the appropriate\
            values as best you can.  Return only the Recipe json object."""
        }
    ]
    #models = ["gpt-4-0613", "gpt-4-0613", "gpt-4", "gpt-3.5-turbo-0613"]
    models = core_models
    # Iterate through the models until you get a successful response
    for model in models:
        try:
            response = openai.chat.completions.create(
                model = model,
                messages = messages,
                temperature = 0,
                max_tokens = 1000,
                response_format = {"type" : "json_object"}
            )
            new_recipe = response.choices[0].message.content
            return new_recipe

        except OpenAIError as e:
            print(f"Error with model {model}: {e}")
            continue

def create_message_from_recipe(recipe: Union[str, dict, Recipe], chef_type:str = "home_cook"):
    """ Convert a vanilla recipe response into a chat message """
    chef_style = openai_chat_models[chef_type]["style"]
    messages = [
        {
            "role" : "system",
            "content" : f""" You have create a recipe {recipe} for a user.
            Please create a message that includes the recipe in the style of
            {chef_style}.  Make sure to return the recipe in the same format.
            An example reponse would be -- 

            I'd be delighted to help you with this recipe.  I've made it many times
            and it's always a hit.  Here's what I would do:
            {recipe}.
            Let me know if you have any questions or need any help! -- 
            
            That is just an example.  Adjust your response based on the chef type."""
        }
    ]
    # Set up the API call
    model = openai_chat_models[chef_type]["model_name"]
    models = [model, model, model] + core_models

    # Iterate through the models until you get a successful response
    for model in models:
        try:
            response = openai.ChatCompletion.create(
                model = model,
                messages = messages,
                temperature = 1,
                max_tokens = 500
            )
            chef_response = response.choices[0].message.content
            # Convert the chef response into a message
            return [{"role" : "ai", "content" : chef_response}]

        except OpenAIError as e:
            print(f"Error with model {model}: {e}")
            continue
>>>>>>> 8527395785d28333fd5240a8229180810d928d69
