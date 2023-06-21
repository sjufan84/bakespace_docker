import streamlit as st
from Home import init_session_state
import time



init_session_state()

# Resetting the state of the pages
def reset_other_pages():
   
    st.session_state['custom_recipe_page'] = 'Get Custom User'
    st.session_state['user_page'] = 'get_user_data'
    st.session_state['kids_recipe_page'] = 'kids_recipe_chatbot'
reset_other_pages()

# Create a list of common main ingredients the user might have --
ingredients_list = [
"Almonds",
"Anchovies",
"Apples",
"Apricots",
"Arugula",
"Asparagus",
"Avocado",
"Bacon",
"Balsamic vinegar",
"Bananas",
"Barley",
"Beans",
"Beef",
"Bell peppers",
"Berries",
"Bok choy",
"Broccoli",
"Brussels sprouts",
"Cabbage",
"Cantaloupe",
"Carrots",
"Cashews",
"Cauliflower",
"Celery",
"Chard",
"Cheese",
"Cherries",
"Chicken",
"Chickpeas",
"Clams",
"Coconut",
"Cod",
"Collard greens",
"Corn",
"Couscous",
"Cranberries",
"Dates",
"Dijon mustard",
"Dill pickles",
"Duck",
"Egg noodles",
"Eggs",
"Fennel",
"Figs",
"Fish sauce",
"Flaxseeds",
"Garlic",
"Grapefruit",
"Grapes",
"Green onions",
"Ham",
"Hazelnuts",
"Honey",
"Hot sauce",
"Kale",
"Ketchup",
"Kiwi",
"Lamb",
"Lasagna noodles",
"Lemons",
"Lentils",
"Lettuce",
"Limes",
"Lobster",
"Macadamia nuts",
"Macaroni",
"Mahi-mahi",
"Mangoes",
"Maple syrup",
"Mayonnaise",
"Milk",
"Mushrooms",
"Mustard greens",
"Nectarines",
"Oats",
"Octopus",
"Okra",
"Onions",
"Orange",
"Oysters",
"Papaya",
"Peanuts",
"Pears",
"Peas",
"Pecans",
"Penne pasta",
"Pine nuts",
"Pistachios",
"Pomegranate",
"Potatoes",
"Pumpkin",
"Pumpkin seeds",
"Quail",
"Quinoa",
"Radishes",
"Rice",
"Ricotta",
"Romaine lettuce",
"Rutabaga",
"Sausages",
"Salmon",
"Sardines",
"Scallops",
"Shallots",
"Shrimp",
"Sesame seeds",
"Soba noodles",
"Spinach",
"Squash",
"Squid",
"Strawberries",
"Sunflower seeds",
"Sweet pickles",
"Sweet potatoes",
"Swiss chard",
"Swordfish",
"Tangerines",
"Teriyaki sauce",
"Tomatoes",
"Tuna",
"Turbot",
"Turnips",
"Udon noodles",
"Vanilla extract",
"Walnuts",
"Watercress",
"Watermelon",
"Yogurt",
"Zucchini"
]

kid_friendly_dishes =["Baked Chicken Tenders", "Baked Potatoes", "Beef Tacos", "Burritos", "Cheese Quesadillas", "Chicken Alfredo",    "Chicken Caesar Salad", "Chicken Fajitas", "Chicken Nuggets", "Chicken Quesadillas", "Chocolate Chip Cookies",    "French Fries", "Fruit Popsicles", "Granola Bars", "Grilled Cheese Sandwiches", "Ham and Cheese Sandwiches",    "Hamburgers", "Hot Dogs", "Ice Cream", "Macaroni and Cheese", "Mashed Potatoes", "Meatball Subs",    "Mini Pizzas", "Nachos", "Pancakes", "Pasta Salad", "Peanut Butter and Jelly Sandwiches",    "Pizza", "Popcorn Chicken", "Quesadillas", "Smoothies", "Spaghetti and Meatballs", "Taco Bowls",    "Tacos", "Trail Mix", "Waffles", "Yogurt", "Zucchini Bread"]


# Sort the kids friendly dishes
kids_friendly_dishes = sorted(kid_friendly_dishes)

