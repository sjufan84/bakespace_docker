""" Pairings functions for the assistant and recipe models """
import os
import logging
from openai import OpenAI
import requests
from dotenv import load_dotenv
from app.models.pairing import Pairing

# Load the environment variables
load_dotenv()

# Load the OpenAI API key and the organization ID
OPENAI_API_KEY = os.getenv("OPENAI_KEY2")
OPENAI_ORGANIZATION_ID = os.getenv("OPENAI_ORG2")

# Create the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY, organization=OPENAI_ORGANIZATION_ID, max_retries=3, timeout=10)

# Set the core models
core_models = ["gpt-3.5-turbo-1106",
"gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo"]

# Create a function to generate a pairing
# Create Recipe Functions
def generate_pairings(pairing_type: str, recipe: dict):
    """ Generate a recipe based on the specifications provided """
    # Define the first system message.  This let's the model know what type of output\
    # we are expecting and in what format it needs to be in.
    logging.debug("Creating system message prompt.")
    messages = [
        {
            "role": "system", "content": f"""You are a master chef helping a user
            pair a {pairing_type} with a recipe {recipe}.  Please provide a list of 2 pairings
            in the format of a JSON list of dictionaries with the following keys: {Pairing.schema()["properties"].keys()}.
            Return only the list of pairings."""
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
                temperature=0.5,
                top_p=1,
                max_tokens=750,
                response_format = {"type" : "json_object"}
            )
            # Get the chef response
            pairings_response = response.choices[0].message.content
            # Convert the chef response to a message and append it to the chat history
            
            return pairings_response

        except (requests.exceptions.RequestException,
            requests.exceptions.ConnectTimeout) as e:
            logging.error("Error with model: %s. Error: %s", model, e)
            continue
        except ConnectionError as e:
            logging.error("Error generating pairing: %s", e)
            return {"message": "Error generating pairing."}

# Generate pairings tool
generate_pairings_tool = {
  "name": "generate_pairings",
  "description": "Generate a list of pairings based on the pairing type and recipe.",
  "parameters": {
    "type": "object",
    "properties": {
      "pairing_type": {
        "type": "string",
        "description": "The type of pairing to generate."
      },
      "recipe": {
        "type": "string, dict, or Recipe object",
        "description": "The recipe to generate the pairings for."
      }
    },
    "required": [
      "pairing_type",
      "recipe"
    ]
  }
}

