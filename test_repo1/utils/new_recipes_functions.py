import streamlit as st
import openai
import os
from dotenv import load_dotenv
load_dotenv()
import re
import requests

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")



# We also need to define a function to intialize the session_state variables unique to this page
# This will be used to store the chat history and the current message
def init_create_recipe_session_variables():
    # Initialize session state variables
    session_vars = [
        'recipe', 'ingredients', 'recipe_name', 'recipes', 'history', 'steps', 'cook_time', 'prep_time', 'total_time', 'servings', 'create_recipe_page', 'response', 'chat_history_dict', 'new_messages', 'i'
    ]
    default_values = [
        '', [], "Invalid Recipe", {}, [], [], 0, 0, 0, 0, 'initial_recipe', '', {}, {}, 0
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value



def extract_recipe_name(recipe):
    match = re.search(r"Recipe Name:\s*(.*?)\n", recipe)
    return match.group(1) if match else None


def extract_ingredients(recipe):
    ingredients_regex = r"Ingredients:(.*?)\n\n(?:Steps|Total time)"
    ingredients_match = re.search(ingredients_regex, recipe, re.DOTALL)
    if ingredients_match:
        ingredients_raw = ingredients_match.group(1).strip().split('\n')
        return [ingredient.strip() for ingredient in ingredients_raw if ingredient.strip()]
    return []


def extract_times(recipe):
    cook_time_match = re.search(r"Cook time:\s*(\d+)\s*minutes?", recipe)
    prep_time_match = re.search(r"Prep time:\s*(\d+)\s*minutes?", recipe)
    total_time_match = re.search(r"Total time:\s*(\d+)\s*minutes?", recipe)
    
    cook_time = int(cook_time_match.group(1)) if cook_time_match else None
    prep_time = int(prep_time_match.group(1)) if prep_time_match else None
    total_time = int(total_time_match.group(1)) if total_time_match else None


    return cook_time, prep_time, total_time



def extract_steps(recipe):
    steps_regex = r"Steps:(.*?)\n\n(?:Total time|Cook time|Prep time)"
    steps_match = re.search(steps_regex, recipe, re.DOTALL)
    if steps_match:
        steps_raw = steps_match.group(1).strip().split('\n')
        return [step.strip() for step in steps_raw if step.strip()]
    return []


def is_valid_recipe(recipe):
    cook_time, prep_time, total_time = extract_times(recipe)
    return (
        recipe is not None
        and extract_recipe_name(recipe) is not None
        and extract_ingredients(recipe)
        and cook_time is not None
        and prep_time is not None
        and total_time is not None
        and extract_steps(recipe)
    )


def generate_new_recipe(specifications, additional_messages):
    if 'response' not in st.session_state:
        st.session_state.response = ''
    if st.session_state.recipe != '':
        st.session_state.recipe = ''

    # Initiate the session state variables
    init_create_recipe_session_variables()

    messages = [
        {
            "role": "system",
            "content": f"You are master chef creating recipes per the user's specifications. The recipe should be creative, unique, and adhere to the user's specifications {specifications}."
        },
        {
            "role": "user",
            "content": f"Create a delicious recipe based on these specifications: {specifications}  Please ensure the returned prep time, cook time, and total time are integers in minutes.  If any of the times are n/a\
                as in a raw dish, return 0 for that time.  Round the times to the nearest 5 minutes to provide a cushion and make for a more readable recipe."
        },
        {
            "role": "system",
            "content": f"Generate a recipe in this format:\n\nRecipe Name:\n\nIngredients:\n\nAmount of ingredient\n\nSteps:\n\n1. Step 1\n2. Step 2\n3. Step 3\n\nPrep time: (in minutes)\n\nCook time: (in minutes)\n\nTotal time: (in minutes)\n\nCookware/bakeware needed: (if any, in bold)\n\n"
        }
    ]
    if additional_messages:
        messages += additional_messages
    st.write(st.session_state.recipe)
    while not is_valid_recipe(st.session_state.recipe):
        try:
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1250,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            temperature=1,
            top_p=0.9,
            n=1,
        )

            recipe = response.choices[0].message.content
            st.session_state.recipe = recipe
            

            if is_valid_recipe(recipe):
                recipe_name = extract_recipe_name(recipe)
                st.session_state.recipe_name = recipe_name
                st.session_state.ingredients = extract_ingredients(recipe)
                cook_time, prep_time, total_time = extract_times(recipe)
                st.session_state.cook_time = cook_time
                st.session_state.prep_time = prep_time
                st.session_state.total_time = total_time
                st.session_state.steps = extract_steps(recipe)
                st.session_state.recipes[recipe_name] = recipe
                return recipe

        except (requests.exceptions.RequestException, openai.error.APIError):
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=messages,
            max_tokens=1250,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            temperature=1,
            top_p=0.9,
            n=1,
        )

            recipe = response.choices[0].message.content
            st.session_state.response = response
            st.write (st.session_state.response)
            st.write(recipe)
            st.session_state.recipe = recipe

            if is_valid_recipe(recipe):
                recipe_name = extract_recipe_name(recipe)
                st.session_state.recipe_name = recipe_name
                st.session_state.ingredients = extract_ingredients(recipe)
                cook_time, prep_time, total_time = extract_times(recipe)
                st.session_state.cook_time = cook_time
                st.session_state.prep_time = prep_time
                st.session_state.total_time = total_time
                st.session_state.steps = extract_steps(recipe)
                st.session_state.recipes[recipe_name] = recipe
                return recipe

    





