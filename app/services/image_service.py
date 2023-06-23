import requests
from dotenv import load_dotenv
load_dotenv()
import os

# Define a function to generate an image for a recipe
def generate_image(image_prompt):
    
    # Load the stable diffusion api key
    api_key = os.getenv("STABLE_DIFFUSION_API_KEY")
    r = requests.post(
        "https://api.deepai.org/api/stable-diffusion",

        data={
            'text':  f'{image_prompt}',
            'grid_size': "1",
        },
        headers={'api-key': api_key}
    )

    # Return the json object containing the image url
    return r.json()
