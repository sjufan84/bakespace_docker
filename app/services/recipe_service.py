""" This module contains the recipe service class. """
import logging
from typing import Optional
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

class RecipeService:
    """ A class to represent the recipe service. """
    def __init__(self, store: RedisStore = None, chef_choice: str = None):
        self.store = store
        self.session_id = self.store.session_id
        self.recipe = self.load_recipe()
        if not self.recipe:
            self.recipe = None
        self.chef_choice = chef_choice
        if not self.chef_choice:
            self.chef_choice = "general"
    

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
        except LookupError as e:
            print(f"Failed to delete recipe from Redis: {e}")
        return {"message": "Recipe deleted."}
    


    def execute_generate_recipe(self, specifications: str, chef_type: Optional[str] = None):
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

            # Check if the user has specified a chef type
            if chef_type:
                self.chef_choice = chef_type
            
            # Get the chef model and prompt
            logging.debug("Getting chef model and prompt.")
            chef_model = chef_data[self.chef_choice]["chef_model"]
            chef_prompt = chef_data[self.chef_choice]["prompt"]

            # Define the first system message.  This let's the model know what type of output\
            # we are expecting and in what format it needs to be in.
            logging.debug("Creating system message prompt.")
            prompt = PromptTemplate(
                template = "{chef_prompt}. You are creating a recipe based on a\
                user's specifications {specifications}. The recipe should be\
                returned in this format{format_instructions}.",
                input_variables = ["specifications", "chef_prompt"],
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
            messages = chat_prompt.format_prompt(specifications=specifications,
                                                chef_prompt=chef_prompt).to_messages()

            # Create a list of models to loop through in case one fails
            models = [chef_model, *core_models]

            # Loop through the models and try to generate the recipe
            for model in models:
                try:
                    logging.debug(f"Trying model: {model}.")
                    
                    # Create the chat object
                    chat = ChatOpenAI(model_name = model, temperature = 1, max_retries=3, timeout=15)

                    # Generate the recipe
                    chef_response = chat(messages).content

                    # Parse the recipe
                    parsed_recipe = output_parser.parse(chef_response)

                    # Get a personalized response from the chef
                    new_chef_response = self.get_personalized_recipe_response(recipe=chef_response,
                                        question=specifications)

                    # Convert the recipe to a dictionary for saving to redis
                    redis_dict = {str(key): str(value) for key, value in dict(parsed_recipe).items()}

                    # Save the recipe history to redis
                    self.save_recipe(redis_dict)

                    return {"recipe": parsed_recipe, "chef_response": new_chef_response, "session_id": self.session_id}

                except (
                    requests.exceptions.RequestException,
                    requests.exceptions.ConnectTimeout, openai.error.APIError) as e:
                    logging.error(f"Error with model: {model}. Error: {str(e)}"
                    )
                    continue
            

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return None
        
    def get_personalized_recipe_response(self, recipe, question):
        """ Getting a more personalized response from the chef. """
        # Load the chef model and prompt based on the chef choice
        chef_type = self.chef_choice
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
