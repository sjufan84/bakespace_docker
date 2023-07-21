""" This module defines the ChatService class, which is responsible for managing the chatbot. """
import json
from typing import Union
import requests
import openai
from ..middleware.session_middleware import RedisStore
from ..dependencies import get_openai_api_key, get_openai_org


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
        self.store = store or RedisStore()
        self.session_id = self.store.session_id
        chat_history = self.store.redis.get(f'{self.session_id}:chat_history')
        if chat_history:
            self.chat_history = chat_history
        else:
            self.chat_history = []

    def load_chat_history(self):
        """ Load the chat history from Redis. """
        try:
            chat_history_json = self.store.redis.get(f'{self.session_id}:chat_history')
            if chat_history_json:
                chat_history_dict = json.loads(chat_history_json)
                return list(chat_history_dict)
            return []
        except Exception as e:
            print(f"Failed to load chat history from Redis: {e}")
            return []
        
    def save_chat_history(self):
        """ Save the chat history to Redis. """
        try:
            # Save the chat history to redis
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
        # Format the message and append it to the chat history  
        chef_message = ChatMessage(message, "ai").format_message()
        self.chat_history.append(chef_message)
        # Save the chat history to redis
        return self.save_chat_history()
    
    # Define a function to initialize the chatbot with context and an optional recipe
    def initialize_general_chat(self, context: Union[str, None] = None) -> dict:    
        """ Initialize the chatbot with an optional context for general chat. """
        initial_message = {
                                "role": "system", 
                                "content": f"""
                                You are a master chef answering a user's questions about cooking.  The context, if any,\
                                is {context}  Your chat history so far is {self.chat_history[1:]}
                                """
                                }
        # Append the initial message to the chat history
        self.chat_history = [initial_message]

        # Save the chat history to redis
        self.save_chat_history()

        # Return the initial message
        return initial_message

    def initialize_recipe_chat(self, recipe_text: str) -> dict:
        """ Initialize the chatbot with a recipe. """
        initial_message = {
                                "role": "system", 
                                "content": f"""
                               You are a master chef who has generated a recipe {recipe_text} that the user\
                                would like to ask questions about.  Your chat history so far is {self.chat_history[1:]} 
                                """
                                }
        # Append the initial message to the chat history
        self.chat_history = [initial_message]

        # Save the chat history to redis
        self.save_chat_history()

        # Return the initial message
        return initial_message


    # Define a function to get a response from the chatbot
    def get_chef_response(self, question: str):
        """ Get a response from the chatbot. """
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        messages = self.load_chat_history()

        self.chat_history = [message for message in self.chat_history]

        # Format the message and add it to the chat history
        user_message = ChatMessage(question, "user").format_message()

        # Append the user message to the chat history
        self.chat_history.append(user_message)
        

        # Use the OpenAI API to generate a recipe
        try:
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=750,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            temperature=1,
            top_p=0.9,
            n=1,
        )
            chef_response = response.choices[0].message.content
            
            # Convert the chef_response to a message and append it to the chat history
            chef_response = ChatMessage(chef_response, "system").format_message()
            self.chat_history.append(chef_response)

            # Save the chat history to redis
            return self.save_chat_history()


        except (requests.exceptions.RequestException, openai.error.APIError):
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            max_tokens=750,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            temperature=1,
            top_p=0.9,
            n=1,
        )
          
            # Convert the chef_response to a message and append it to the chat history
            chef_response = ChatMessage(chef_response, "system").format_message()
            self.chat_history.append(chef_response)

            # Save the chat history to redis
            self.save_chat_history()

            # Return the chef response
            return chef_response

    

    def clear_chat_history(self):
        """ Clear the chat history. """
        self.chat_history = []
        self.save_chat_history()
