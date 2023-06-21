# We are going to allow the user to decide between three chefs who have 3 different cooking styles, give their specifications
# and then generate a recipe for them. After that we will then allow them to ask the selected chef questions about the recipe
import streamlit as st
from streamlit_chat import message
from langchain.memory import ConversationSummaryBufferMemory
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
import re
import openai
from streamlit_extras.switch_page_button import switch_page
import os
from dotenv import load_dotenv
from save_recipes import save_recipe_as_pdf, get_recipe_pdf_download_link
load_dotenv()

# App layout
st.set_page_config(page_title="Chef Chat", initial_sidebar_state="collapsed", layout="wide")

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")


if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'chosen_chef' not in st.session_state:
    st.session_state.chosen_chef = ''
if 'chef_chat_page' not in st.session_state:
    st.session_state.chef_chat_page = 'get_chef_choice'
if 'recipe' not in st.session_state:
    st.session_state.recipe = "Invalid Recipe"
if 'chef' not in st.session_state:
    st.session_state.chef = ""
if 'style' not in st.session_state:
    st.session_state.style = ""
if 'chosen_style' not in st.session_state:
    st.session_state.chosen_style = ""
if 'initials_seed' not in st.session_state:
    st.session_state.initials_seed = ""
if 'chef_attitude' not in st.session_state:
    st.session_state.chef_attitude = ""


# Initialize ConversationChain
llm = OpenAI()
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=40)
conversation_chain = ConversationChain(llm=llm, memory=memory, verbose=True)

def handle_user_input(user_input):
    response = conversation_chain.predict(input=user_input)
    return response

# Create a dictionary of chefs and their cooking styles
chef_style_dict = {
    "Gordon Ramsay": "Precise and elevated",
    "Curtis Stone": "Pro Chef",
    "Rachel Ray": "Home Chef",
    "Anthony Bourdain": "Outside the Box",
}
chef_attitude_dict = {
    "Gordon Ramsay": "Brash and demanding",
    "Curtis Stone": "Professional and friendly",
    "Rachel Ray": "Friendly and encouraging",
    "Anthony Bourdain": "Cynical and sarcastic",
}
seed_dict = {
    "Gordon Ramsay" : "GR",
    "Curtis Stone" : "CS",
    "Rachel Ray" : "RR",
    "Anthony Bourdain" : "AB",
}

def is_valid_recipe(recipe):
    # Example: Check if the recipe has a name, ingredients, and steps
    has_name = re.search(r"Recipe Name:\s*(.*?)\n", recipe)
    has_ingredients = re.search(r"Ingredients:\s*(.*?)\n", recipe)
    has_steps = re.search(r"Steps:\s*(.*?)\n", recipe)

    return has_name and has_ingredients and has_steps



