""" Service Utilities for Image Generation """
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the environment variables
load_dotenv()

# Load the OpenAI API key and the organization ID
OPENAI_API_KEY = os.getenv("OPENAI_KEY2")
OPENAI_ORGANIZATION_ID = os.getenv("OPENAI_ORG2")

# Create the OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    organization=OPENAI_ORGANIZATION_ID,
    max_retries=3,
    timeout=10
    )

def generate_image(recipe_name):
    """ Generate an image from the given image request. """
    # Generate the image
    response = client.images.generate(
        prompt=str(recipe_name),
        model="dall-e-2",
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    # Return the image response as a string
    return f"Success! Your image can be viewed at {image_url}"

