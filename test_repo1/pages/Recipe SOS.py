import streamlit as st
import os
import pdfplumber
import requests
from utils.save_recipes import save_recipe_as_pdf, get_recipe_pdf_download_link
from dotenv import load_dotenv
load_dotenv()
import openai
from google.oauth2 import service_account
from spellchecker import SpellChecker


# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])


from google.cloud import vision


if "sos_recipe" not in st.session_state:
    st.session_state.sos_recipe = ""
if "sos_page" not in st.session_state:
    st.session_state.sos_page = "upload recipe"
if "sos_question" not in st.session_state:
    st.session_state.sos_question = ""
if "sos_answer" not in st.session_state:
    st.session_state.sos_answer = ""


def reset_pages():
    st.session_state.seasonal_page = 'Get Produce Choice'
    # st.session_state.chat_page_select = 'chat_home'
    # st.session_state.chef_chat_page = 'get_chef_choice'
    # st.session_state.create_recipe_page = 'create_recipe_home'
    # st.session_state.foodpedia_page = "foodpedia_question_page"
    st.session_state.sous_page = 'get_new_recipe'
    st.session_state.pairing_page = 'get_pairing_type'


reset_pages()

def extract_pdf(pdf_file):
    # Here we are going to use the pdfplumber library to extract the text from the PDF file
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text



def detect_document(uploaded_image):

    client = vision.ImageAnnotatorClient(credentials=credentials)

    #with io.BytesIO(uploaded_image) as image_file:
    #    content = image_file

    #image = vision.Image(uploaded_image)

    response = client.document_text_detection(image=uploaded_image)

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))
    
    response_text = response.full_text_annotation.text


    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    
    return response_text


# Inport the CSS file
with open('./src/css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Create the header for the page
st.markdown('### Recipe S.O.S.')
st.markdown('---')

# Define a function to run the extracted text through a spellchecker
def spellcheck_text(text):

    # Load the custom domain-specific list
    with open("./resources/new_ingredients.txt", "r") as file:
        cooking_terms = [line.strip() for line in file]

    # Initialize the spell-checker
    spell = SpellChecker(language='en')
    spell.word_frequency.load_words(cooking_terms)

    # Tokenize the returned text from the Vision model`)
    tokens = text.split()

    # Correct the misspelled words
    corrected_tokens = []
    for token in tokens:
        if token not in cooking_terms:
            corrected = spell.correction(token)
            if corrected:
                corrected_tokens.append(corrected)
            else:
                corrected_tokens.append(token)
        else:
            corrected_tokens.append(token)

    # Reconstruct the corrected text
    corrected_text = ' '.join(corrected_tokens)

    return corrected_text



def extract_text_from_txt(file):
    # Extract text from a text file
    return file.read()

# We need two functions for feeding extracted text to the OpenAI API -- 1 for text and pdf that uses GPT 3.5 turbo, and one for photots that uses GPT 4.
# The extracted text from photos generally needs to be cleaned up a bit more and needs a more powerful model to handle it.

def text_recipe_edit(recipe):
    # Use the OpenAI API to re-format the recipe

    messages = [
        {
            "role": "system",
            "content": f"You are a helpful Chef who edits user's recipes to make them more readable."
        },
        {
            "role": "user",
             "content" : f"""Reformat and clean up the following extracted recipe text {recipe}, ensuring that the ingredient names are correct and that the recipe is easy to understand. Please stay as true to the original recipe as possible and,\
            if necessary, infer any parts of the recipe that are unintelligible or don't make sense.  Please reformat it into the following format:\
            \n\nRecipe Name:\n\nIngredients:\n\nAmount of ingredient\n\nSteps:\n\n1. Step 1\n2. Step 2\n3. Step 3\n\nTotal time: (in bold)\n\n\
            If there are extra fields that are not in this format, clean them as much as possible, and display them at the end."""
        },
    ]

           # Use the OpenAI API to generate a recipe
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            max_tokens=750,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            temperature=0.6,
            n=1,
            top_p =1
        )
        edited_recipe = response.choices[0].message.content

    except (requests.exceptions.RequestException, openai.error.APIError):

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                max_tokens=750,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                temperature=0.6,
                n=1,
                top_p =1
            )
            edited_recipe = response.choices[0].message.content
        except (requests.exceptions.RequestException, openai.error.APIError):

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                messages = messages,
                max_tokens=750,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                temperature=0.6,
                n=1,
                top_p =1
            )
            edited_recipe = response.choices[0].message.content
       
    return edited_recipe



