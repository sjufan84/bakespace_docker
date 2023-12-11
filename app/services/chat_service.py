""" This module defines the ChatService class, which is responsible for managing the chatbot. """
import json
from typing import Union
import logging
import requests
from redis.exceptions import RedisError
from app.models.recipe import Recipe
from app.dependencies import get_openai_client
from app.middleware.session_middleware import RedisStore

client = get_openai_client()
# Create a dictionary to house the chef data to populate the chef model
openai_chat_models = {
  "adventurous_chef": {
    "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:ab-sous-chef:86VMDut4",
    "style": "snarky chef in the style of Anthony Bourdain.  Should 'yank the user's chain'\
        in a fun and playful manner, while also pushing them to test and try new things.\
        Always\
        remember you are on a site called 'Bakespace' that is a social and recipe platform that\
        allows users to create, upload, and share recipes as well as create cookbooks for\
        themselves and other users to enjoy in case they need a reminder.  You do not need to\
        constantly mention this, just something to be aware of."
  },
    "home_cook": {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:rr-sous-chef:86U8O9Fp",
        "style": "home cook in the style of Rachel Ray.  Always\
        remember you are on a site called 'Bakespace' that is a social and recipe platform that\
        allows users to create, upload, and share recipes as well as create cookbooks for\
        themselves and other users to enjoy in case they need a reminder.  You do not need to\
        constantly mention this, just something to be aware of."
    },
    "pro_chef": {
        "model_name" : "ft:gpt-3.5-turbo-0613:david-thomas:gr-sous-chef:86TgiHTW",
        "style": "pro chef in the style of Gordon Ramsay.  Should have high expectations,\
        elevated suggestions, and push the user to test the boundaries of their skills.  Always\
        remember you are on a site called 'Bakespace' that is a social and recipe platform that\
        allows users to create, upload, and share recipes as well as create cookbooks for\
        themselves and other users to enjoy in case they need a reminder.  You do not need to\
        constantly mention this, just something to be aware of."
    },
    None: {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:rr-sous-chef:86U8O9Fp",
        "style": "home cook in the style of Rachel Ray.  The goal is to be helpful, warm,\
        friendly and encouraging.  This is the default chef type.  Always\
        remember you are on a site called 'Bakespace' that is a social and recipe platform that\
        allows users to create, upload, and share recipes as well as create cookbooks for\
        themselves and other users to enjoy in case they need a reminder.  You do not need to\
        constantly mention this, just something to be aware of."
    }
}

# Establish the core models that will be used by the chat service
core_models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k"]

class ChatMessage:
    """ A class to represent a chat message. """
    def __init__(self, content, role):
        self.content = content
        self.role = role
    def format_message(self):
        """ Format the message for the chat history. """
        # Return a dictionary with the format {"role": role, "content": content}
        return {"role": self.role, "content": self.content}

