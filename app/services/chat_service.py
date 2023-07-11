import requests
from ..middleware.session_middleware import RedisStore  
import json
# from urllib.parse import urlparse
from ..dependencies import get_openai_api_key, get_openai_org
from typing import Optional
import openai
import uuid

class ChatMessage:
    def __init__(self, content, role):
        self.content = content
        self.role = role
    
    def format_message(self):
        # Return a dictionary with the format {"role": role, "content": content}
        return {"role": self.role, "content": self.content}
    

class ChatService:
    def __init__(self, session_id: str = None, store: RedisStore = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.store = store or RedisStore()
        chat_history = self.store.redis.get(f'{self.session_id}:chat_history')
        if chat_history:
            self.chat_history = chat_history
        else:
            self.chat_history = []

    def load_chat_history(self):
        try:
            chat_history_json = self.store.redis.get(f'{self.session_id}:chat_history')
            if chat_history_json:
                chat_history_dict = json.loads(chat_history_json)
                return [message for message in chat_history_dict]
            else:
                return []
        except Exception as e:
            print(f"Failed to load chat history from Redis: {e}")
            return []

    def save_chat_history(self):
        try:
            # Save the chat history to redis
            chat_history_json = json.dumps(self.chat_history)
            self.store.set(f'{self.session_id}:chat_history', chat_history_json)
        except Exception as e:
            print(f"Failed to save chat history to Redis: {e}")
        return self.chat_history
  
    def add_user_message(self, message: str):
        # Format the message and append it to the chat history
        user_message = ChatMessage(message, "user").format_message()
        self.chat_history.append(user_message)
        # Save the chat history to redis
        return self.save_chat_history()

    def add_chef_message(self, message: str):\
        # Format the message and append it to the chat history  
        chef_message = ChatMessage(message, "ai").format_message()
        self.chat_history.append(chef_message)
        # Save the chat history to redis
        return self.save_chat_history()

    # Define a function to initialize the chatbot with context and an optional recipe
    def initialize_chat(self, context: str, recipe_text: Optional[str] = None):    
         # Check to see if the context is "recipe" -- if it is, we need to retrieve the
        # recipe from the session state and use that to generate the initial message
        if context == "recipe":
            initial_message = {
                                    "role": "system", 
                                    "content": f"""
                                   You are a master chef who has generated a recipe {recipe_text} that the user\
                                    would like to ask questions about.  Your chat history so far is {self.chat_history[1:]} 
                                    """
                                    }
        # If the context is not recipe, then we need to adapt to the general chat context
        elif context != "recipe":
            initial_message = {
                                    "role": "system", 
                                    "content": f"""
                                   You are a master chef answering a user's questions about cooking.  Your chat history so far is {self.chat_history[1:]}
                                    """
                                    }
            # Append the initial message to the chat history
            self.chat_history = [initial_message]

            # Save the chat history to redis
            return self.save_chat_history()


    # Define a function to get a response from the chatbot
    def get_chef_response(self, question: str):
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        messages = self.load_chat_history()

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
            return self.save_chat_history()

    

    # Define a function to clear the chat history
    def clear_chat_history(self):
        self.chat_history = []
        self.save_chat_history()