kids_ingredients_list = [
'apples',
'bananas',
'bell peppers',
'black beans',
'blueberries',
'broccoli',
'carrots',
'cauliflower',
'celery',
'cheese',
'cherries',
'chicken',
'chocolate',
'cinnamon',
'corn',
'couscous',
'cranberries',
'cucumber',
'eggs',
'grapes',
'green beans',
'ham',
'honey',
'ketchup',
'kiwi',
'lemons',
'lettuce',
'macaroni',
'mango',
'maple syrup',
'milk',
'mushrooms',
'mustard',
'noodles',
'oatmeal',
'onions',
'orange',
'pasta',
'peaches',
'peanut butter',
'pears',
'peas',
'pepperoni',
'pineapple',
'plums',
'pork',
'potatoes',
'pumpkin',
'raisins',
'raspberries',
'rice',
'salmon',
'sausage',
'spaghetti',
'spinach',
'squash',
'strawberries',
'sweet potatoes',
'turkey',
'vanilla',
'watermelon',
'yogurt',
'zucchini'
]

# Create a list of common ingredients the user might have --
kitchen_staples = [
    'all-purpose flour',
    'baking powder',
    'baking soda',
    'barbecue sauce',
    'basil',
    'bay leaves',
    'black pepper',
    'bread crumbs',
    'brown rice',
    'brown sugar',
    'butter',
    'canola oil',
    'cayenne pepper',
    'chicken broth',
    'chili powder',
    'chives',
    'cider vinegar',
    'cinnamon',
    'cloves',
    'coconut milk',
    'coconut oil',
    'cornmeal',
    'cornstarch',
    'cumin',
    'curry powder',
    'dijon mustard',
    'dried oregano',
    'dry pasta',
    'extra virgin olive oil',
    'fennel seeds',
    'fish sauce',
    'garlic',
    'garlic powder',
    'garlic salt',
    'ginger',
    'granulated sugar',
    'honey',
    'hot sauce',
    'italian seasoning',
    'ketchup',
    'kosher salt',
    'lemon juice',
    'lentils',
    'maple syrup',
    'mayonnaise',
    'nutmeg',
    'olive oil',
    'onion powder',
    'oregano',
    'paprika',
    'parmesan cheese',
    'peanut butter',
    'peanut oil',
    'pepper',
    'pickle relish',
    'quinoa',
    'raisins',
    'red pepper flakes',
    'red wine vinegar',
    'rice vinegar',
    'rosemary',
    'sage',
    'salt',
    'sesame oil',
    'soy sauce',
    'sriracha',
    'sugar',
    'tabasco',
    'tarragon',
    'thyme',
    'tomato paste',
    'tomato sauce',
    'vanilla extract',
    'vegetable broth',
    'vegetable oil',
    'vinegar',
    'walnuts',
    'white rice',
    'white sugar',
    'white vinegar',
    'whole wheat flour',
    'worcestershire sauce',
    'yeast',
]





def get_basics():
    st.markdown("**Let's learn about your kitchen basics and setup to create better recipes!**")
    st.markdown("We assume you have common ingredients (salt, pepper, olive oil). Let us know about the spices, herbs, and other ingredients you usually have on hand. The more thorough you are, the more possibilities there will be for your recipes.")
    with st.form(key='get_basics_form'):
        # Kitchen staples
        st.markdown("**1. Kitchen Staples:**")
        staples = st.multiselect("Select your staples:", kitchen_staples)
        other_staples = st.text_input("Enter any other staples not listed above (separated by commas). Leave blank if none:", value='')

        # Kitchen limitations
        st.markdown("**2. Kitchen Limitations:**")
        st.markdown("Enter any kitchen setup limitations, e.g., I don't have an oven, I don't have aluminum foil.")
        limitations = st.text_input("Enter any limitations you have:", value='none')

        st.markdown("**Review your selections before saving. Click 'Save and Continue' when you are ready.**")
        save_and_continue_button = st.form_submit_button("Save and Continue")

    if save_and_continue_button:
        if other_staples != 'none':
            staples.extend(other_staples.split(', '))
        st.session_state.staples = staples
        st.session_state.limitations = limitations
        st.session_state.user_page = 'get_user_data'
        st.experimental_rerun()


