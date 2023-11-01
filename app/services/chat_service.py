""" This module defines the ChatService class, which is responsible for managing the chatbot. """
import json
from typing import Union
import logging
import requests
import openai
from redis.exceptions import RedisError
from ..middleware.session_middleware import RedisStore
from ..dependencies import get_openai_api_key, get_openai_org

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
    "general": {
        "model_name": "gpt-turbo-0613",
        "style": "master sous chef in the style of the best chefs in the world"
    }
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

    def set_initial_prompt(self):
        """ Set the initial prompt for the chef. """
        initial_prompt = [
            {
                "role" : "system", "content" : f"""
                You are a master chef of type {self.chef_type} with style {openai_chat_models[self.chef_type]["style"]}
                answering a user's questions about cooking.  Answer you think the chef would.  The goal is to be
                the user's personal sous chef.  Do not break character as the style and type of chef the user
                has chosen.  
                """
            },
        ]
        return initial_prompt

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
            The context, if any, is {context}  Your chat history so far is {self.chat_history[1:]}
            """
                        }
        # Append the initial message to the chat history
        self.chat_history = [initial_message]

        # Save the chat history to redis
        self.save_chat_history()

        # Return the initial message, session_id, and chat_history as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "initial_message": initial_message, "chef_type": self.chef_type}

    def initialize_recipe_chat(self, recipe_text: str, chef_type:str=None) -> dict:
        """ Initialize the chatbot with a recipe. """
        if chef_type:
            self.chef_type = chef_type
            self.save_chef_type()

        initial_message = {
            "role": "system", 
            "content": f"""
            You have generated a recipe {recipe_text} that the user\
            would like to ask questions about.  Your chat history so far is {self.chat_history[1:]} 
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

        # Set the messages to be passed to the API
        messages = self.set_initial_prompt() + self.chat_history

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
