# services/chat_service.py

import requests
from .chat_history import ChatMessageHistory
from langchain.schema import messages_to_dict
from ..dependencies import get_openai_api_key, get_openai_org
import openai
#

# Define a class to handle the chatbot using OpenAI and langchain
class ChatService:
    def __init__(self):
        self.chat_history = ChatMessageHistory()
        self.openai_api_key = get_openai_api_key()
        self.openai_org = get_openai_org()
        self.recipe = None

    def add_recipe_to_chat(self, recipe: str):
        self.chat_history.add_user_message(f'Here is the recipe {recipe} for reference.')
        self.recipe = recipe

    def initialize_chat(self, initial_message: str):
        self.chat_history.add_ai_message(initial_message)

    def save_chat_history_dict(self):
        return messages_to_dict(self.chat_history.messages)

    # Define a function to add messages to the chatbot
    def add_message_to_chat(self, message: str, role: str):
        if role == "user":
            self.chat_history.add_user_message(message)
        elif role == "ai":
            self.chat_history.add_ai_message(message)

        return self.chat_history

    # Define a function to get a response from the chatbot
    def get_chef_response(self, question: str):
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        if self.recipe is None:
            messages = [
                {
                "role": "system",
                "content": f"You are a master chef answering a user's culinary questions. Your chat history\
                            so far is {self.chat_history.messages}.  Please respond as a friendly chef who is happy to answer the user's questions thoroughly."
                },
            ]
        else:
            messages = [
            {
                
                "role": "system",
                "content": f"You are a master chef who has provided a recipe {self.recipe} for the user about which they would like to ask some follow up questions.  Your chat history\
                            so far is {self.chat_history.messages}.  Please respond as a friendly chef who is happy to answer the user's questions thoroughly."
                        
            },
        ]
            
        messages.append(
        {
            "role": "user",
            "content": f"I need to ask you a follow up question {question}."
        },
        )

        # Use the OpenAI API to generate a recipe
        try:
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1250,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            temperature=1,
            top_p=0.9,
            n=1,
        )
            chef_response = response.choices[0].message.content
        
        except (requests.exceptions.RequestException, openai.error.APIError):
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            max_tokens=1250,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            temperature=1,
            top_p=0.9,
            n=1,
        )
            chef_response = response.choices[0].message.content
            
            
        return chef_response


