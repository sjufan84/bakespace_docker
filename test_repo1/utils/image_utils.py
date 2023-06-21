# This page will contain the utilities to be able to generate images for the recipes with stable diffusion's api

# Initial imports
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
import requests

# Load the stable diffusion api key
api_key = os.getenv("STABLE_DIFFUSION_API_KEY")

# Define a function to generate an image for a recipe
def generate_image(image_prompt):
    r = requests.post(
        "https://api.deepai.org/api/stable-diffusion",

        data={
            'text':  f'{image_prompt}',
            'grid_size': "1",
        },
        headers={'api-key': api_key}
    )
    return r.json()


   