# Edit recipe function -- covers all edits

def get_recipe_edit(edits_requested):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that helps users create amazing recipes from the ingredients and preferences they supply."
        },
        {
            "role": "user",
            "content": f"You generated a recipe {st.session_state.recipe} for me based on my preferences, dietary restrictions, ingredients requested, etc., but I would like to make some edits {edits_requested} to it. Please generate a new recipe in the same format as the recipe {st.session_state.recipe} you already gave me, but with the requested changes. Try to keep the recipe as close to the original as possible, and only make the changes I requested. Keep the same ingredients unless explicitly told to change them or it is absolutely necessary to accommodate the requested changes."
        },
        {
            "role": "assistant",
            "content": "Your updated recipe:"
        },
        {
            "role": "system",
            "content": "Given the user provided parameters, generate a recipe in the same format as the original, incorporating the requested changes."
        }
    ]
    
    # Extract the recipe name from the previous recipe and delete it from the seasonal recipes session state
    match = re.search(r"Recipe Name:\s*(.*?)\n", st.session_state.recipe)
    if match:
        recipe_name = match.group(1)
        
    else:
        recipe_name = "Unknown Recipe"
        
    del st.session_state['recipes'][recipe_name] 
    

        

    # Use the OpenAI API to generate a recipe
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            max_tokens=1000,
            temperature=0.5,
            n=1
        )
       
        recipe = response.choices[0].message.content
        st.session_state.temp_recipe = recipe
        
        st.session_state['messages'] = messages
        st.session_state.recipe = recipe

         # Extract the recipe name from the new recipe
        match = re.search(r"Recipe Name:\s*(.*?)\n", st.session_state.recipe)
        if match:
            recipe_name = match.group(1)
            st.session_state['recipes'][recipe_name] = recipe
            st.session_state.recipe = recipe
        else:
            #st.write("Recipe name not found in the generated recipe.")
            recipe_name = "Unknown Recipe"
            st.session_state['recipes'][recipe_name] = recipe
            st.session_state.recipe = recipe
    
    except (requests.exceptions.RequestException, openai.error.APIError):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages = messages,
            max_tokens=2000,
            temperature=0.5
        )
        
        recipe = response.choices[0].message.content
        st.session_state.temp_recipe = recipe
        st.session_state['messages'] = messages
        st.session_state.recipe = recipe
        # Extract the recipe name from the new recipe
        match = re.search(r"Recipe Name:\s*(.*?)\n", recipe)
        if match:
            recipe_name = match.group(1)
            st.session_state['recipes'][recipe_name] = recipe
            st.session_state.recipe = recipe
            st.session_state.recipe_name = recipe_name
        else:
            #st.write("Recipe name not found in the generated recipe.")
            recipe_name = "Unknown Recipe"
            st.session_state['recipes'][recipe_name] = recipe
            st.session_state.recipe = recipe
            st.session_state.recipe_name = recipe_name