""" This module defines the chat service and it's
related functions. """
import logging
from typing import Union
import json
import os
from dotenv import load_dotenv
import openai
from redis.exceptions import RedisError
from app.middleware.session_middleware import RedisStore
from app.services.recipe_service import RecipeService
from app.models.recipe import Recipe
from app.utils.recipe_utils import parse_recipe

load_dotenv()

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

# Establish openai api key and organization
openai.api_key = os.getenv("OPENAI_KEY2")
openai.organization = os.getenv("OPENAI_ORG2")

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
    """ A class to represent the chat service. """
    def __init__(self, store: RedisStore = None, chef_choice: str = None):
        """ Initialize the chat service. """
        self.store = store
        self.session_id = self.store.session_id
        chat_history = self.store.redis.get(f'{self.session_id}:chat_history')
        if chat_history:
            self.chat_history = json.loads(chat_history)  # No need to decode
        else:
            self.chat_history = []
        chef_choice = self.store.redis.get(f'{self.session_id}:chef_type')
        if chef_choice:
            self.chef_type = chef_choice
        else:
            self.chef_type = "general"

    def load_chat_history(self, session_id: str = None):
        """ Load the chat history from Redis and return as a list of dicts. """
        if not session_id:
            session_id = self.session_id
        try:
            chat_history_json = self.store.redis.get(f'{self.session_id}:chat_history')
            if chat_history_json:
                return json.loads(chat_history_json)  # No need to decode
            else:
                return []
        except RedisError as e:
            logging.error("Failed to load chat history from Redis: %s", e)
            return []

    def save_chat_history(self):
        """ Save the chat history to Redis as a list of dicts. """
        try:
            self.store.redis.set(f'{self.session_id}:chat_history', json.dumps(self.chat_history))
            return self.chat_history
        except RedisError as e:
            logging.error("Failed to save chat history to Redis: %s", e)
            return "Failed to save chat history to Redis"

    def add_message(self, message: str, role: str):
        """ Add a message to the chat history and save it. """
        formatted_message = ChatMessage(message, role).format_message()
        self.chat_history.append(formatted_message)
        return self.save_chat_history()

    def add_user_message(self, message: str):
        """ Add a user message to the chat history. """
        return self.add_message(message, "user")

    def add_chef_message(self, message: str):
        """ Add a chef message to the chat history. """
        return self.add_message(message, "ai")

    async def get_new_recipe(self, adjustments:str, recipe: Union[str, dict, Recipe],
                            recipe_service: RecipeService, chef_type:str="general"):
        """ Chat a new recipe that needs to be generated based on\
        a previous recipe. """
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

    async def recipe_chat(self, recipe:Union[Recipe, str, dict],
    question:str, chef_type:str="general"):
        """ Chat about questions related to a specific recipe that
        does not involve the creation of a new recipe. """
        chat_history =  self.load_chat_history()

        # Determine the model and style based on the chef type
        model = openai_chat_models[chef_type]["model_name"]
        style = openai_chat_models[chef_type]["style"]
        # Add the user message to the chat history
        self.add_user_message(question)
        messages = [
            {
                "role": "system", "content": f"""You are a master chef of\
                type {style}.  You are helping a user answer a question {question} about a\
                recipe {recipe} that you generated for them earlier.  Please answer the question\
                as if you were their personal sous chef, helpful and in the style of chef\
                they have chosen.  Please do not break character\
                during the chat.  Your chat history so far is {chat_history}"""
            },
            {
                "role": "user", "content": question
            }
        ]
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
                # Add the response to the chat history
                self.add_chef_message(response.choices[0].message.content)
                # Save the chat history to Redis
                self.save_chat_history()
                return {"response": response.choices[0].message.content,
                "chat_history": self.chat_history, "session_id": self.session_id}
            except TimeoutError as a:
                print(f"Timeout error: {str(a)}")
                continue

    async def general_chat(self, user_question:str, chef_type:str="general"):
        """ Chat about general questions that do not involve a recipe. """
        chat_history =  self.load_chat_history()
        model = openai_chat_models[chef_type]["model_name"]
        style = openai_chat_models[chef_type]["style"]
        messages = [
            {
                "role": "system", "content": f"""You are a master chef of\
                type {style}.  You are helping a user answer a question {user_question} about cooking.\
                The goal is to interact with them as if you were their personal sous chef.\
                helpful and in the style of chef they have chosen.  Please do not break character\
                during the chat.  Your chat history so far is {chat_history}"""
            },
            {
                "role": "user", "content": user_question
            }
        ]
        # Add the user message to the chat history
        self.add_user_message(user_question)
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
                # Add the response to the chat history
                self.add_chef_message(response.choices[0].message.content)
                # Save the chat history to Redis
                self.save_chat_history()
                return {"response": response.choices[0].message.content, "chat_history": self.chat_history,
                        "session_id": self.session_id}
            except TimeoutError as a:
                print(f"Timeout error: {str(a)}")
                continue

    def clear_chat_history(self):
        """ Clear the chat history. """
        self.chat_history = []
        self.save_chat_history()
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "message": "Chat history cleared"}

    def check_status(self):
        """ Return the session id and any user data from Redis. """
        return {"session_id": self.session_id, "chat_history": self.chat_history}
    
    def set_chef_type(self, chef_type: str):
        """ Set the chef type. """
        self.chef_type = chef_type
        # Save the chef type to Redis
        self.store.redis.set(f'{self.session_id}:chef_type', chef_type)
        return self.chef_type
    