class ChatService:
    """ A class to represent the chatbot. """
    def __init__(self, store: RedisStore = None):
        self.store = store
        self.session_id = self.store.session_id
        self.chef_type = self.store.redis.get(f'{self.session_id}:chef_type')
        chat_history = self.store.redis.get(f'{self.session_id}:chat_history')
        if chat_history:
            self.chat_history = chat_history
        else:
            self.chat_history = []
        if self.chef_type:
            self.chef_type = self.chef_type
        else:
            self.chef_type = "home_cook"
            self.save_chef_type()
        self.thread_id = self.store.redis.get(f'{self.session_id}:thread_id')
        if self.thread_id:
            self.thread_id = self.thread_id
        else:
            self.thread_id = None


    def load_chat_history(self):
        """ Load the chat history from Redis. """
        try:
            # Load the chat history from redis.  If there is not chat history, return an empty list
            chat_history = self.store.redis.get(f'{self.session_id}:chat_history')
            if chat_history:
                return json.loads(chat_history)
            return []
        except RedisError as e:
            print(f"Failed to load chat history from Redis: {e}")
            return []

    def save_chat_history(self):
        """ Save the chat history to Redis. """
        try:
            chat_history_json = json.dumps(self.chat_history)
            self.store.redis.set(f'{self.session_id}:chat_history', chat_history_json)
        except RedisError as e:
            print(f"Failed to save chat history to Redis: {e}")
        return self.chat_history

    def save_chef_type(self):
        """ Save the chef type to Redis. """
        try:
            self.store.redis.set(f'{self.session_id}:chef_type', self.chef_type)
        except RedisError as e:
            print(f"Failed to save chef type to Redis: {e}")
        return self.chef_type

    # Define a function to load the chef type from Redis
    def load_chef_type(self):
        """ Load the chef type from Redis. """
        try:
            chef_type = self.store.redis.get(f'{self.session_id}:chef_type')
            if chef_type:
                return chef_type
            return "home_cook"
        except RedisError as e:
            print(f"Failed to load chef type from Redis: {e}")
            return "home_cook"

    def add_user_message(self, message: str):
        """ Add a message from the user to the chat history. """
        # Format the message and add it to the chat history
        user_message = ChatMessage(message, "user").format_message()
        self.chat_history = self.load_chat_history()
        self.chat_history.append(user_message)
        # Save the chat history to redis
        return self.save_chat_history()

    # Define a function to add a message from the chef to the chat history
    def add_chef_message(self, message: str):
        """ Add a message from the chef to the chat history. """  
        chef_message = ChatMessage(message, "ai").format_message()
        self.chat_history.append(chef_message)
        # Save the chat history to redis
        return self.save_chat_history()

    # Define a function to set the thread_id
    def set_thread_id(self, thread_id: str):
        """ Set the thread_id. """
        try:
            self.store.redis.set(f'{self.session_id}:thread_id', thread_id)
        except RedisError as e:
            print(f"Failed to save thread_id to Redis: {e}")
        return thread_id

    # Define a function to load the thread_id
    def get_thread_id(self):
        """ Get the thread_id. """
        try:
            thread_id = self.store.redis.get(f'{self.session_id}:thread_id')
            if thread_id:
                return thread_id
            return None
        except RedisError as e:
            print(f"Failed to load thread_id from Redis: {e}")
            return None


    # Define a function to initialize the chatbot with context and an optional recipe
    async def initialize_general_chat(self, context: Union[str, None] = None,
                                chef_type:str = None) -> dict:
        """ Initialize the chatbot with an optional context for general chat. """
        # Set the chef type if it is passed in
        if chef_type:
            self.chef_type = chef_type
            self.save_chef_type()
        # Set the initial message
        initial_message = {
            "role": "system", 
            "content": f"""
            The context, if any, is {context}  Your chat history so far is {self.chat_history}.
            Please remember that you are on a website called "Bakespace" that
            is a social and recipe platform that allows users to create, upload, and share recipes as
            well as create cookbooks for themselves and other users to enjoy.
            """
                        }
        # Add the initial message to the chat history
        self.chat_history = [initial_message]

        # Save the chat history to redis
        self.save_chat_history()

        # Log the chat history
        logging.log(logging.INFO, "Chat history: %s", self.chat_history)

        # Return the initial message, session_id, and chat_history as a json object
        logging.log(logging.INFO, "Session id: %s", self.session_id)
        
        return {"chat_history": self.chat_history, "session_id": self.session_id}

    '''def initialize_recipe_chat(self, recipe_text: Union[str, dict, Recipe],
    chef_type:str=None) -> dict:
        """ Initialize the chatbot with a recipe. """
        # Convert the recipe to a string if not already
        if isinstance(recipe_text, Recipe):
            recipe_text = str(recipe_text)

        if chef_type:
            self.chef_type = chef_type
            self.save_chef_type()

        initial_message = {
            "role": "system", 
            "content": f"""
            You have generated a recipe {recipe_text} that the user\
            would like to ask questions about. Please remember that you are on
            a website called "Bakespace" that
            is a social and recipe platform that allows
            users to create, upload, and share recipes as
            well as create cookbooks for themselves and other users to enjoy.
            """
        }

        # Append the initial message to the chat history
        self.chat_history = [initial_message]

        # Save the chat history to redis
        self.save_chat_history()

        # Return the initial message, session_id, and chat_history as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "initial_message": initial_message, "chef_type": self.chef_type}

    def initialize_cookbook_chat(self, recipes_list: list = None,
                                chef_type:str=None) -> dict:
        """ Initialize the chatbot with a recipe. """
        if chef_type:
            self.chef_type = chef_type
            self.save_chef_type()

        initial_message = {
            "role": "system", 
            "content": f"""
            The user has created a cookbook that they would like to ask a question
            about.  The names of the recipes in the 
            cookbook are {recipes_list}.  Your chat history so far is {self.chat_history}. 
            You should answer as a chef of type {self.chef_type} in the style of
            {openai_chat_models[self.chef_type]["style"]} acting as the user's personal sous chef.
            Do not break character.  Please remember that you are on a website called "Bakespace" that
            is a social and recipe platform that allows users to create, upload, and share recipes as
            well as create cookbooks for themselves and other users to enjoy.
            """
        }

        # Append the initial message to the chat history
        self.chat_history = [initial_message]

        # Save the chat history to redis
        self.save_chat_history()

        # Return the initial message, session_id, and chat_history as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "initial_message": initial_message, "chef_type": self.chef_type}'''

    # Define a function to get a response from the chatbot
    async def get_chef_response(self, question: str, chef_type:str=None):
        """ Get a response from the chatbot. """
        self.chat_history = self.load_chat_history()
        # Set your API key

        # Set the chef type if it is passed in
        if chef_type:
            self.chef_type = chef_type
            self.save_chef_type()
        # Format the message and add it to the chat history
        system_question = question + f"Please answer as a chef of type {self.chef_type} in the style of\
        {openai_chat_models[self.chef_type]['style']}.  This may be different than\
        the initial chef type.  Do not break character."
        # Convert the system question to a system message
        system_question = ChatMessage(system_question, "system").format_message()
        user_message = ChatMessage(question, "user").format_message()
        system_message = [
            {"role" : "system", "content": f"If the user requests a recipe in any way,\
            do your best to return the recipe with the same fields as a {Recipe} object within the message\
            to be parsed from the response later"
            },
        ]
        # Append the user message to the chat history
        messages = self.chat_history + [system_question] + system_message
        self.chat_history = self.chat_history + [user_message]

        # Get the appropriate model for the chef type
        #model = openai_chat_models[self.chef_type]["model_name"]
        # List of models to use
        #models = [model, model, model] + core_models
        models = core_models

        # Iterate through the models until you get a successful response
        for model in models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.75,
                    top_p=1,
                    max_tokens=1250,
                )
                chef_response = response.choices[0].message.content
                recipe = None
                # Check for a recipe in the response
                '''if "Recipe" in chef_response:
                    recipe = parse_recipe(chef_response)
                    # Save the recipe to Redis
                    try:
                        # Convert the recipe JSON to a dictionary
                        recipe_dict = {str(key): str(value) for key, value in dict(recipe).items()}
                        recipe_service = RecipeService(self.store)
                        recipe_service.save_recipe(recipe_dict)
                    except TypeError as e:
                        logging.error("Error saving recipe to Redis: %s", e)'''

                # Convert the chef_response to a message and append it to the chat history
                chef_response = ChatMessage(chef_response, "system").format_message()
                self.chat_history = self.chat_history + [chef_response]
                # Save the chat history to redis
                self.save_chat_history()

                # Return the session_id, the chat_history, and the chef_response as a json object
                return {"session_id": self.session_id, "chat_history": self.chat_history,
                 "chef_response": chef_response, "chef_type": self.chef_type, "recipe": recipe}

            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
                logging.error("Request failed for model %s due to: %s", model, err)
                continue  # Try the next model

    def clear_chat_history(self):
        """ Clear the chat history. """
        self.chat_history = []
        self.save_chat_history()
        # Reset the thread_id
        self.thread_id = None

        # Return the session_id, the chat_history, and "Chat history cleared" as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history, "thread_id": self.thread_id,
        "message": "Chat history cleared"}

    
    def check_status(self):
        """ Return the session id and any user data from Redis. """
        return {"session_id": self.session_id,
        "chat_history": self.chat_history, "chef_type": self.chef_type,
        "thread_id": self.thread_id}

   