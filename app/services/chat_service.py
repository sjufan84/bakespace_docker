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
from ..middleware.session_middleware import RedisStore
from ..dependencies import get_openai_api_key, get_openai_org
from ..services.recipe_service import RecipeService
from ..models.recipe import Recipe


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
    def __init__(self, store: RedisStore = None):
        """ Initialize the chat service. """
        self.store = store
        self.session_id = self.store.session_id
        chat_history = self.store.redis.get(f'{self.session_id}:chat_history')
        if chat_history:
            self.chat_history = json.loads(chat_history)  # No need to decode
        else:
            self.chat_history = []

    def load_chat_history(self):
        try:
            chat_history_json = self.store.redis.get(f'{self.session_id}:chat_history')
            if chat_history_json:
                chat_history_dict = json.loads(chat_history_json.decode("utf-8"))
                return chat_history_dict
            return []
        except Exception as e:
            print(f"Failed to load chat history from Redis: {e}")
            return []

        
    def save_chat_history(self):
        """ Save the chat history to Redis. """
        try:
            chat_history_json = json.dumps(self.chat_history)
            self.store.redis.set(f'{self.session_id}:chat_history', chat_history_json)
        except Exception as e:
            print(f"Failed to save chat history to Redis: {e}")
        return self.chat_history
    
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


    # Define a function to get a new recipe from the chatbot
    def get_new_recipe(self, user_question: str, original_recipe: dict,
                    recipe_service: RecipeService, recipe: Union[Recipe, str] = None,
                    chef_type: str = "general"):
        """ Get a new recipe from the chatbot. """
        # Set the api key and organization
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        # If the recipe is None, load the current recipe from Redis
        if recipe is None:
            original_recipe = recipe_service.load_recipe()
        else:
            original_recipe = recipe

        # Load the chat history from redis
        chat_history = self.load_chat_history()
        chat_history = json.dumps(chat_history) if\
        isinstance(chat_history, dict) else chat_history

        # Create the output parser -- this takes in the output from the model
        # and parses it into a Pydantic object that mirrors the schema
        logging.debug("Creating output parser.")
        output_parser = PydanticOutputParser(pydantic_object=Recipe)

        # Define the first system message.  This let's the model know what type of output\
        # we are expecting and in what format it needs to be in.
        logging.debug("Creating system message prompt.")
    
        # format the messages to feed to the model
        messages = [
            {
                "role" : "system", "content" : f"You are a\
                master chef of type {chef_type} helping a user change a recipe {original_recipe}\
                based on their question {user_question}.\
                Please return the new recipe in the same format as the original recipe."
            },
            {
                "role" : "user", "content" : f"Please help me change the recipe {original_recipe} based on my question {user_question}\
                and return the new recipe in the same format as the original recipe."
            }
        ]

        # Format the user question and append it to the chat_history
        user_question = ChatMessage(user_question, "user").format_message()
        chat_history.append(user_question)

        # List of models to use
        models = ["gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo"]

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

    def get_recipe_chef_response(self, question: str, recipe_service: RecipeService,
                                chef_type : str = "general", recipe: Union[Recipe, str] = None):
        """ Get a response from the chatbot. """
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        # If the recipe is None, try to load the recipe from Redis
        # If that fails, throw an error
        if recipe is None:
            try:
                recipe = recipe_service.load_recipe()
            except Exception as e:
                logging.error(f"Failed to load recipe from Redis: {e}")
                return None
        
        # Load the chat history from Redis
        self.chat_history = self.load_chat_history()

        # Define the first system message.  This let's the model know what type of output\
        # we are expecting and in what format it needs to be in.
        logging.debug("Creating system message prompt.")
        prompt = PromptTemplate(
            template = "You are a master chef helping a user answer a question\
            {question} about a recipe {recipe} that you generated for them.\
            Your chef style is {chef_type} Your chat history so far is {chat_history}.\
            Please answer them as if you were their personal sous chef!",
        input_variables = ["question", "recipe", "chat_history", "chef_type"],
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
                                            chef_type=chef_type).to_messages()

        # Format the message and add it to the chat history
        user_message = ChatMessage(question, "user").format_message()

        # Append the user message to the chat history
        self.chat_history.append(user_message)
        
        # List of models to use
        models = ["gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo"]

         # Loop through the models and try to generate the recipe
        for model in models:
            try:
                logging.debug(f"Trying model: {model}.")
                
                # Create the chat object
                chat = ChatOpenAI(model_name = model, temperature = 1, max_retries=3, timeout=15)

                # Generate the chef response
                chef_response = chat(messages).content                

                # Parse the response

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


    # Define a function to get a response from the chatbot
    def get_chef_response(self, question: str, chef_type: str = "general"):
        """ Get a response from the chatbot. """
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        # Generate the messages to send to the model
        messages = [
            {
            "role" : "system", "content" : f"You are a master chef answering\
            a user's question {question}.  You are a {chef_type} type of chef.\
            Your chat history so far is {self.chat_history}.  Please respond\
            to the user's question as their personal sous chef of type {chef_type}."
            },
            {
            "role" : "user", "content" : f"Please answer my question {question}\
            as my personal sous chef of type {chef_type}."
            }
        ]

        # Format the message and add it to the chat history
        user_message = ChatMessage(question, "user").format_message()

        # Append the user message to the chat history
        self.chat_history.append(user_message)
        
        # List of models to use
        models = ["gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo"]

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
                logging.error(f"Request failed for model {model} due to: {err}")
                if model == models[-1]:  # If this is the last model in the list
                    raise  # Propagate the error up
                else:
                    continue  # Try the next model

        response_json = response.json()
        chef_response = response_json["choices"][0]["message"]["content"]
            
        # Convert the chef_response to a message and append it to the chat history
        chef_response = ChatMessage(chef_response, "system").format_message()
        self.chat_history.append(chef_response)

        # Save the chat history to redis
        self.save_chat_history()

        # Return the session_id, the chat_history, and the chef_response as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "chef_response": chef_response}

    def clear_chat_history(self):
        """ Clear the chat history. """
        self.chat_history = []
        self.save_chat_history()
        # Return the session_id, the chat_history, and "Chat history cleared" as a json object
        return {"session_id": self.session_id, "chat_history": self.chat_history,
        "message": "Chat history cleared"}
    
    def check_status(self):
        """ Return the session id and any user data from Redis. """
        return {"session_id": self.session_id, "chat_history": self.chat_history}