def photo_recipe_edit(recipe):
    # Use the OpenAI API to re-format the recipe

    messages = [
        {
            "role": "system",
            "content": f"You are a helpful Chef who edits user's recipes to make them more readable."
        },
        {
            "role": "user",
             "content" : f"""Reformat and clean up the following extracted recipe text {recipe}, ensuring that the ingredient names are correct and that the recipe is easy to understand. Please stay as true to the original recipe as possible and,\
            if necessary, infer any parts of the recipe that are unintelligible or don't make sense.  Please reformat it into the following format:\
            \n\nRecipe Name:\n\nIngredients:\n\nAmount of ingredient\n\nSteps:\n\n1. Step 1\n2. Step 2\n3. Step 3\n\nTotal time: (in bold)\n\n\
            If there are extra fields that are not in this format, clean them as much as possible, and display them at the end."""
        },
    ]

           # Use the OpenAI API to generate a recipe
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages = messages,
            max_tokens=750,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            temperature=0.6,
            n=1,
            top_p =1
        )
        edited_recipe = response.choices[0].message.content

    except (requests.exceptions.RequestException, openai.error.APIError):

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0314",
                messages = messages,
                max_tokens=750,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                temperature=0.6,
                n=1,
                top_p =1
            )
            edited_recipe = response.choices[0].message.content
        except (requests.exceptions.RequestException, openai.error.APIError):

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                max_tokens=750,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                temperature=0.6,
                n=1,
                top_p =1
            )
            edited_recipe = response.choices[0].message.content
       
    return edited_recipe

        

def get_recipe_sos_answer(recipe,question):
    
    messages = [
    {
        "role": "system",
        "content": f"You are helpful Chef who answers user's questions about recipes."
                
    },
    {
        "role": "user",
        "content": f"I have this recipe {recipe}, and I was hoping you could answer my question {question} about it."
                    
    },
    ]

      # Use the OpenAI API to generate a recipe
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            max_tokens=750,
            frequency_penalty=0.5,
            presence_penalty=0.75,
            temperature=1,
            n=1
        )
        answer = response.choices[0].message.content

    except (requests.exceptions.RequestException, openai.error.APIError):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages = messages,
            max_tokens=500,
            frequency_penalty=0.2,
            temperature = 1, 
            n=1, 
            presence_penalty=0.2,
        )
        answer = response.choices[0].message.content

    return answer


