import streamlit as st
import openai
import os
from dotenv import load_dotenv
load_dotenv()
import requests
# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

# Create a function to initiate the session state
def init_create_pairing_session_variables():
    # Initialize session state variables
    session_vars = [
        'pairing', 'pairing_type', 'pairings_dict'
    ]
    default_values = [
        "", "", {}
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Create a function to generate a pairing based on the recipe
# The pairing could be of type coffee, wine, beer, spirits, etc.
# We will use asynchronous programming to run the GPT-3.5 Turbo model
# This will allow us to run the model in the background while the user is interacting with the app
# We will use the st.spinner() functiion to show the user that the model is running
def get_pairing(recipe, pairing_type):

    # Create the messages (prompts) for the GPT-3.5 Turbo model
    messages = [
    {
        "role": "system",
        "content": f"You are helpful assistant creating an innovate and creative pairing of type {pairing_type} to go with the user's\
                recipe {recipe}.  Please provide the user with multiple different options in the pairing, and include why each option is\
                    appropriate for the recipe.  If {pairing_type} is cocktail, please provide the user with the recipe for the cocktails."
    },
    {
        "role": "user",
        "content": f"Provide me with a pairing of type {pairing_type} with the recipe {recipe}."
    },
    {
        "role": "user",
        "content": f"Use this format for the pairing:\n\n{pairing_type} Pairing Suggestions:\n\n- Pairing 1\n- Pairing 2\n- Pairing 3\n\nNote about why this pairing is appropriate for the recipe {recipe}: (in bold)"
    }
]

# Use the OpenAI API to generate a recipe
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            max_tokens=1000,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            temperature=1,
            n=1
        )
        pairing = response.choices[0].message.content
        st.session_state['messages'] = messages
        st.session_state['response'] = response
        st.session_state.pairing = pairing
        st.session_state.pairings_dict[st.session_state.recipe_name] = pairing

        
    except (requests.exceptions.RequestException, openai.error.APIError):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages = messages,
            max_tokens=1000,
            frequency_penalty=0.5,
            temperature = 1, 
            n=1, 
            presence_penalty=0.5,
        )
        pairing = response.choices[0].message.content
        st.session_state['messages'] = messages
        st.session_state['response'] = response
        st.session_state.pairing = pairing
        st.session_state.pairings_dict[st.session_state.recipe_name] = pairing

    return pairing



