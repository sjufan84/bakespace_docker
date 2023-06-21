from utils.pairings_functions import get_pairing
import streamlit as st
from streamlit_extras.switch_page_button import switch_page



# Initialize the session state
# Create a function to initialize the session state variables
def init_pairing_session_variables():
    # Initialize session state variables
    session_vars = [
        'pairing', 'pairing_type', 'pairing_page', 'pairings_dict', 
    ]
    default_values = [
        'None', 'None', 'get_pairing_type', {},    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value



def get_pairing_type():
    # Create a selectbox that allows the user to choose what type of pairing they would like to generate
    st.markdown("**Select a type of pairing for your recipe:**")
    pairing_type = st.selectbox("Type of pairing", ["Wine", "Beer", "Cocktail", "Non-Alcoholic Beverage", "Coffee", "Tea"])
    get_pairing_button = st.button("Get Pairing")
    if get_pairing_button:
        with st.spinner("Generating pairing..."):
            st.session_state.pairing = get_pairing(st.session_state.recipe, pairing_type)
            st.session_state.pairing_page = 'display_pairing'
            st.experimental_rerun()

    # Display the recipe in session state and allow the user to generate a pairing for it
    st.markdown("**Your current recipe:**")
    st.write(st.session_state.recipe)

    # Create a button to return to the home page
    home_button = st.button("Back to home", type = 'primary', use_container_width=True)
    if home_button:
        switch_page("Home")
        st.experimental_rerun()

    # Create a button to go back to the recipe
    recipe_back_button = st.button("Back to recipe", type = 'primary', use_container_width=True)
    if recipe_back_button:
        switch_page("My Sous Chef")
        st.experimental_rerun()


    


# Function to display the pairing
def display_pairing():
    # Display the pairing and the recipe in 2 columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Your Recipe:**")
        st.write(st.session_state.recipe)
    with col2:
        st.markdown("**Your Pairing:**")
        st.write(st.session_state.pairing)
    
    # Create a space
    st.text("")

    # Create a button to generate a new pairing
    new_pairing_button = st.button("Get a New Pairing", type = 'primary', use_container_width=True)
    if new_pairing_button:
        st.session_state.pairing_page = 'get_pairing_type'
        st.experimental_rerun()
    
    # Create a button to go back to the recipe
    recipe_back_button = st.button("Back to recipe", type = 'primary', use_container_width=True)
    if recipe_back_button:
        switch_page("My Sous Chef")
        st.experimental_rerun()

init_pairing_session_variables()

# Set the page flow based on the session state
if st.session_state.pairing_page == 'get_pairing_type':
    get_pairing_type()
elif st.session_state.pairing_page == 'display_pairing':
    display_pairing()