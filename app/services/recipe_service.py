""" This module contains the recipe service class. """
import json
import openai
import requests
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from ..models.recipe import Recipe
from ..dependencies import get_openai_api_key, get_openai_org
from ..middleware.session_middleware import RedisStore

class RecipeService:
    """ A class to represent the recipe service. """
    def __init__(self, store: RedisStore = None):
        self.store = store or RedisStore()
        self.session_id = self.store.session_id
       
        recipe_history = self.store.redis.getrange(f'{self.session_id}_recipe_history', start = 0, end = -1)
        if recipe_history:
            self.recipe_history = recipe_history
        else:
            self.recipe_history = []


    # Create a function to load the recipe history from redis
    def load_recipe_history(self):
        try:
            recipe_history_json = self.store.redis.getrange(f'{self.session_id}_recipe_history', start = 0, end = -1)
            if recipe_history_json:
                recipe_history_dict = json.loads(recipe_history_json)
                return [message for message in recipe_history_dict]
            else:
                return []
        except Exception as e:
            print(f"Failed to load recipe history from Redis: {e}")
            return []
        
    # Create a function to save the recipe history to redis
    def save_recipe_history(self):
        """ Save the recipe history to Redis. """
        try:
            # Save the recipe history to redis
            recipe_history_json = json.dumps(self.recipe_history)
            self.store.redis.setrange(f'{self.session_id}_recipe_history', 0, recipe_history_json)
        except Exception as e:
            print(f"Failed to save recipe history to Redis: {e}")
        return self.recipe_history
    
    # Create a function to be able to load a recipe from the store by the recipe_name
    def load_recipe(self, recipe_name: str):
        try:
            recipe_json = self.store.redis.get(f'{self.session_id}_recipe_history : {recipe_name}')
            if recipe_json:
                recipe_dict = json.loads(recipe_json)
                return recipe_dict
            else:
                return None
        except Exception as e:
            print(f"Failed to load recipe from Redis: {e}")
            return None
        
    # Create a function to save a recipe to the store by the recipe_name
    def save_recipe(self, recipe_name: str, recipe: dict):
        try:
            # Save the recipe to redis
            recipe_json = json.dumps(recipe_name)
            self.store.redis.set(f'{self.session_id}_recipe_history : {recipe_name}', recipe_json)
        except Exception as e:
            print(f"Failed to save recipe to Redis: {e}")
        return recipe
    
    # Create a function to delete a recipe from the store by the recipe_name
    def delete_recipe(self, recipe_name: str):
        """ Delete a recipe from the store by the recipe_name """
        try:
            # Delete the recipe from redis
            self.store.redis.delete(f'{self.session_id}_recipe_history : {recipe_name}')
        except Exception as e:
            print(f"Failed to delete recipe from Redis: {e}")
        return recipe_name
    
    # Create a function to delete the recipe history from the store
    def delete_recipe_history(self):
        """ Delete the recipe history from the store """
        try:
            # Delete the recipe history from redis
            self.store.redis.delete(f'{self.session_id}_recipe_history : *')
        except Exception as e:
            print(f"Failed to delete recipe history from Redis: {e}")
        return self.recipe_history

    def execute_generate_recipe(self, specifications: str):
        """ Generate a recipe based on the specifications provided """
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        # Create the output parser -- this takes in the output from the model and parses it into a Pydantic object that mirrors the schema
        output_parser = PydanticOutputParser(pydantic_object=Recipe)

        
        # Create the prompt template from langchain to query the model and parse the output
        # We will format system, user, and AI messages separately and then pass the formatted messages to the model to
        # generate the recipe in a specific format using the output parser

        # Define the first system message.  This let's the model know what type of output\
        # we are expecting and in what format it needs to be in.
        prompt = PromptTemplate(
            template = "You are a master chef creating a based on a user's specifications {specifications}.\
                        The recipe should be returned in this format{format_instructions}.",
            input_variables = ["specifications"],
            partial_variables = {"format_instructions": output_parser.get_format_instructions()}
        )

        # Generate the system message prompt
        system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)
        
        # Define the user message.  This is the message that will be passed to the model to generate the recipe.
        human_template = "Create a delicious recipe based on the specifications {specifications} provided.  Please ensure the returned prep time, cook time, and total time are integers in minutes.  If any of the times are n/a\
                    as in a raw dish, return 0 for that time.  Round the times to the nearest 5 minutes to provide a cushion and make for a more readable recipe."
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)    
        
        # Create the chat prompt template
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        # format the messages to feed to the model
        messages = chat_prompt.format_prompt(specifications=specifications).to_messages()

        # Create a list of models to loop through in case one fails
        models = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]

        # Loop through the models and try to generate the recipe
        for model in models:
            try:
                # Create the chat object
                chat = ChatOpenAI(model_name = model, temperature = 1, max_retries=3)

                # Generate the recipe
                recipe = chat(messages).content

                # Parse the recipe
                parsed_recipe = output_parser.parse(recipe)

                # Save the recipe history to redis
                self.save_recipe(parsed_recipe.name, parsed_recipe)

                return parsed_recipe

            except (requests.exceptions.RequestException, openai.error.APIError):
                continue