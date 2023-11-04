""" This module defines the ChatService class, which is responsible for managing the chatbot. """
import json
from typing import Union
import logging
import requests
import openai
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from redis.exceptions import RedisError
from app.middleware.session_middleware import RedisStore
from app.dependencies import get_openai_api_key, get_openai_org
from app.models.recipe import Recipe
from app.utils.recipe_utils import parse_recipe
from app.services.recipe_service import RecipeService

# Create a dictionary to house the chef data to populate the chef model
openai_chat_models = {
  "adventurous_chef": {
    "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:ab-sous-chef:86VMDut4",
    "style": "adventurous chef in the style of Anthony Bourdain"
  },
    "home_cook": {
        "model_name": "ft:gpt-3.5-turbo-0613:david-thomas:rr-sous-chef:86U8O9Fp",
        "style": "home cook in the style of Rachel Ray"
    },
    "pro_chef": {
        "model_name" : "ft:gpt-3.5-turbo-0613:david-thomas:gr-sous-chef:86TgiHTW",
        "style": "professional chef in the style of Gordon Ramsey"
    },
}

# Establish the core models that will be used by the chat service
core_models = ["gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo"]

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
            chat_history_json = self.store.redis.get(f'{self.session_id}:chat_history')
            if chat_history_json:
                chat_history_dict = json.loads(chat_history_json)
                return chat_history_dict
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
            The context, if any, is {context}  Your chat history so far is {self.chat_history}
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
            would like to ask questions about.
            """
        }

        # Append the initial message to the chat history
        self.chat_history = [initial_message]

        # Save the chat history to redis
        self.save_chat_history()

        # Return the initial message, session_id, and chat_history as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "initial_message": initial_message, "chef_type": self.chef_type}

    def initialize_cookbook_chat(self, user_question: str, recipes_list: list = None,
                                chef_type:str=None) -> dict:
        """ Initialize the chatbot with a recipe. """
        if chef_type:
            self.chef_type = chef_type
            self.save_chef_type()

        initial_message = {
            "role": "system", 
            "content": f"""
            The user has created a cookbook that they would like to ask a question
            about.  The question is {user_question}.  The names of the recipes in the 
            cookbook are {recipes_list}.  Your chat history so far is {self.chat_history}. 
            You should answer as a chef of type {self.chef_type} in the style of
            {openai_chat_models[self.chef_type]["style"]} acting as the user's personal sous chef.
            Do not break character.
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
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        # Set the chef type if it is passed in
        if chef_type:
            self.chef_type = chef_type
            self.save_chef_type()

        # Format the message and add it to the chat history
        user_message = ChatMessage(question, "user").format_message()

        # Append the user message to the chat history
        self.chat_history = self.load_chat_history()
        self.chat_history = self.chat_history + [user_message]

        # Set the messages to send to the chatbot
        messages = self.chat_history

        # Get the appropriate model for the chef type
        model = openai_chat_models[self.chef_type]["model_name"]
        # List of models to use
        models = [model, model, model] + core_models

        # Iterate through the models until you get a successful response
        for model in models:
            try:
                response = requests.post(
                    url="https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai.api_key}"},
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": 750,
                        "frequency_penalty": 0.5,
                        "presence_penalty": 0.5,
                        "temperature": 1,
                        "top_p": 0.9,
                        "n": 1,
                    },
                    timeout=15,
                )
                response.raise_for_status()
                break  # If the response is successful, exit the loop

            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
                logging.error("Request failed for model %s due to: %s", model, err)
                if model == models[-1]:  # If this is the last model in the list
                    raise  # Propagate the error up
                else:
                    continue  # Try the next model

        response_json = response.json()
        chef_response = response_json["choices"][0]["message"]["content"]

        # Convert the chef_response to a message and append it to the chat history
        chef_response = ChatMessage(chef_response, "system").format_message()
        self.chat_history = self.chat_history + [chef_response]

        # Save the chat history to redis
        self.save_chat_history()

        # Return the session_id, the chat_history, and the chef_response as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "chef_response": chef_response, "chef_type": self.chef_type}

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

    async def adjust_recipe(self, adjustments:str, recipe: Union[str, dict, Recipe],
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
                in the form of {Recipe}.  Please do not break character."""
            },
            {
                "role": "user", "content": "Hi chef, thanks for the recipe you generated\
                for me earlier. Can you help me adjust it?"
            }
        ]
        # Add the user message to the chat history
        self.add_user_message(adjustments)
        models = [model, "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k"]
        for model in models:
            try:
                response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=1,
                top_p=1,
                max_tokens=500
            )
                new_recipe = parse_recipe(response.choices[0].message.content)
                # Save the recipe to Redis
                recipe_service.save_recipe(new_recipe)
                # Add the chef response to the chat history
                self.add_chef_message(response.choices[0].message.content)
                return {"response": response.choices[0].message.content, "new_recipe": new_recipe}
            except TimeoutError as a:
                print(f"Timeout error: {str(a)}")
                continue

    def create_new_recipe(self, specifications: str, chef_type:str=None):
        """ Generate a recipe based on the specifications provided """
        recipe_service = RecipeService(self.store)
        try:
            # Set your API key
            logging.debug("Setting API key and organization.")
            openai.api_key = get_openai_api_key()
            openai.organization = get_openai_org()

            # If there is a chef_type, set the model_name and style
            if chef_type:
                self.chef_type = chef_type
                self.save_chef_type()
            model_name = openai_chat_models[self.chef_type]["model_name"]
            style = openai_chat_models[self.chef_type]["style"]
            # Create the output parser -- this takes
            # in the output from the model and parses it into
            # a Pydantic object that mirrors the schema
            logging.debug("Creating output parser.")
            output_parser = PydanticOutputParser(pydantic_object=Recipe)

            # Define the first system message.  This let's the model know what type of output\
            # we are expecting and in what format it needs to be in.
            logging.debug("Creating system message prompt.")
            prompt = PromptTemplate(
                template = "You are a master chef of type {chef_type} with style {style}\
                            creating a based on a user's specifications {specifications}.\
                            The recipe should be returned in this format{format_instructions}.",
                input_variables = ["specifications"],
                partial_variables = {"format_instructions": output_parser.get_format_instructions()}
            )
            system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)

            # Define the user message.
            logging.debug("Creating user message prompt.")
            human_template = """Create a delicious recipe based
            on the specifications {specifications} provided.
            Please ensure the returned prep time, cook time, and total time are integers in minutes.\
            If any of the times are n/a\
            as in a raw dish, return 0 for that time.  Round the times to the nearest 5 minutes
            to provide a cushion and make for a more readable recipe."""
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

            # Create the chat prompt template
            logging.debug("Creating chat prompt.")
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                            human_message_prompt])

            # format the messages to feed to the model
            messages = chat_prompt.format_prompt(specifications=specifications,
                                                chef_type=chef_type, style=style).to_messages()

            # Create a list of models to loop through in case one fails
            models = [model_name, model_name, model_name] + ["gpt-3.5-turbo-0613",
                    "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]

            # Loop through the models and try to generate the recipe
            for model in models:
                try:
                    logging.debug("Trying model: %s.", model)

                    # Create the chat object
                    chat = ChatOpenAI(model_name=model, temperature=1, max_retries=3, timeout=15)

                    # Generate the recipe
                    recipe = chat(messages).content

                    # Parse the recipe
                    try:
                        parsed_recipe = output_parser.parse(recipe)
                    except ValueError as e:
                        logging.error("Error parsing recipe: %s", e)
                        parsed_recipe = parse_recipe(recipe)

                    # Convert the recipe to a dictionary for saving to redis
                    redis_dict = {str(key): str(value) for key, value
                    in dict(parsed_recipe).items()}

                    # Save the recipe history to redis
                    recipe_service.save_recipe(redis_dict)

                    return {"Recipe": parsed_recipe, "session_id": self.session_id}

                except (requests.exceptions.RequestException,
                    requests.exceptions.ConnectTimeout, openai.error.APIError) as e:
                    logging.error("Error with model: %s. Error: %s", model, e)
                    continue
        except ConnectionError as e:
            logging.error("Error generating recipe: %s", e)
            return {"message": "Error generating recipe."}