def get_chat_mode_recipe(specifications):
    if not st.session_state.user_data.get('recipes'):
        st.session_state.user_data['recipes'] = {}
   
  
    
    messages = [
    {
        "role": "system",
        "content": f"You are a chef {st.session_state.chef} with {st.session_state.style} style and {st.session_state.chef_attitude} attitude.\
            You are going to help the user create a recipe based on their specifications and answer\
            follow-up questions about the recipe.  Respond as the chef would respond to the user.\
            The recipe name and the recipe should be innovative, creative, and reflect your style {st.session_state.style}\
             and your attitude {st.session_state.chef_attitude}.\n\n\""
    },
    {
        "role": "user",
        "content": f"Please create a delicious recipe based on my specification {specifications}."
    },
    {
        "role": "system",
        "content": "Given the user provided parameters, generate a recipe in the following format:\n\nRecipe Name:\n\nIngredients:\n\n- Amount of ingredient\n\nSteps:\n\n- Step 1\n- Step 2\n- Step 3\n\nTotal amount of time to make the dish: (in bold)\n\nAdded ingredients: (if any, in bold)\n\nOptional ingredients: (if any, in bold)\n\nCookware or bakeware needed: (if any, in bold)"
    }
    ]

    st.session_state.recipe = "Invalid Recipe"

    while not is_valid_recipe(st.session_state.recipe):
        # Use the OpenAI API to generate a recipe
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                max_tokens=2500,
                frequency_penalty=0.5,
                presence_penalty=0.5,
                temperature=1,
                n=1
            )
            recipe = response.choices[0].message.content
            st.session_state['messages'] = messages
            
            # Extract the recipe name from the new recipe
            match = re.search(r"Recipe Name:\s*(.*?)\n", recipe)
            if match:
                recipe_name = match.group(1)
                st.session_state.recipe = recipe
                st.session_state.recipe_name = recipe_name
                st.session_state['user_data']['recipes'][recipe_name] = recipe
            else:
                if st.session_state.recipe != "Invalid Recipe":
                    #st.write("Recipe name not found in the generated recipe.")
                    recipe_name = "Unknown Recipe"
                    st.session_state['user_data']['recipes'][recipe_name] = recipe
                    st.session_state.recipe = recipe
                    st.session_state.recipe_name = recipe_name
        except:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                messages = messages,
                max_tokens=3000,
                frequency_penalty=0.2,
                temperature = 1, 
                n=1, 
                presence_penalty=0.2,
            )
            recipe = response.choices[0].message.content
            st.session_state['messages'] = messages
            
            # Extract the recipe name from the new recipe
            match = re.search(r"Recipe Name:\s*(.*?)\n", recipe)
            if match:
                recipe_name = match.group(1)
                st.session_state.user_data['recipes'][recipe_name] = recipe
                st.session_state.recipe = recipe
                st.session_state.recipe_name = recipe_name
            else:
                if st.session_state.recipe != "Invalid Recipe":
                    recipe_name = "Unknown Recipe"
                    st.session_state.user_data['recipes'][recipe_name] = recipe
                    st.session_state.recipe = recipe
                    st.session_state.recipe_name = recipe_name

    return recipe

def get_chef_choice():
    # Allowing the user to select a chef fron the chef dictionary
    st.markdown('<h4 style = "text-align:center; color:#7b3583">Welcome to Chef Chat!  Select a chef below to get started.  Feeling adventurous?<br>  How about asking\
            Anthony Bourdain for a recipe.  Feeling like a home cooked meal?<br>  Rachel Ray is here to help.  Or if you\
            know you\'re a pro, Curtis Stone<br> and Gordon Ramsey have you covered.</h2>', unsafe_allow_html=True)
    st.markdown('- - -')
    st.markdown('<h5 style = "text-align:center; color:#7b3583">Select a Chef to get started:</h4>', unsafe_allow_html=True)
    chef_name = st.selectbox("Select a Chef:", list(chef_style_dict.keys()))
    start_conversation_button = st.button("Start Conversation", type = 'primary', use_container_width=True)
    if start_conversation_button:
        # Set the session state variables and rerun the script to hide the chef inputs and show the chat
        st.session_state.chef = chef_name
        st.session_state.initials_seed = seed_dict[chef_name]
        st.session_state.chosen_style = chef_style_dict[chef_name]
        st.session_state.chef_chat_page = 'get_specifications'
        st.session_state.chef_attitude = chef_attitude_dict[chef_name]
        st.experimental_rerun()
    
# Function to get the user's recipe specifications
def get_chef_recipe_specifications():    
    message(f"{st.session_state.chef}: What kind of recipe would you like to make today?  Make sure you tell me about any\
            dietary restrictions or allergies you have.", avatar_style='initials', seed = st.session_state.initials_seed)
    user_specifications = st.text_input("Your recipe specifications:")
    generate_recipe_button = st.button("Create Your Recipe", type = 'primary', use_container_width=True)
    if generate_recipe_button:
        with st.spinner(f"Hang tight, {st.session_state.chef} is creating your recipe..."):
            get_chat_mode_recipe(user_specifications)
            st.session_state.chef_chat_page = 'follow_up'
            st.experimental_rerun()
        


