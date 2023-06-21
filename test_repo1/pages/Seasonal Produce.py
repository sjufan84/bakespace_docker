import streamlit as st
from utils.find_seasonal_produce import find_seasonal_fruits, find_seasonal_vegetables
from datetime import datetime
from utils.find_farmers_markets import get_new_farmers
from streamlit_extras.switch_page_button import switch_page
from PIL import Image

# Reset the other pages to their default values
def reset_other_pages():
    st.session_state.sos_page = 'upload recipe'
    # st.session_state.create_recipe_page = 'initial_recipe'
    # st.session_state.foodpedia_page = "foodpedia_question_page"
    st.session_state.sous_page = 'get_new_recipe'
    # st.session_state.query_page = 'get_query'
    st.session_state.image_page = 'get_image'
    st.session_state.pairing_page = 'get_pairing_type'

reset_other_pages()


# Initialize session state variables
if 'location' not in st.session_state:
    st.session_state.location = ''
if 'date' not in st.session_state:
    st.session_state.date = datetime.today()
if 'seasonal_fruits' not in st.session_state:
    st.session_state.seasonal_fruits = []
if 'seasonal_vegetables' not in st.session_state:
    st.session_state.seasonal_vegetables = []
if 'fruits_dict' not in st.session_state:
    st.session_state.fruits_dict = {}
if 'vegetables_dict' not in st.session_state:
    st.session_state.vegetables_dict = {}
if 'seasonal_page' not in st.session_state:
    st.session_state.seasonal_page = 'Get Produce Choice'
if "response" not in st.session_state:
    st.session_state.response = ""
if "vector_text" not in st.session_state:
    st.session_state.vector_text = []
if "markets" not in st.session_state:
    st.session_state.market = {}
if "radius_dict" not in st.session_state:
    st.session_state.radius_dict = {}
if 'maps' not in st.session_state:
    st.session_state['maps'] = {}



# Define a function to create a hyperlink for each item
def create_link(item):
    url = f"https://www.bing.com/search?q={item}"
    return f"<a href='{url}' target='_blank'>{item}</a>"

# Find new produce for a location

def find_new_produce():   
    # Create a form to get the user's location and date
    title_container = st.container()
    with title_container:
            plant_icon = Image.open("./src/icons/plant.thumbnail.png")
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1], gap = 'medium')
            with col1:
                st.text("")
            with col2:
                st.image(plant_icon, width = 40)
            with col3:
                st.markdown("what's in season")
            with col4:
                st.text("")
    with st.form("get_produce"):
        # Create a text input for the user to enter their zip code or city and state
        location = st.text_input("What is your zip code?")
        date = st.date_input('Today\'s date or another?', st.session_state.date)

        get_produce_button = st.form_submit_button("Find Seasonal Produce", type = 'secondary')
        if get_produce_button:
            with st.spinner(f"Finding seasonal produce in {location}..."):
                st.session_state.location = location
                st.session_state.date = date
                st.session_state.seasonal_fruits = find_seasonal_fruits(location, date)
                st.session_state.seasonal_vegetables = find_seasonal_vegetables(location, date)
                st.session_state.fruits_dict[location] = st.session_state.seasonal_fruits
                st.session_state.vegetables_dict[location] = st.session_state.seasonal_vegetables
                st.session_state.seasonal_page = 'Display Produce'
                st.experimental_rerun()

def get_produce_choice():
    # This is the intial weclome that determines whether the user wants to find new produce or use existing produce
    # Check to see if there is already data in the fruits_dict or vegetables_dict for any locations
    if st.session_state.fruits_dict or st.session_state.vegetables_dict:
        # Tell the user that there is produce stored for the location(s) and give them the option to continue with that produce or find new produce
        st.markdown('You already have stored seasonal produce for these locations.  Select a location if you would like to continue with that produce.\
                    Otherwise, enter a new location to find new produce below.')
        # Create a select box for the user to select a location
        location = st.selectbox("Select a location", list(st.session_state.fruits_dict.keys()) + list(st.session_state.vegetables_dict.keys()))
        # If the location is in the fruits dict, set the seasonal_fruits to the fruits for that location
        if location in st.session_state.fruits_dict.keys():
            st.session_state.seasonal_fruits = st.session_state.fruits_dict[location]
        # If the location is in the vegetables dict, set the seasonal_vegetables to the vegetables for that location
        if location in st.session_state.vegetables_dict.keys():
            st.session_state.seasonal_vegetables = st.session_state.vegetables_dict[location]
        # Set the location to the selected location
        st.session_state.location = location
        # Create a button to continue with the produce for the selected location
        continue_button = st.button("Continue with Produce for " + location, type = 'primary')
        if continue_button:
            st.session_state.seasonal_page = 'Display Produce'
            st.experimental_rerun()
        # Create a button to find new produce
        find_new_produce_button = st.button("Find Produce for a different location", type = 'primary')
        if find_new_produce_button:
            st.session_state.seasonal_page = 'Find Produce'
            st.experimental_rerun()
        
    else:
        st.session_state.seasonal_page = 'Find Produce'
        st.experimental_rerun()


        
   

# Display Seasonal Produce
def display_seasonal_produce():           
    st.markdown("##### Success! Here is a list of produce that is generally in season during the month of "\
            + st.session_state.date.strftime("%B") + " in " + st.session_state.location + ":  📆🍅🥕🍎")
    
    st.markdown('---')

    # Create a list of the fruits and vegetables in the seasonal produce
    fruits = st.session_state.seasonal_fruits
    vegetables = st.session_state.seasonal_vegetables

    # Convert the lists to strings with hyperlinks
    fruits_str = ", ".join([create_link(f) for f in fruits])
    vegetables_str = ", ".join([create_link(v) for v in vegetables])

    # Display the strings as markdown
    st.markdown(f"**Fruits:** {fruits_str}", unsafe_allow_html=True)
    st.markdown(f"**Vegetables:** {vegetables_str}", unsafe_allow_html=True)

    # Create a note explaining the user can click on the name of the fruit or vegetable to find more information about it
    st.warning("**Note:** You can click on the name of the fruit or vegetable to find more information about it!")
    st.markdown('---')

    st.markdown('**What would you like to do next?**')
    # Give the user to find famrers markets near them
    find_farmers_button = st.button("Find Farmers Markets Near You", type='primary', use_container_width=True)
    if find_farmers_button:
       st.session_state.seasonal_page = 'Find Farmers Markets'
       st.experimental_rerun()
    # Give the user to find more produce somewhere else
    find_produce_button = st.button("Find Produce in a Different Location", type='primary', use_container_width=True)
    if find_produce_button:
        st.session_state.seasonal_page = 'Find Produce'
        st.experimental_rerun()
    seasonal_back_button = st.button("Back to Homepage", type='primary', use_container_width=True)
    if seasonal_back_button:
        switch_page('Home')
    
    
   

# Main execution

if st.session_state.seasonal_page == 'Get Produce Choice':
    get_produce_choice()
elif st.session_state.seasonal_page == 'Find Produce':
    find_new_produce()
elif st.session_state.seasonal_page == 'Display Produce':
    display_seasonal_produce()
elif st.session_state.seasonal_page == 'Find Farmers Markets':
    get_new_farmers()



