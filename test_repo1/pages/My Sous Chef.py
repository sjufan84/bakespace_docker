# This is a core recipe generation page that allows the user to create recipes based on preferences, skill level, etc. 
# It will also allow the user to generate pairings including wine, coffee, etc.

# Initial imports
import streamlit as st
from utils.chat_utils import add_message_to_chat, initialize_chat, save_chat_history_dict, get_chef_response
from utils.new_recipes_functions import generate_new_recipe
from utils.image_utils import generate_image
import openai
import os
from langchain.memory import ChatMessageHistory
from streamlit_extras.switch_page_button import switch_page
from streamlit_chat import message
from dotenv import load_dotenv
load_dotenv()


# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

# Reset the other pages to their default values
def reset_other_pages():
    st.session_state.seasonal_page = 'Get Produce Choice'
    st.session_state.sos_page = 'upload recipe'
    # st.session_state.create_recipe_page = 'initial_recipe'
    # st.session_state.foodpedia_page = "foodpedia_question_page"
    # st.session_state.query_page = 'get_query'
    st.session_state.image_page = 'get_image'
    st.session_state.pairing_page = 'get_pairing_type'

reset_other_pages()

# Create a function to initialize the session state variables
def init_sous_chef_session_variables():
    # Initialize session state variables
    session_vars = [
        'recipe', 'recipes', 'sous_page', 'response', 'additional_messages', 'pairing', 'pairings_dict', 'selected_pairings', 'recipe_name', 'image_generated', 'history', 'chat_summary', 'chat_history_dict'
    ]
    default_values = [
        "", {}, "get_new_recipe", '', [], '', {}, [], '', False, ChatMessageHistory(), '', {}
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

# Initialize the session state variables
init_sous_chef_session_variables()

# Create a function to reset the session state variables
def reset_sous_chef_session_variables():
    # Reset session state variables to their default values
    session_vars = [
        'recipe', 'recipes', 'sous_page', 'response', 'additional_messages', 'pairing', 'pairings_dict', 'selected_pairings', 'recipe_name', 'image_generated', 'history', 'chat_summary', 'chat_history_dict'
    ]
    default_values = [
        "", {}, "get_new_recipe", '', [], '', {}, [], '', False, ChatMessageHistory(), '', {}
    ]

    for var, default_value in zip(session_vars, default_values):
        st.session_state[var] = default_value


# First we will define a function to ask the user whether they want to use an existing recipe or create a new one
def get_recipe_type():
    # Ask the user whether they want to use an existing recipe or create a new one
    recipe_type = st.selectbox("Do you want to use an existing recipe or create a new one?", options = ["Use an existing recipe", "Create a new recipe"])
    # If the recipe type is "Use an existing recipe" display the recipe name
    st.markdown(f'"Your current recipe is {st.session_state.recipe_name}"')
    # Create a button to submit the recipe type
    submit_recipe_type = st.button("Submit Recipe Type")
    # If the user clicks the button, return the recipe type
    if submit_recipe_type:
        # If the recipe type is "Use an existing recipe" change the page to "sous_existing_recipe", otherwise change the page to "sous_new_recipe"
        if recipe_type == "Use an existing recipe":
            st.session_state.sous_page = "use_existing_recipe"
            # Rerun the script
            st.experimental_rerun()
        else:
            st.session_state.sous_page = "get_new_recipe"
            # Rerun the script
            st.experimental_rerun()

# Create a function that will allow the user to select an existing recipe
def get_existing_recipe():
    # @TODO -- Create a function to pull the user's recipes from the database and allow them to select by name
    # @TODO -- we will then allow them to explore chat functions related to that recipe
    # The layout will be similar to the new recipe layout below and have similar functionality

    return None

# We need to define a function to add the appropriate message to the generate recipe API call for the cook level
def get_cook_level_message(cook_level):
    st.session_state.additional_messages.append({"role" : "user", "content" : f'I am a {cook_level} cook.'})
    return None

# Now we need to define a function to add a user's preferences to the generate recipe API call
def get_preferences_message(preferences):
    # Convert the preferences list into a string
    preferences = ", ".join(preferences)
    st.session_state.additional_messages.append({"role" : "user", "content" : f'I prefer {preferences}.'})

# Now we need to define a function to add a user's serving size to the generate recipe API call
def get_serving_size_message(serving_size):
    st.session_state.additional_messages.append({"role" : "user", "content" : f'I am cooking\
                                                  for {serving_size} people.'})
    return None


# Helper function for creating single-choice checkbox columns
def single_choice_checkbox(container, title, options):
    with container:
        col_list = st.columns(len(options) + 1)
        col_list[0].write(title)
        choices = []
        for i, option in enumerate(options, start=1):
            choice = col_list[i].checkbox(option)
            choices.append(choice)
    return choices

# Helper function for creating multiple-choice checkbox columns
def multi_choice_checkbox(container, title, options):
    with container:
        col_list = st.columns(len(options) + 1)
        col_list[0].write(title)
        choices = []
        for i, option in enumerate(options, start=1):
            choice = col_list[i].checkbox(option)
            choices.append(choice)
    return choices


# Main function to create a new recipe
def get_new_recipe():
    # Create a header for the page
    st.markdown('#### My Sous Chef')
    specifications = st.text_area(
        label="Recipe Specifications",
        value="",
        height=150,
    )

    # Reset the session_state variables if there is already a recipe created
    if st.session_state.recipe_name != "":
        reset_sous_chef_session_variables()

    # Creating the SKILL LEVEL checkboxes
    skill_level_container = st.container()
    skill_level_choices = single_choice_checkbox(skill_level_container, "SKILL LEVEL: (Select One)", ["Home Cook", "Explorer", "Pro Chef"])

    st.write("\n\n\n")

    # Creating the CUSTOMIZE checkboxes
    customize_container = st.container()
    customize_choices = multi_choice_checkbox(customize_container, "CUSTOMIZE: (Select One or More)", ["Sweet", "Savory", "Spicy", "Low Salt", "Vegetarian", "Vegan", "Gluten Free", "Meat Lovers"])

    st.write("\n\n\n")

    # Creating the MAKE FOR checkboxes
    make_for_container = st.container()
    make_for_choices = single_choice_checkbox(make_for_container, "MAKE FOR: (Select One)", ["Just Me", "For Two", "My Family"])

    st.write("\n\n\n")
    
    # Create a button to submit the recipe request
    submit_recipe_request = st.button("Submit Recipe Request")
    if submit_recipe_request:
        with st.spinner("Generating your recipe..."):
            # Get selected options for "SKILL LEVEL" and "MAKE FOR"
            selected_skill_level = [option for option, choice in zip(["Home Cook", "Explorer", "Pro Chef"], skill_level_choices) if choice]
            selected_make_for = [option for option, choice in zip(["Just Me", "For Two", "My Family"], make_for_choices) if choice]

            # Count the number of selected options for "SKILL LEVEL", "PAIRINGS", and "MAKE FOR"
            skill_level_count = len(selected_skill_level)
            make_for_count = len(selected_make_for)

            # Validate the user's selections
            if skill_level_count != 1:
                st.error("Please select exactly one option for 'SKILL LEVEL'")
            elif make_for_count != 1:
                st.error("Please select exactly one option for 'MAKE FOR'")

            # If the selections are valid, proceed with appending messages and generating the recipe
            else:
                # Append the selected "SKILL LEVEL" message to the additional_messages list
                selected_level = selected_skill_level[0]
                get_cook_level_message(selected_level)

                # Append the selected "MAKE FOR" message to the additional_messages list
                selected_serving = selected_make_for[0]
                get_serving_size_message(selected_serving)

                # Now loop through the "CUSTOMIZE" options and add the selected options to a list
                customize_list = []
                for option, choice in zip(["Sweet", "Savory", "Spicy", "Low Salt", "Vegetarian", "Vegan", "Gluten Free", "Meat Lovers"], customize_choices):
                    if choice:
                        customize_list.append(option)
    
                # Call the get_preferences_message function and pass in the customize_list
                get_preferences_message(customize_list)

                # Now call the generate recipe function and pass in the specifications and the session state "additional_messages" list
                recipe = generate_new_recipe(specifications, st.session_state.additional_messages)

                # Set the session state variables
                st.session_state.sous_page = 'display_new_recipe'
                st.session_state.recipe = recipe
                                
                # Re-run the script
                st.experimental_rerun()

# Function to display the new recipe
def display_new_recipe():

    # Display the individual recipe components
    st.markdown('**Recipe Components (Recipe Name, Ingredients, Steps, Prep Time, Cook Time, Total Time are all stored in variables for access / storage/ etc.):**')
    st.markdown(f'**Recipe Name:** {st.session_state.recipe_name}')
    st.markdown(f'**Ingredients:** {st.session_state.ingredients}')
    st.markdown(f'**Steps:** {st.session_state.steps}')
    st.markdown(f'**Prep Time:** {st.session_state.prep_time} minutes')
    st.markdown(f'**Cook Time:** {st.session_state.cook_time} minutes')
    st.markdown(f'**Total Time:** {st.session_state.total_time} minutes')
    st.markdown('---')

    # Display the recipe text
    st.write(st.session_state.recipe)


    
    

    st.markdown('---')

        
    # Inititate an "i" for the session state
    if "i" not in st.session_state:
        st.session_state.i = 0
    
    # We will create two columns, one to display the recipe, and one to display an image of the recipe generated by the Stability AI API
    chat_column, image_column = st.columns([1.15,1], gap = 'large')

    # Create the chat column
    with chat_column:        
        # If the chat_history_dict is empty, then add the chef's message to the chat history
        if len(st.session_state.chat_history_dict) == 0:
            # Display the Sous Chef's first message
            chef_message = "Do you have any questions about the recipe?"
        
            # Add the chef's message to the chat history
            initialize_chat(chef_message)
            
        # Create a text input field for the user to enter their question
        user_input = st.text_area("Enter your question here...", height=330, key="user_input")
        
        # Create a submit button for the form
        submit_question = st.button("Submit Question", type='primary', use_container_width=True)

        if submit_question:
            with st.spinner("Sous Chef thinking..."):
                # Establish a chat container that will be replaced with the most recent 2 messages
                # Add the user's question to the chat history
                add_message_to_chat(user_input, role="user")
                # Get the Sous Chef's response to the user's question
                chef_response = get_chef_response(user_input)
                # Add the Sous Chef's response to the chat history
                add_message_to_chat(chef_response, role="ai")
                
                 # Add the new chat history to the chat history dictionary
                st.session_state.chat_history_dict = save_chat_history_dict()
                # Write the last two messages in the chat history by using the chat_history_dict
                for chat_message in st.session_state.chat_history_dict:
                    # Loop through the chat history and display the last two messages
                    if chat_message['type'] == 'human':
                        message(chat_message['data']['content'], avatar_style="initials", seed="U", is_user=True, key = f"chat_message_{st.session_state.i}")
                        # Add 1 to the session state "i" value
                        st.session_state.i += 1
                    else:
                        message(chat_message['data']['content'], avatar_style="initials", seed="SC", key = f"chat_message_{st.session_state.i}")
                        # Add 1 to the session state "i" value
                        st.session_state.i += 1

        st.text("")
        
        # Give the user options for what to do next
        st.markdown("**What would you like to do next?**")

        # Create a button to allow the user to create a pairing
        create_pairing = st.button("Get a pairing for this recipe", type='primary', use_container_width=True)
        if create_pairing:
            switch_page('Get a Pairing')
            st.experimental_rerun()
        # Create a button to allow the user to make a picture if they don't like the one generated
        make_picture = st.button("Create a different image of your recipe", type = 'primary', use_container_width=True)
        if make_picture:
            switch_page('Image Generator')
            st.experimental_rerun()
        # Create a button to generate a new recipe
        new_recipe = st.button("Generate a new recipe", type = 'primary', use_container_width=True)
        if new_recipe:
            st.session_state.sous_page = 'get_new_recipe'
            st.experimental_rerun()
        # Create a button to allow the user to save the recipe
        save_recipe = st.button("Save Recipe", type = 'primary', use_container_width=True)
        if save_recipe:
            st.session_state.sous_page = 'display_saved_recipe'
            st.experimental_rerun()



    with image_column:
        # Display the recipe name
        st.markdown(f'<div style="text-align: center; text-weight: bold;">{st.session_state["recipe_name"]}</div>', unsafe_allow_html=True)
        st.text("")
        # Placeholder for the image
        image_placeholder = st.empty()
        # Check if the image has already been generated
        if st.session_state.image_generated == False:
            image_placeholder.text("Generating recipe image..")
            # Generate the image
            image_prompt = f'{st.session_state.recipe_name}'
            st.session_state.image = generate_image(image_prompt)
            st.session_state.image_generated = True
        # Update the placeholder with the generated image
        image_placeholder.image(st.session_state.image['output_url'], use_column_width=True)
        st.markdown('---')
        # Markdown "AI image generate by [StabilityAI](https://stabilityai.com)"]"
        st.markdown('''<div style="text-align: center;">
        <p>AI recipe image generated using the Stable Diffusion API by <a href="https://deepai.org/" target="_blank">DeepAI</a></p>
        </div>''', unsafe_allow_html=True)
        st.warning('**Note:** The actual dish may not look exactly like this!')
    

if st.session_state.sous_page == 'get_recipe_type':
    get_recipe_type()
elif st.session_state.sous_page == 'get_new_recipe':
    get_new_recipe()
elif st.session_state.sous_page == 'use_existing_recipe':
    get_existing_recipe()
# Check if the sous_page value is set to 'display_new_recipe'
elif st.session_state.sous_page == 'display_new_recipe':
    display_new_recipe()



