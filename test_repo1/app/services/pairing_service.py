## Need to create the function "get_pairing" which 
# will take in a recipe and generate a pairing that fits 
# the Pairing class model
import openai
import os
from ..models.pairing import Pairing

# Create a function that takes in a recipe and a pairing type
# and returns a pairing that fits the Pairing class model
def get_pairing(recipe: str, pairing_type: str):
    # @TODO Migrate code over from the streamlit app
    # Should return a pairing that fits the Pairing class model
    # Set your API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.getenv("OPENAI_ORG")
    #@TODO Use the OpenAI API to generate a pairing and return it as a Pairing object