def follow_up_chat():
    if 'asked_questions' not in st.session_state:
        st.session_state['asked_questions'] = []
    # Display the recipe and ask the user if they have any follow-up questions
    
    # Set i = 0 to be able to generate unique keys for the follow-up questions
    i = 0
    # Create a container to hold the recipe and the follow-up question
    chef_recipe_chat = st.container()
    with chef_recipe_chat:
        col1, col2 = st.columns(2, gap = 'large')
        
        # Display the chat in the left column
        with col2:
        
          
            st.write(st.session_state.recipe)
            
        with col1:
            # Ask the user if they have any follow-up questions
            follow_up_question = st.text_area(f"Ask {st.session_state.chef} any follow up questions:", key= f'follow_up_question{i}', height=100)
            ask_button = st.button("Ask", key=f'ask_button{i}', type='primary', use_container_width=True)
            st.markdown('- - -')
            st.markdown(f'**Your chat with {st.session_state.chef}:**')
            initial_message_container = st.empty()
            with initial_message_container.container():
                message(f"{st.session_state.chef}: Here is your recipe!: ", avatar_style='initials', seed=st.session_state.initials_seed)
                message(f"{st.session_state.chef}: Do you have any follow-up questions about the recipe?",\
                        avatar_style='initials', seed=st.session_state.initials_seed)
            chat_container = st.empty()
            if ask_button:
                if initial_message_container:
                    initial_message_container.empty()
                if st.session_state.chef == 'Anthony Bourdain':
                    spinner_message = "I guess... hang on."
                elif st.session_state.chef == 'Rachel Ray':
                    spinner_message = "Of course!  Let me get right on that."
                elif st.session_state.chef == 'Gordon Ramsey':
                    spinner_message = "All right!  But clean up your station first!  It's a hot mess!"
                elif st.session_state.chef == 'Curtis Stone':
                    spinner_message = "Absolutely Chef!  Let me think for a second..."
                with st.spinner(f"{spinner_message}"):
                    response = handle_user_input(follow_up_question)
                    st.session_state.asked_questions.append((follow_up_question, response))
                    
                    with chat_container.container():
                        for question, answer in st.session_state.asked_questions[-1:]:
                            message(question, is_user=True)
                            message(answer, avatar_style='initials', seed=st.session_state.initials_seed)
                i+=1
            # Give the user the option to save their recipe
            st.markdown('- - -')
            st.markdown('<h5 style = "text-align:center; color:#7b3583">If you are satisfied with your recipe,\
                        and your questions have been answered, you may download it as a pdf by clicking "Save Recipe" below:</h4>', unsafe_allow_html=True)
            save_recipe_button = st.button("Save Recipe", type = 'secondary', use_container_width=True)
            if save_recipe_button:
                # Generate the pdf download link and display it
                # Save the selected recipe as a PDF
                pdf_path = save_recipe_as_pdf(st.session_state.recipe, f"{st.session_state.recipe_name}.pdf")

                # Generate a download link for the saved PDF
                download_link = get_recipe_pdf_download_link(pdf_path, f"{st.session_state.recipe_name}.pdf")

                # Display the download link
                st.markdown(download_link, unsafe_allow_html=True)
            st.markdown('<h5 style = "text-align:center; color:#7b3583">Want to create another recipe, perhaps with a diferent\
                        Chef?</h4>', unsafe_allow_html=True)
            create_new_chef_recipe_button = st.button("Create New Recipe", type = 'secondary', use_container_width=True)
            if create_new_chef_recipe_button:
                st.session_state.chef_chat_page = 'get_chef_choice'
                st.experimental_rerun()
            chef_return_to_home_button = st.button("Return to Home Page", type = 'secondary', use_container_width=True)
            if chef_return_to_home_button:
                switch_page('Home')
                






if st.session_state.chef_chat_page == 'get_chef_choice':
    get_chef_choice()
elif st.session_state.chef_chat_page == 'get_specifications':
    get_chef_recipe_specifications()
elif st.session_state.chef_chat_page == 'follow_up':
    follow_up_chat()
    

       
st.sidebar.markdown("---")
st.sidebar.header("Instructions")
st.sidebar.markdown("1. Select a chef from the dropdown menu.")
st.sidebar.markdown("2. Click 'Start Conversation' to display the chef's message.")
st.sidebar.markdown("3. Enter your recipe specifications and click 'Generate Recipe'.")
st.sidebar.markdown("4. Ask follow-up questions about the recipe.")