def add_user_data(preferences, favorite_ingredients, least_favorite_ingredients, dietary_restrictions):
    user_data = {
        'preferences': preferences,
        'favorite_ingredients': favorite_ingredients,
        'dietary_restrictions': dietary_restrictions,
        'least_favorite_ingredients': least_favorite_ingredients,
    }

    st.session_state['user_data'][st.session_state.name] = user_data
    st.session_state['user_data'][st.session_state.name]['recipes'] = {}
    if not st.session_state['user_data'][st.session_state.name].get('favorites_list'):
        st.session_state['user_data'][st.session_state.name]['favorites_list'] = []
    if not st.session_state['user_data'][st.session_state.name].get('least_favorites_list'):
        st.session_state['user_data'][st.session_state.name]['least_favorites_list'] = []
    if not st.session_state.get('staples_list'):
        st.session_state['staples_list'] = []
    if not st.session_state.get('staples_notes'):
        st.session_state['staples_notes'] = ""
    if not st.session_state.get('limitations'):
        st.session_state['limitations'] = ""

    
    





def get_user_data():
    st.markdown("#### Let's learn a little more about your so we can personalizes your recipes. 🏡🍲")
    st.markdown('---')
    
    
    st.markdown('##### Briefly tell us about your preferences and dietary restrictions below.  For each question, you can answer\
                in natural language i.e. "I love pasta and olives" or "I am vegan and gluten free":')

    with st.form(key='get_user_data_form'):
        # User name
        st.markdown("**1. Name:**")
        name = st.text_input("Enter your name:", value='')

        # User Preferences
        st.markdown("**2. Food Preferences:**")
        st.markdown("Describe your food preferences, e.g., I like spicy food, I hate olives. The more details, the better!")
        preferences = st.text_input("Enter your preferences:", value='')

        
        # User favorite ingredients
        st.markdown("**3. Ingredients I love:**")
        favorite_ingredients = st.multiselect("Tell us about ingredients you really love:", ingredients_list)

        # User least favorite ingredients
        st.markdown("**4. Ingredients I hate:**")
        least_favorite_ingredients = st.multiselect("Tell us about ingredients you really hate:", ingredients_list)

        # User dietary restrictions
        st.markdown("**4. Dietary Restrictions:**")
        st.markdown("Enter any dietary restrictions, e.g., gluten-free, vegan. Type 'none' if no restrictions.")
        dietary_restrictions = st.text_input("Enter any dietary restrictions:", value='none')

        if st.session_state.noob == True:
            st.warning('**We assume that you have basic ingredients in your kitchen, ie. salt, pepper, spices, etc and basic kitchen\
                       equipment.  If you would like to add more specific information to your profile, including a more detailed list of\
                       your preferences, you may select "My Information" from the sidebar menu to edit. The information that you have\
                       entered here will be stored for the duration of your session.**')
            
        st.markdown("**Review your selections before saving. Click 'Save and Continue' when you are ready.**")
        save_and_continue_button = st.form_submit_button("Save and Continue")
        if save_and_continue_button:
            st.session_state['name'] = name
            add_user_data(preferences, favorite_ingredients, least_favorite_ingredients, dietary_restrictions)
            st.success("Your information has been saved!")
            st.experimental_rerun()
       

    
    
