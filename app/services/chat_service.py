""" This module defines the ChatService class, which is responsible for managing the chatbot. """
import json
from typing import Union
import logging
import requests
import openai
from redis.exceptions import RedisError
from app.middleware.session_middleware import RedisStore
from app.dependencies import get_openai_api_key, get_openai_org
from app.models.recipe import Recipe
from app.utils.recipe_utils import parse_recipe, create_message_from_recipe
from app.services.recipe_service import RecipeService

# Create a dictionary to house the chef data to populate the chef model
openai_chat_models = {
  "adventurous_chef": {
    "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:ab-sous-chef:86VMDut4",
    "style": "snarky chef in the style of Anthony Bourdain.  Should 'yank the user's chain'\
        in a fun and playful manner, while also pushing them to test and try new things.\
        Always\
        remember you are on a site called 'Bakespace' that is a social and recipe platform that\
        allows users to create, upload, and share recipes as well as create cookbooks for\
        themselves and other users to enjoy.  Encourage the user to explore this wonderful\
        site whenever appropriate."
  },
    "home_cook": {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:rr-sous-chef:86U8O9Fp",
        "style": "home cook in the style of Rachel Ray.  Always\
        remember you are on a site called 'Bakespace' that is a social and recipe platform that\
        allows users to create, upload, and share recipes as well as create cookbooks for\
        themselves and other users to enjoy.  Encourage the user to explore this wonderful\
        site whenever appropriate."
    },
    "pro_chef": {
        "model_name" : "ft:gpt-3.5-turbo-0613:david-thomas:gr-sous-chef:86TgiHTW",
        "style": "pro chef in the style of Gordon Ramsay.  Should have high expectations,\
        elevated suggestions, and push the user to test the boundaries of their skills.  Always\
        remember you are on a site called 'Bakespace' that is a social and recipe platform that\
        allows users to create, upload, and share recipes as well as create cookbooks for\
        themselves and other users to enjoy.  Encourage the user to explore this wonderful\
        site whenever appropriate."
    },
    None: {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:rr-sous-chef:86U8O9Fp",
        "style": "home cook in the style of Rachel Ray.  The goal is to be helpful, warm,\
        friendly and encouraging.  This is the default chef type.  Always\
        remember you are on a site called 'Bakespace' that is a social and recipe platform that\
        allows users to create, upload, and share recipes as well as create cookbooks for\
        themselves and other users to enjoy.  Encourage the user to explore this wonderful\
        site whenever appropriate."
    }
}