def upload_recipe():
    st.warning('*Please note: we will do our best to re-format your recipe into one that is as clean and easy to read\
               as possible. Especially if you are uploading an image/photo of the recipe, it may not be perfect, but you\
               should still be able to ask questions about it, and will have the opportunity to edit it after as well.*')
    
    recipe_files = st.file_uploader("Upload one or multiple recipe files", type=["txt", "pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)
    

    recipe_text_area = st.text_area("Or copy and paste the recipe text here")
    submit_recipe_button = st.button("Submit Recipe", type='primary')

    if submit_recipe_button and recipe_files:
        with st.spinner("Extracting and cleaning recipe text. If uploading from photos, this will take a minute..."):
            full_recipe_text = extract_and_concatenate_text(recipe_files, recipe_text_area)
            recipe_edited = edit_recipe(full_recipe_text, recipe_files)

            st.session_state.sos_recipe = recipe_edited
            st.session_state.sos_page = "user edit recipe"
            st.experimental_rerun()
    elif submit_recipe_button and recipe_text_area:
        with st.spinner("Reading and formatting recipe..."):
            recipe_edited = text_recipe_edit(recipe_text_area)
            st.session_state.sos_recipe = recipe_edited
            st.session_state.sos_page = "user edit recipe"
            st.experimental_rerun()
    else:
        st.warning("Please upload a recipe file or copy and paste the recipe text into the text box above.  Ensure images are formatted with the\
                   extension .jpg, .jpeg, or .png.")


def extract_and_concatenate_text(recipe_files, recipe_text_area):
    allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
    full_recipe_text = ""

    for recipe_file in recipe_files:
        if recipe_file.type == "application/pdf":
            recipe_text = extract_pdf(recipe_file)
        elif recipe_file.type == "text/plain":
            recipe_text = extract_text_from_txt(recipe_file)
        elif recipe_text_area != "":
            recipe_text = recipe_text_area
        elif recipe_file.type in allowed_image_types:
            recipe_text = detect_document(recipe_file)
            recipe_text = spellcheck_text(recipe_text)
        else:
            st.write(f"Unsupported file type: {recipe_file.type}")
            continue

        full_recipe_text += recipe_text + "\n\n"

    return full_recipe_text


def edit_recipe(full_recipe_text,  recipe_files):
    allowed_image_types = ["image/jpeg", "image/png", "image/jpg"]
    last_uploaded_file = recipe_files[-1]

    if last_uploaded_file.type in allowed_image_types:
        return photo_recipe_edit(full_recipe_text)
    else:
        return text_recipe_edit(full_recipe_text)

       
      

def user_edit_recipe():
    st.markdown("**Extracted recipe text:**")
    user_recipe_text = st.text_area('Make any edits to the recipe text you need to here. The model is very good at understanding\
                                    the text of the recipe, regardless of format, but there may be wording or abbreviations, etc.\
                                    that need to be fixed. A good rule of thumb is, if you cannot understand the text, the model probably can\'t either.\
                                    Once you are ready, click the "Ask Question" below to ask your question about the recipe', height=300, value=st.session_state.sos_recipe)
    submit_user_edited_recipe = st.button("Submit your recipe to ask a question about it")
    if submit_user_edited_recipe:
        st.session_state.sos_recipe = user_recipe_text
        st.session_state.sos_page = "question form"
        st.experimental_rerun()

def question_form():
    st.markdown("Your edited recipe text:")
    st.write(st.session_state.sos_recipe)
    
    st.markdown('---')

    # Give the user the option to ask a question about the recipe they have uploaded
    st.markdown("**Ask a question about the recipe**")
    question = st.text_area("", height=150)

    submit_question_button = st.button("Submit Question")
    if submit_question_button:
        with st.spinner("Thinking..."):
            st.session_state.sos_answer = get_recipe_sos_answer(st.session_state.sos_recipe, question)
            st.session_state.sos_question = question
            st.session_state.sos_page = "display answer"
            st.experimental_rerun()

    st.markdown('---')

    # Allow the user to save the recipes
    st.success('If you would like to save this recipe, enter a name for it and click "Save Recipe" below.  You can\
               also upload a different recipe to save or ask questions about.')
    # Enter the recipe name
    st.session_state.recipe_name = st.text_input("Recipe Name", value=f"Enter a name for your recipe here")
    # Save the recipe button
    save_recipe_button = st.button("Save Recipe", type = 'primary', use_container_width=True)
    if save_recipe_button:
        # Save the selected recipe as a PDF
        pdf_path = save_recipe_as_pdf(st.session_state.sos_recipe, f"{st.session_state.recipe_name}.pdf")

        # Generate a download link for the saved PDF
        download_link = get_recipe_pdf_download_link(pdf_path, f"{st.session_state.recipe_name}.pdf")

        # Display the download link
        st.markdown(download_link, unsafe_allow_html=True)

    # Allow the user to upload a different recipe
    upload_different_recipe_button = st.button("Upload a Different Recipe", type = 'primary', use_container_width=True)
    if upload_different_recipe_button:
        st.session_state.sos_page = "upload recipe"
        st.experimental_rerun()

def display_answer():
    st.markdown("**Question**")
    st.write(st.session_state.sos_question)
    st.markdown("**Answer**")
    st.write(st.session_state.sos_answer)

    go_back_button = st.button("Ask Another Question")
    if go_back_button:
        st.session_state.sos_page = "question form"
        st.experimental_rerun()

    upload_another_recipe_button= st.button("Upload a Another Recipe")
    if upload_another_recipe_button:
        st.session_state.sos_page = "upload recipe"
        st.experimental_rerun()

if st.session_state.sos_page == "upload recipe":
    upload_recipe()
elif st.session_state.sos_page == "question form":
    question_form()
elif st.session_state.sos_page == "display answer":
    display_answer()
elif st.session_state.sos_page == "user edit recipe":
    user_edit_recipe()