# Create a function to allow the user to view and edit their data
def display_user_data():
    user_data = st.session_state['user_data'][st.session_state.name]
    st.markdown("#### Review the data below and make any changes if necessary")
    with st.form("display_user_data"):
        st.markdown('#### Your current profile:')
        # Favorite ingredients
        # Create a list from the user's current favorite ingredients and the ingredients list
        st.markdown('**Favorite Ingredients:**')
        current_favorite_ingredients = user_data['favorite_ingredients']
        new_favorites_text = st.text_input("Enter any new favorite ingredients:", value=current_favorite_ingredients)
        st.markdown("**To select from a list of common ingredients to add to your favorites, select from the list below:**")
        new_favorites_list = st.multiselect("Select any new favorite ingredients:", ingredients_list)
        
        # Least favorite ingredients
        st.markdown('**Your least favorite ingredients.**')
        new_least_favorite_ingredients_text = st.text_input("Tell us about any ingredients you really hate:", value=user_data['least_favorite_ingredients'])
        st.markdown("**If you would like to select form a list of ingredients to add to your hated ingredients, do so below:")     
        hated_ingredients_list = st.multiselect("Select any ingredients you really hate:", ingredients_list)  

        # Dietary restrictions
        st.markdown('**Your Dietary Restrictions**')
        new_dietary_restrictions = st.text_input("Enter any dietary restrictions:", value=user_data['dietary_restrictions'])

        # Preferences
        st.markdown('**Your prefences.**')
        new_preferences = st.text_input("Enter any preferences:", value=user_data['preferences'])

        # Staples
        st.markdown('**If you would like to add any specific staples that you carry on hand, you can select below:**')
        new_staples_list = st.multiselect("Select any staples you have on hand:", kitchen_staples)
        st.markdown("**Any notes about your staples?**")
        staples_notes = st.text_input("Enter any notes about your staples:", value='')

        # Limitations
        st.markdown('**If you have any specific kitchen limitations you would like to mention, do so here (i.e. no stove, no blender, etc.**')
        new_limitations = st.text_input("Enter any limitations:", value=st.session_state['limitations'])

        changes_submit_button = st.form_submit_button("Submit changes")
        
        if changes_submit_button:
            # Update the user's data
            add_user_data(new_preferences, new_favorites_text, new_least_favorite_ingredients_text, new_dietary_restrictions)
            
            # Update the session state
            st.session_state.staples_notes = staples_notes
            st.session_state.staples_list = new_staples_list
            st.session_state.user_data[st.session_state.name]['least_favorite_ingredients_list'] = hated_ingredients_list
            st.session_state.user_data[st.session_state.name]['favorite_ingredients_list'] = new_favorites_list
            st.session_state.limitations = new_limitations
            
          
            st.success("Your changes have been saved!")
           
def save_kid_data(favorite_ingredients, least_favorite_ingredients, dietary_restrictions, food_preferences, age, favorite_dishes):
    if 'kids_data' not in st.session_state:
        st.session_state['kids_data'] = {}
    
    kids_data = {
        'least_favorite_ingredients': least_favorite_ingredients,
        'favorite_ingredients': favorite_ingredients,
        'dietary_restrictions': dietary_restrictions,
        'favorite_dishes': favorite_dishes,
        'preferences': food_preferences,
        'age': age, 
        'recipes': {}
    }

    st.session_state.kids_data[st.session_state.kid_name] = kids_data
    
def get_new_child_data():
    st.markdown(f'####  Welcome to your recipe generator, {st.session_state.kid_name}! 🚂👩🏻‍🍳')
    st.markdown('---')
    st.success(f"Chef Waldo 👩🏻‍🍳🐈‍⬛:  Let's learn a little bit more about you, and then\
                we'll get to the fun part.  **Any text input questions you can answer in natural\
               language, no need to give it in any specific format.**")

    with st.form(key='get_new_child_data_form'):
        # Favorite ingredients
        st.markdown(f"**What are some ingredients that {st.session_state.kid_name} really loves?**")
        favorite_ingredients = st.multiselect("Select their least favorite ingredients:", value='')

        st.markdown(f'**What are some ingredients that {st.session_state.kid_name} really hates?**')
        least_favorite_ingredients = st.multiselect("Select their leat favorite ingredients:", value=kids_ingredients_list)
                
        # Dietary restrictions
        st.markdown("**2. Dietary Restrictions and Allergies:**")
        st.markdown("Enter any dietary restrictions or allergies, e.g., shellfish allergy, gluten-free, vegetarian, etc. Type 'none' if no restrictions.")
        dietary_restrictions = st.text_input("Enter any dietary restrictions:", value='none')

        # Favorite dishes
        st.markdown("**3. Favorite Dishes:**")
        st.markdown("Does your child have any dishes that they particularly love?  If so, you can tell us about them here.")
        favorite_dishes = st.text_input("Favorite dishes:", value='')

        
        # Preferences
        st.markdown("**4. Food Preferences:**")
        st.markdown("Describe your child's food preferences, e.g., spicy, sweet, or dislikes certain foods.")
        food_preferences = st.text_input("Enter your child's food preferences:", value='')

        # Age
        st.markdown("**5. Age:**")
        st.markdown("Choose your child's age to help us determine age-appropriate ways they can help prepare the meal.")
        age = st.slider("Select your child's age:", min_value=5, max_value=18, step=1)

        st.markdown('**Review your selections before saving. Click "Save and Continue" when you are ready.**')
        save_and_continue_button = st.form_submit_button("Save and Continue")

    if save_and_continue_button:
        if dietary_restrictions != '' and food_preferences != '':
            st.session_state['kids_recipe_page'] = 'kids_recipe_form'
            st.session_state.kids_recipe_page = 'kids_recipe_form'
            
            save_kid_data(favorite_ingredients, least_favorite_ingredients, dietary_restrictions, food_preferences, age, favorite_dishes)
            st.experimental_rerun()
        else:
            st.warning('**Please fill out all required fields before saving.**')


