import streamlit as st
from streamlit_extras.switch_page_button import switch_page


st.set_page_config(page_title="BakeSpace App", layout="wide", initial_sidebar_state="collapsed")

def init_session_variables():
    # Initialize session state variables
    session_vars = [
        'query_page', 'sous_page', 'create_recipe_page', 'sos_page', 'chat_page_select', 'chef_chat_page', 'seasonal_page', 'foodpedia_page', 'recipe_name', 'recipe', 'username', 'recipes', 'markets', 'pairing_page'
    ]
    default_values = [
        'get_query', 'get_new_recipe', 'initial_recipe', 'upload recipe', 'chat_home', 'get_chef_choice', 'Get Produce Choice', 'foodpedia_question_page', '', '', '', {}, {}, st.container(), 'get_pairing_type'    
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

def reset_pages():
    st.session_state.seasonal_page = 'Get Produce Choice'
    st.session_state.sos_page = 'upload recipe'
    #st.session_state.create_recipe_page = 'initial_recipe'
    #st.session_state.foodpedia_page = "foodpedia_question_page"
    st.session_state.sous_page = 'get_new_recipe'
    #st.session_state.query_page = 'get_query'
    st.session_state.image_page = 'get_image'
    st.session_state.pairing_page = 'get_pairing_type'



init_session_variables()
reset_pages()


# Use html for the header
st.markdown('<h2 style="text-align: center; color: #373a3c; font-size: 35px; font-weight: bold;">BakeSpace AI</h2>', unsafe_allow_html=True)

st.markdown('---')

#chef_chat_button = st.button("Chef Chat", type='primary', use_container_width=True)
#if chef_chat_button:
#    switch_page('Chef Chat')
#    st.experimental_rerun()

# Button for basic recipe generation page
# create_recipe_button = st.button("Create a Recipe", type='primary', use_container_width=True)
#if create_recipe_button:
#    switch_page('Create a Recipe')
#    st.experimental_rerun()

#community_inspiration_button = st.button("Community Inspiration", type='primary', use_container_width=True)
#if community_inspiration_button:
#    switch_page('Community Inspiration')
#    st.experimental_rerun()

whats_in_season_button = st.button("What's in Season", type='primary', use_container_width=True)
if whats_in_season_button:
    switch_page('Seasonal Produce')
    st.experimental_rerun()

#foodpedia_button = st.button("Foodpedia", type='primary', use_container_width=True)
#if foodpedia_button:
#    switch_page('Foodpedia')
#    st.experimental_rerun()

recipe_sos_button = st.button("Recipe S.O.S.", type='primary', use_container_width=True)
if recipe_sos_button:
    switch_page('Recipe SOS')

my_sous_chef_button = st.button("My Sous Chef", type='primary', use_container_width=True)
if my_sous_chef_button:
    switch_page('My Sous Chef')
    st.experimental_rerun()

