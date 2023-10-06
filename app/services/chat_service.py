""" This module defines the chat service and it's
related functions. """
import logging
from typing import Union, Optional
import json
import os
from dotenv import load_dotenv
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
from ..middleware.session_middleware import RedisStore
from ..services.recipe_service import RecipeService
from ..models.recipe import Recipe

load_dotenv()

# Create a dictionary to house the chef data to populate the chef model
chef_data = {
    "gr" : {
        "chef_model" : "ft:gpt-3.5-turbo-0613:david-thomas:gr-sous-chef:86TgiHTW",
        "prompt" : "You are a chef in the style of Gordon Ramsay, professional,\
        intense, and demanding helping a user with their cooking questions.\
        Please answer their questions as if you were their personal sous chef."
    },
    "rr" : {
        "chef_model" : "ft:gpt-3.5-turbo-0613:david-thomas:rr-sous-chef:86U8O9Fp",
        "prompt" : "You are a chef in the style of Rachael Ray, friendly, bubbly,\
        and energetic helping a user with their cooking questions. Please answer\
        their questions as if you were their personal sous chef."
    },
    "ab" : {
        "chef_model" : "ft:gpt-3.5-turbo-0613:david-thomas:ab-sous-chef:86VMDut4",
        "prompt" : "You are a chef in the style of Anthony Bourdain, worldly,\
        adventurous, and curious helping a user with their cooking questions.\
        Please answer their questions as if you were their personal sous chef."
    }, 
    "general" : {
        "chef_model" : "ft:gpt-3.5-turbo-0613:david-thomas:sous-chef-core:84he6ouC",
        "prompt" : "You are a chef helping a user with their cooking questions.\
        Please answer their questions as if you were their personal sous chef."
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

    def load_chat_history(self):
        """ Load the chat history from Redis and return as a dict. """
        try:
            chat_history_json = self.store.redis.get(f'{self.session_id}:chat_history')
            return json.loads(chat_history_json.decode("utf-8")) if chat_history_json else []
        except Exception as e:
            logging.error(f"Failed to load chat history from Redis: {e}")
            return []

    def save_chat_history(self):
        """ Save the chat history to Redis. """
        try:
            chat_history_json = json.dumps(self.chat_history)
            self.store.redis.set(f'{self.session_id}:chat_history', chat_history_json)
        except Exception as e:
            logging.error(f"Failed to save chat history to Redis: {e}")
        return self.chat_history

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

    def get_new_recipe(self, user_question: str, original_recipe: dict,
                    recipe_service: RecipeService, recipe: Union[Recipe, str] = None,
                    chef_type: str = None):
        """ Get a new recipe from the chatbot. """
        # If the chef type is None, get the chef type from Redis
        if chef_type is None:
            chef_type = self.chef_type
        # If the chef type is different from the current chef type, update the chef type
        if chef_type != self.chef_type:
            self.set_chef_type(chef_type)
            
        # If the recipe is None, load the current recipe from Redis
        if recipe is None:
            original_recipe = recipe_service.load_recipe()
        else:
            original_recipe = recipe

        # Load the chat history from redis
        chat_history = self.load_chat_history()
        chat_history = json.dumps(chat_history) if\
        isinstance(chat_history, dict) else chat_history

        # Load the chef model and prompt based on the chef choice
        sc_model = chef_data[chef_type]["chef_model"]
        chef_prompt = chef_data[chef_type]["prompt"]

        # Create the output parser -- this takes in the output from the model
        # and parses it into a Pydantic object that mirrors the schema
        logging.debug("Creating output parser.")
        output_parser = PydanticOutputParser(pydantic_object=Recipe)

        # Define the first system message.  This let's the model know what type of output
        # we are expecting and in what format it needs to be in.
        logging.debug("Creating system message prompt.")
    
        # format the messages to feed to the model
        messages = [
            {
                "role" : "system", "content" : f"{chef_prompt}.  You are helping\
                a user change a recipe change a recipe {original_recipe}\
                based on their question {user_question}.Please return the new recipe\
                in the same format as the original recipe."
            },
            {
                "role" : "user", "content" : f"Please help me change the recipe\
                {original_recipe} based on my question {user_question}\
                and return the new recipe in the same format as the original recipe."
            }
        ]

        # Format the user question and append it to the chat_history
        user_question = ChatMessage(user_question, "user").format_message()
        chat_history.append(user_question)

        # List of models to use
        models = [sc_model] + core_models

         # Loop through the models and try to generate the recipe
        for model in models:
            try:
                
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.9,
                    max_tokens=1500,
                    top_p=1,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                )
                chef_response = response.choices[0].message.content
                try:
                    parsed_recipe = output_parser.parse(chef_response)
                except Exception as e:
                    parsed_recipe = chef_response
                    print(f"Error parsing recipe: {e}")
                # Format the chef response and append it to the chat_history
                chef_response = ChatMessage(chef_response, "system").format_message()
                chat_history.append(chef_response)
                
                # Save the chat history to redis
                self.save_chat_history()  

                # Parse the recipe
                parsed_recipe_dict = parsed_recipe.dict() if isinstance(parsed_recipe, Recipe) else parsed_recipe

                # Save the recipe to redis
                recipe_service.save_recipe(parsed_recipe_dict)

                # Return the parsed recipe and the chef response
                return {"recipe": parsed_recipe_dict, "chef_response": chef_response, "chat_history": chat_history} 
            except Exception as e:
                logging.debug(f"Model {model} failed with error: {e}")
                continue

    def get_chef_attributes(self):
        """ Get the chef attributes depending on the chef choice. """
        chef_attributes = chef_data[self.chef_type]
        return {"chef_type": self.chef_type, "chef_attributes": chef_attributes}

    
    def get_recipe_chef_response(self, question: str, recipe_service: RecipeService,
                                recipe: Union[Recipe, str] = None, chef_type: str = None):
        """ Get a response from the chatbot regarding a recipe-related question. """
        # If the chef type is None, get the chef type from Redis
        if chef_type is None:
            chef_type = self.chef_type
        # If the chef type is different from the current chef type, update the chef type
        if chef_type != self.chef_type:
            self.set_chef_type(chef_type)
        # If the recipe is None, try to load the recipe from Redis
        # If that fails, throw an error
        if recipe is None:
            try:
                recipe = recipe_service.load_recipe()
            except ValueError as e:
                logging.error(f"Failed to load recipe from Redis: {e}")
                return None
        
        # Load the chat history from Redis
        self.chat_history = self.load_chat_history()

        # Get the chef model and prompt based on the chef choice
        chef_type = self.chef_type
        sc_model = chef_data[chef_type]["chef_model"]
        chef_prompt = chef_data[chef_type]["prompt"]
        # Define the first system message.  This let's the model know what type of output\
        # we are expecting and in what format it needs to be in.
        logging.debug("Creating system message prompt.")
        prompt = PromptTemplate(
            template = "{chef_prompt}. You are helping a user answer a question\
            {question} about a recipe {recipe} that you generated for them.\
            Your chat history so far is {chat_history}.",
        input_variables = ["question", "recipe", "chat_history", "chef_prompt"],
        )
        system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)
        
        # Define the user message.
        logging.debug("Creating user message prompt.")
        human_template = "Please answer my question {question} about the recipe\
        {recipe} you provided me."
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)    
        
        # Create the chat prompt template
        logging.debug("Creating chat prompt.")
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                        human_message_prompt])

        # format the messages to feed to the model
        messages = chat_prompt.format_prompt(question=question, recipe=recipe,
                                            chat_history=self.chat_history,
                                            chef_prompt=chef_prompt).to_messages()

        # Format the message and add it to the chat history
        user_message = ChatMessage(question, "user").format_message()

        # Append the user message to the chat history
        self.chat_history.append(user_message)
        
        # List of models to use
        models = [sc_model] + core_models
         # Loop through the models and try to generate the recipe
        for model in models:
            try:
                logging.debug(f"Trying model: {model}.")
                
                # Create the chat object
                chat = ChatOpenAI(model_name = model, temperature = 1, max_retries=3, timeout=15)

                # Generate the chef response
                chef_response = chat(messages).content                

                # Format the chef response and add it to the chat history
                chef_response = ChatMessage(chef_response, "system").format_message()
                self.chat_history.append(chef_response)

                # Save the chat history to redis
                self.save_chat_history()

                # Return the chat_history, the session_id, and the recipe
                return {"session_id": self.session_id, "chat_history": self.chat_history, "chef_response": chef_response}
            
            except requests.exceptions.HTTPError as e:
                logging.error(f"Failed to get response from chatbot: {e}")
                return None


    def get_chef_response(self, question: str, chef_type: Optional[str] = None):
        """ Get a response from the chatbot. """
        # If the chef choice is None, get the chef choice from Redis
        if chef_type is None:
            chef_type = self.chef_type
        # If the chef choice is different from the current chef choice, update the chef choice

        # Get the chef model and prompt based on the chef choice
        chef_type = self.chef_type
        sc_model = chef_data[chef_type]["chef_model"]
        chef_prompt = chef_data[chef_type]["prompt"]
        
        # Initialize chat messages
        messages = [
            {
                "role": "system",
                "content": f"{chef_prompt}. Your chat history so far\
                            is {self.chat_history}."
            },
            {
                "role": "user",
                "content": f"Please answer my question {question} about cooking."
            }
        ]
        
        # Format user message and append to chat history
        self.add_message(question, "user")
        
        
        # Iterate through models until a successful response is received
        models = [sc_model] + core_models
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
                break  # Exit loop on success
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
                logging.error(f"Request failed for model {model} due to: {err}")
                if model == models[-1]:  # If last model in the list
                    raise  # Propagate error up
                else:
                    continue  # Try next model
        
        # Parse response and append to chat history
        response_json = response.json()
        chef_response = response_json["choices"][0]["message"]["content"]
        self.add_message(chef_response, "system")

        # Return session details as JSON object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
                "chef_response": chef_response}

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
    
    def get_personalized_recipe_response(self, recipe, question):
        """ Getting a more personalized response from the chef. """
        # Load the chef model and prompt based on the chef choice
        chef_type = self.chef_type
        sc_model = chef_data[chef_type]["chef_model"]
        chef_prompt = chef_data[chef_type]["prompt"]
        # Define the first system message.  This let's the model know what type of output\
        # we are expecting and in what format it needs to be in.
        messages = [
            {
            "role":"system", "content": f"{chef_prompt}.  You have created a recipe\
            {recipe} for the user.  Please provide a personalized response to the user based\
            on their original question {question} and the recipe you provided them.  Make sure\
            you include the recipe text in your response."
            },
        ]
        models = [sc_model] + core_models

        # Loop through the models and try to generate the response
        for model in models:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.9,
                    max_tokens=1500,
                    top_p=1,
                    frequency_penalty=0.5,
                    presence_penalty=0.5,
                )
                chef_response = response.choices[0].message.content
                return chef_response
            except Exception as e:
                logging.debug(f"Model {model} failed with error: {e}")
                continue

