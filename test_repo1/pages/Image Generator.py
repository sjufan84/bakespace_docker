# This will be a page to allow the user to generate images from stable diffusion's api based on their recipe

# Initial imports
import streamlit as st
from utils.image_utils import generate_image
from streamlit_extras.switch_page_button import switch_page
import os
from dotenv import load_dotenv
load_dotenv()
import requests

# Define a function to initialize the session state variables
def init_image_generator_session_variables():
    # Initialize session state variables
    session_vars = [
        'image_prompt', 'image', 'images_dict', 'image_page'
    ]
    default_values = [
        '', None, {}, 'get_image'
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

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




# Define a function to allow the user to specify the image to generate
def get_image():
    # Tell the user by default, the name of the recipe is used to generate a recipe
    st.markdown("**By default, the name of the recipe is used to generate an image.**")
    # Create a text box to allow the user to specify the prompt for the image generator if they would rather use
    # something else besides the recipe name
    st.markdown("**If you would like to use something else, enter it below:**")
    image_prompt = st.text_input("Image Prompt", value=st.session_state.recipe_name)
    # Create a button to generate the image
    generate_image_button = st.button("Generate Image")
    if generate_image_button:
        with st.spinner("Generating image..."):
            if image_prompt != '':
                st.session_state.image_prompt = image_prompt
            else:
                st.session_state.image_prompt = st.session_state.recipe_name

            st.session_state.image = generate_image(st.session_state.image_prompt)
            st.session_state.images_dict[st.session_state.recipe_name] = st.session_state.image
            st.session_state.image_page = 'display_image'
            st.experimental_rerun()

# This page will contain the utilities to be able to generate images for the recipes with stable diffusion's api

# Define a function to display the image
def display_image():
    st.markdown(f"**Here is your recipe image for {st.session_state.recipe_name}:**")

    # Display the image
    st.image(st.session_state.image['output_url'])
    st.markdown(f"{st.session_state.recipe_name}")

    st.markdown('---')
    st.text("")

    # Create a button to generate a new image
    new_image_button = st.button("Get a New Image", key = 'new_image_button', type = 'primary', use_container_width=True)
    if new_image_button:
        st.session_state.image_page = 'get_image'
        st.experimental_rerun()
    
    # Create a button to go back to the recipe
    recipe_back_button2 = st.button("Back to recipe", key = 'recipe_back_button2', type = 'primary', use_container_width=True)
    if recipe_back_button2:
        switch_page("My Sous Chef")
        st.experimental_rerun()

# Define a function to save the image
def save_image():
    # Save the image
    image = st.session_state.images
    if image:
        st.markdown(f"**Here is your recipe image for {st.session_state.recipe_name}:**")
        st.image(image['output_url'])

init_image_generator_session_variables()

# Define the flow of the page
if st.session_state.image_page == 'get_image':
    get_image()
elif st.session_state.image_page == 'display_image':
    display_image()