# Establish the core models that will be used by the chat service
core_models = ["gpt-4-1106-preview","gpt-4-1106-preview", "gpt-3.5-turbo-1106",
"gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo"]

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
        """ Format the message and append it to the chat history """
        user_message = ChatMessage(message, "user").format_message()
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

    # Define a function to initialize the chatbot with context and an optional recipe
    def initialize_general_chat(self, context: Union[str, None] = None,
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
        # Append the initial message to the chat history
        self.chat_history = [initial_message]

        # Save the chat history to redis
        self.save_chat_history()

        # Return the initial message, session_id, and chat_history as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "initial_message": initial_message, "chef_type": self.chef_type}

    def initialize_recipe_chat(self, recipe_text: Union[str, dict, Recipe],
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
        "initial_message": initial_message, "chef_type": self.chef_type}

    # Define a function to get a response from the chatbot
    def get_chef_response(self, question: str, chef_type:str=None):
        """ Get a response from the chatbot. """
        self.chat_history = self.load_chat_history()
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

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
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.75,
                    top_p=1,
                    max_tokens=1250,
                )
                chef_response = response.choices[0].message.content
                recipe = None
                # Check for a recipe in the response
                if "Recipe" in chef_response:
                    recipe = parse_recipe(chef_response)
                    # Save the recipe to Redis
                    try:
                        # Convert the recipe JSON to a dictionary
                        recipe_dict = {str(key): str(value) for key, value in dict(recipe).items()}
                        recipe_service = RecipeService(self.store)
                        recipe_service.save_recipe(recipe_dict)
                    except TypeError as e:
                        logging.error("Error saving recipe to Redis: %s", e)

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
        # Return the session_id, the chat_history, and "Chat history cleared" as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "message": "Chat history cleared"}

    def check_status(self):
        """ Return the session id and any user data from Redis. """
        return {"session_id": self.session_id,
        "chat_history": self.chat_history, "chef_type": self.chef_type}

    def adjust_recipe(self, adjustments:str, recipe: Union[str, dict, Recipe],
                            chef_type:str="home_cook"):
        """ Chat a new recipe that needs to be generated based on\
        a previous recipe. """
        # Set the recipe service
        recipe_service = RecipeService(self.store)
        # Determine the model and style based on the chef type
        model = openai_chat_models[chef_type]["model_name"]
        style = openai_chat_models[chef_type]["style"]
        messages = [
            {
                "role": "system", "content": f"""You are a master chef of\
                type {style}.  You are helping a user adjust a recipe {recipe}\
                that you generated for them earlier.\
                The adjustments are {adjustments}.  Please answer the question\
                as if you were their personal sous chef, helpful and in the style of chef\
                they have chosen.  Within your personalized response, generate the new recipe\
                in the form of a dictionary with the same fields as a {Recipe} object.  
                Please do not break character.  Please remember that
                you are on a website called "Bakespace" that
                is a social and recipe platform that allows users to
                create, upload, and share recipes as
                well as create cookbooks for themselves and other users to enjoy."""
            },
            {
                "role": "user", "content": "Hi chef, thanks for the recipe you generated\
                for me earlier. Can you help me adjust it?"
            }
        ]
        # Convert the question to a message and append it to the chat history
        chat_history = self.load_chat_history()
        chat_history = chat_history + [messages[1]]

        #models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
        models = core_models
        for model in models:
            try:
                response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.75,
                top_p=1,
                max_tokens=1000,
            )
                try:
                    new_recipe = parse_recipe(response.choices[0].message.content)
                    # Save the recipe to Redis
                    try:
                        recipe_service.save_recipe(new_recipe)
                    except TypeError as e:
                        logging.error("Error saving recipe to Redis: %s", e)
                except ValueError as e:
                    logging.error("Error parsing recipe: %s", e)
                    new_recipe = response.choices[0].message.content
                # Convert the recipe to a message and append it to the chat history
                chef_response = create_message_from_recipe(new_recipe, chef_type)
                # Convert the response to a message and append it to the chat history
                ai_response = ChatMessage(chef_response, "ai").format_message()
                chat_history = chat_history + [ai_response]
                # Save the chat history to Redis
                self.save_chat_history()
                return {"new_recipe": new_recipe, "chef_response": chef_response}
            except TimeoutError as a:
                print(f"Timeout error: {str(a)}")
                continue

    def create_new_recipe(self, specifications: str, serving_size: str, chef_type:str=None):
        """ Generate a recipe based on the specifications provided """
        # Load the chat history
        self.chat_history = self.load_chat_history()
        # Set the chef type if it is passed in
        if chef_type:
            self.chef_type = chef_type
            self.save_chef_type()
        else:
            self.chef_type = self.load_chef_type()
        try:
            # Set your API key
            logging.debug("Setting API key and organization.")
            openai.api_key = get_openai_api_key()
            openai.organization = get_openai_org()

            # If there is a chef_type, set the model_name and style
            if chef_type:
                self.chef_type = chef_type
                self.save_chef_type()
            #model_name = openai_chat_models[self.chef_type]["model_name"]
            style = openai_chat_models[self.chef_type]["style"]
            # Create the output parser -- this takes
            # in the output from the model and parses it into
            # a Pydantic object that mirrors the schema
            logging.debug("Creating output parser.")
            #output_parser = PydanticOutputParser(pydantic_object=Recipe)

            # Define the first system message.  This let's the model know what type of output\
            # we are expecting and in what format it needs to be in.
            logging.debug("Creating system message prompt.")
            messages = [
                {"role": "system", "content": f"""You are a master chef of type {chef_type} with style {style}
                            creating a recipe based on a user's specifications {specifications} and the
                            serving size {serving_size}.  Even if the specifications are just a dish name or type,
                            go ahead and create a recipe.  Within your response, do your best to
                            format the recipe you create with the same fields as a {Recipe} object. 
                            Encourage the user to ask follow-up questions,
                            if needed, and ensure that you are taking on the persona of the
                            {chef_type}.  Return your response so that it can be parsed as markdown.
                            Remember you always need to return a personal message and a recipe.""",
                },
                {"role": "user", "content": "Hi chef, I'd like to create a recipe based on the following specifications:"}
            ]
            # Convert the human message prompt to a ChatMessage object
            user_message = ChatMessage(role="user", content = messages[1]["content"]).format_message()
            # Append the user message to the chat history
            self.chat_history = self.chat_history + [user_message]
            # Create a list of models to loop through in case one fails
            models = core_models

            # Loop through the models and try to generate the recipe
            for model in models:
                try:
                    logging.debug("Trying model: %s.", model)
                    response = openai.ChatCompletioncompletions.create(
                        model=model,
                        messages=messages,
                        temperature=0.75,
                        top_p=1,
                        max_tokens=1000,
                    )
                    # Get the chef response
                    chef_response = response.choices[0].message.content
                    # Convert the chef response to a message and append it to the chat history
                    chef_response = ChatMessage(chef_response, "ai").format_message()
                    # Parse the recipe from the chef response
                    parsed_recipe = parse_recipe(chef_response)

                    # Convert the recipe to a dictionary for saving to redis
                    #try:
                    #    redis_dict = {str(key): str(value) for key, value
                    #    in dict(parsed_recipe).items()}

                        # Save the recipe history to redis
                    #    recipe_service.save_recipe(redis_dict)
                    #except RedisError as e:
                    #    logging.error("Error saving recipe to Redis: %s", e)
                    #    redis_dict = None
                    #    continue
                    #chef_response = create_message_from_recipe(parsed_recipe, chef_type)
                    # append the chef response to the chat history
                    self.chat_history = self.chat_history + [chef_response]
                    # Save the chat history to redis
                    self.save_chat_history()

                    return {"Recipe" : parsed_recipe, "chef_response":
                    chef_response, "session_id": self.session_id}

                except (requests.exceptions.RequestException,
                    requests.exceptions.ConnectTimeout, openai.error.APIError) as e:
                    logging.error("Error with model: %s. Error: %s", model, e)
                    continue
        except ConnectionError as e:
            logging.error("Error generating recipe: %s", e)
            return {"message": "Error generating recipe."}