# Create a function to display the child's data
# If the user has not inputted any data, display a message to do so
def display_kids_data():
    if st.session_state.kids_data == {}:
        st.markdown(f"**Chef Waldo 👩🏻‍🍳🐈‍⬛:  It looks like you haven't entered any data for your child yet.  Click on the Kids Recipe Creator option\
                    on the sidebar to get started!**")
    else:
        # Pull the data from the session state
        st.markdown('**Please select which child you would like to view the data for.**')

        # Create a list of the kids names
        kids_names = list(st.session_state.kids_data.keys())

        # Create a selectbox to choose the child
        kid_name = st.selectbox("Select a child:", kids_names)

        # Display the data in a form for the user to see and edit if needed
        st.markdown(f"**Chef Waldo 👩🏻‍🍳🐈‍⬛:  Here is {kid_name}'s data.  If you need to make any changes, you can do so below.**")

        child_data_select_button = st.button(f"View and Edit {kid_name}'s Data")
        if child_data_select_button:
            st.session_state.kid_name = kid_name
            with st.form('kids_display_data_form'):
                kids_data = st.session_state.kids_data[kid_name]
                # Favorite ingredients
                # Create a list from the user's current favorite ingredients and other favorite ingredients
                current_favorite_ingredients = kids_data['favorite_ingredients']
                #  Sort the list
                current_favorite_ingredients = sorted(current_favorite_ingredients)

                # Create a list of choices from a set of the current favorite ingredients and the kids_ingredients list
                new_favorite_options = sorted(list(set(current_favorite_ingredients + kids_ingredients_list)))
                
                
                st.markdown('**Your favorite ingredients.**')
                new_favorite_ingredients = st.multiselect("Select your favorite ingredients:", new_favorite_options, default=current_favorite_ingredients)
                st.markdown('**If there are other ingredients that you particularly like that are not listed above,\
                            please enter them below, separated by commas.**')
                other_favorite_ingredients = st.text_input("Enter any other favorite ingredients:", value='none')


                # Dietary restrictions
                st.markdown(f'**{st.session_state.kid_name}\'s Restrictions**')
                new_dietary_restrictions = st.text_input("Enter any dietary restrictions:", value=kids_data['dietary_restrictions'])

                # Create a list from the user's current staples and the kitchen staples list
                # Remove any duplicates
                # Sort the list
                staples_choices = list(set(st.session_state.staples + kitchen_staples))
                staples_choices = sorted(staples_choices)
                
                st.markdown('**Your staples.**')
                new_staples = st.multiselect("Select your staples:", options = staples_choices, default=st.session_state.staples)

              
                 # Limitations
                st.markdown('**Your kitchen limitations.**')
                new_limitations = st.text_input("Enter any limitations:", value=st.session_state['limitations'])


                # Preferences
                st.markdown(f'**{st.session_state.kid_name}\'s preferences:**')
                new_preferences = st.text_input("Enter any preferences:", value=kids_data['preferences'])

                # Age
                st.markdown(f'**{st.session_state.kid_name}\'s age:**')
                new_age = st.slider("Enter your age:", value=kids_data['age'], min_value=5, max_value=18)

                changes_submit_button = st.form_submit_button("Submit changes")

                if changes_submit_button:
                    # Update the user's data
                    if other_favorite_ingredients != 'none':
                        new_favorite_ingredients.extend(other_favorite_ingredients.split(','))
                    kids_data['favorite_ingredients'] = new_favorite_ingredients
                    kids_data['dietary_restrictions'] = new_dietary_restrictions
                    kids_data['preferences'] = new_preferences
                    kids_data['age'] = new_age
                    
                    
                    # Update the session state
                    st.session_state['staples'] = new_staples
                    st.session_state['limitations'] = new_limitations
                    
                    st.success("Your changes have been saved!")

