""" Service Utilities for Image Generation """
from typing import Union
from app.dependencies import get_openai_api_key, get_openai_org
from openai import OpenAI, OpenAIError
import logging
from models.recipe import Recipe, FormattedRecipe
import base64
import io
from PIL import Image

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

client = OpenAI(api_key=get_openai_api_key(), organization=get_openai_org(), max_retries=3, timeout=55)

# Decode Base64 JSON to Image
async def decode_image(image_data, image_name):
    """ Decode the image data from the given image request. """
    # Decode the image
    image_bytes = base64.b64decode(image_data)
    # Convert the bytes to an image
    image = Image.open(io.BytesIO(image_bytes))
    # Save the image
    return image.save(image_name)

async def create_image_string(prompt : str):
    """ Generate an image from the given image request. """
    logger.info(f"Generating image for prompt: {prompt}")
    # Generate the image
    try:
        response = client.images.generate(
            prompt=prompt,
            model="dall-e-3",
            size="1024x1024",
            quality="hd",
            n=1,
            style="vivid",
            response_format="b64_json"
        )
        # await decode_image(image_data=response.data[0].b64_json, image_name="image.png")
        logger.info(f"Image successfully generated: {response.data[0].b64_json[:100]}...")
        await decode_image(image_data=response.data[0].b64_json, image_name="image.png")
        return response.data[0].b64_json

    except OpenAIError as e:
        logger.error(f"Error generating image: {e}")
        return {"error": str(e)}

async def get_image_prompt(recipe: Union[dict, str, Recipe, FormattedRecipe]) -> str:
    logger.info(f"Generating prompt for image generation for recipe: {recipe}")
    messages = [
        {
            "role" : "system",
            "content": f"""Given a recipe {recipe} to be posted on Instagram,
            create a DALL-E prompt for generating
            a highly realistic photo for maximum engagement.
            Consider the recipe content, what the final dish would look like,
            and Instagram specifics to identify key visual elements.  The photo should look as authentic
            and true to life as possible, as if it were taken by a professional food photographer just after
            the dish was prepared.
            Detail essential photographic aspects to guide the photo generation, focusing
            on attributes that enhance realism and relevance, such as scene composition, lighting,
            and perspective. Include
            specific photo settings, such as lens, aperture,
            shutter speed, ISO, and any other relevant
            details that would help the AI generate the most
            hyper-photo-realistic photo possible .Avoid including
            hands or text in the image. Synthesize this
            analysis into a concise DALL-E prompt aimed at producing
            an engaging and contextually appropriate photo."""
        }
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            max_tokens=500,
        )
        prompt_response = response.choices[0].message.content
        logger.info(f"Image prompt response: {prompt_response}")
        return prompt_response

    except OpenAIError as e:
        logger.error(f"Error generating prompt for image generation: {e}")
        return None
