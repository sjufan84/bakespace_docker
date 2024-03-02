""" Service Utilities for Image Generation """
import os
from typing import Union
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

async def create_image_string(prompt : str):
    """ Generate an image from the given image request. """
    logger.debug(f"Generating image for prompt: {prompt}")
    # Generate the image
    try:
        response = client.images.generate(
            prompt=prompt,
            model="dall-e-3",
            size="1024x1024",
            quality="hd",
            n=1,
            # style="vivid",
            response_format="b64_json"
        )
        # decoded_image = decode_image(image_data=response.data[0].b64_json, image_name="image.png")
        logger.debug(f"Image response: {response}", response.data[0].b64_json)
        return response.data[0].b64_json

    except OpenAIError as e:
        logger.error(f"Error generating image: {e}")
        return {"error": str(e)}

async def get_image_prompt(recipe: Union[dict, str]) -> str:
    logger.debug(f"Generating prompt for image generation for recipe: {recipe}")
    messages = [
        {
            "role" : "system",
            "content": f"""Given a recipe {recipe} to be posted on Instagram,
            create a DALL-E prompt for generating
            a highly realistic image that maximizes engagement. Consider the recipe content,
            and platform specifics to identify key visual elements.
            Detail essential photographic aspects to guide the image generation, focusing
            on attributes that enhance realism and relevance, such as scene composition, lighting,
            and perspective. Include
            specific photo settings, such as lens, aperture,
            shutter speed, ISO, and any other relevant
            details that would help the AI generate the most
            hyper-photo-realistic photo possible.Avoid including
            hands or text in the image. Synthesize this
            analysis into a concise DALL-E prompt aimed at producing
            an engaging and contextually appropriate image."""
        }
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            max_tokens=500,
        )
        logger.debug(f"Response: {response}")
        prompt_response = response.choices[0].message.content
        logger.debug(f"Prompt response: {prompt_response}")
        return prompt_response
    except OpenAIError as e:
        logger.error(f"Error generating prompt for image generation: {e}")
        return None
