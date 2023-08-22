""" This module contains the recipe service class. """
import logging
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

logging.basicConfig(level=logging.DEBUG)

class RecipeService:
    """ A class to represent the recipe service. """
    def __init__(self, store: RedisStore = None):
        self.store = store
        self.session_id = self.store.session_id
        self.recipe = self.load_recipe()
        if not self.recipe:
            self.recipe = None

    # Create a function to be able to load a recipe from the store by the recipe_name
    def load_recipe(self):
        """ Load the session recipe from the store"""
        try:
            # Load the recipe hash from redis with all of the keys
            recipe_json = self.store.redis.hgetall(f'{self.session_id}_recipe')
            if recipe_json:
                return recipe_json
            else:
                return None
        except Exception as e:
            print(f"Failed to load recipe from Redis: {e}")
            return None
        
    # Create a function to save a recipe to the store by the recipe_name
    def save_recipe(self, recipe):
        """ Save a recipe to the store by session_id """
        try:
            # Save the recipe to redis
            self.store.redis.hmset(f'{self.session_id}_recipe', mapping = recipe)
        except Exception as e:
            print(f"Failed to save recipe to Redis: {e}")
        return recipe
    
    
    # Create a function to delete a recipe from the store by the recipe_name
    def delete_recipe(self):
        """ Delete a recipe from the store by the recipe_name """
        try:
            # Delete the recipe from redis
            self.store.redis.delete(f'{self.session_id}_recipe')
        except Exception as e:
            print(f"Failed to delete recipe from Redis: {e}")
        return {"message": "Recipe deleted."}
    


    def execute_generate_recipe(self, specifications: str):
        """ Generate a recipe based on the specifications provided """
        try:
            # Set your API key
            logging.debug("Setting API key and organization.")
            openai.api_key = get_openai_api_key()
            openai.organization = get_openai_org()

            # Create the output parser -- this takes in the output
            #  from the model and parses it into a Pydantic object that mirrors the schema
            logging.debug("Creating output parser.")
            output_parser = PydanticOutputParser(pydantic_object=Recipe)

            # Define the first system message.  This let's the model know what type of output\
            # we are expecting and in what format it needs to be in.
            logging.debug("Creating system message prompt.")
            prompt = PromptTemplate(
                template = "You are a master chef creating a based on a\
                user's specifications {specifications}. The recipe should be\
                returned in this format{format_instructions}.",
                input_variables = ["specifications"],
                partial_variables = {"format_instructions": 
                output_parser.get_format_instructions()}
            )
            system_message_prompt = SystemMessagePromptTemplate(prompt=prompt)
            
            # Define the user message.
            logging.debug("Creating user message prompt.")
            human_template = "Create a delicious recipe based on the specifications\
            {specifications} provided.  Please ensure the returned prep time,\
            cook time, and total time are integers in minutes.  If any of the times are n/a\
            as in a raw dish, return 0 for that time.  Round the times to the nearest\
            5 minutes to provide a cushion and make for a more readable recipe."
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)    
            
            # Create the chat prompt template
            logging.debug("Creating chat prompt.")
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                            human_message_prompt])

            # format the messages to feed to the model
            messages = chat_prompt.format_prompt(specifications=specifications).to_messages()

            # Create a list of models to loop through in case one fails
            models = [
                "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613",
                "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
                ]

            # Loop through the models and try to generate the recipe
            for model in models:
                try:
                    logging.debug(f"Trying model: {model}.")
                    
                    # Create the chat object
                    chat = ChatOpenAI(model_name = model, temperature = 1, max_retries=3, timeout=15)

                    # Generate the recipe
                    recipe = chat(messages).content

                    # Parse the recipe
                    parsed_recipe = output_parser.parse(recipe)

                    # Convert the recipe to a dictionary for saving to redis
                    redis_dict = {str(key): str(value) for key, value in dict(parsed_recipe).items()}

                    # Save the recipe history to redis
                    self.save_recipe(redis_dict)

                    return {"recipe": parsed_recipe, "session_id": self.session_id}

                except (
                    requests.exceptions.RequestException,
                    requests.exceptions.ConnectTimeout, openai.error.APIError) as e:
                    logging.error(f"Error with model: {model}. Error: {str(e)}"
                    )
                    continue
            

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return None
