# services/chat_service.py

import requests
from .chat_history_service import ChatMessageHistory
from langchain.schema import messages_to_dict
from ..dependencies import get_openai_api_key, get_openai_org
import openai
#

# Define a class to handle the chatbot using OpenAI and langchain
class ChatService:
    def __init__(self):
        # Initialize the chat history
        self.chat_history = ChatMessageHistory()
        self.openai_api_key = get_openai_api_key()
        self.openai_org = get_openai_org()
        self.recipe = None

    # Define a function to add a recipe to the chatbot.  We can also implement this for other states as well if we want
    # to provide the chatbot with more context on the front end.
    def add_recipe_to_chat(self, recipe: str):
        self.chat_history.add_user_message(f'Here is the recipe {recipe} for reference.')
        self.recipe = recipe

    # This is a function to initialize the chatbot with an initial message -- typically a system message
    # that explains the context of the chatbot i.e. "You are a master chef answering a user's culinary questions."
    # This is potentially a good place to initiate the chat with different states as well.
    def initialize_chat(self, initial_message: str):
        self.chat_history.add_ai_message(initial_message)

    # This saves the chat_history to a dictionary to be able to pass it to the front end
    # or to save it to a database.  Note: if we decide to implement context based chatting
    # where there is the possibility for the user to have multiple conversations with the chatbot,
    # we will need to clear the chat history after each conversation.  
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

        # Checks to see if the chatbot has been initialized with a recipe.  If not, it will initialize the chatbot 
        # with a system message that explains the context of the chatbot i.e. "You are a master chef answering a user's culinary questions."
        # and pass any chat history that has been generated so far for the chatbot to use as context.
        if self.recipe is None:
            messages = [
                {
                "role": "system",
                "content": f"You are a master chef answering a user's culinary questions. Your chat history\
                            so far is {self.chat_history.messages}.  Please respond as a friendly chef who is happy to answer the user's questions thoroughly."
                },
            ]
        # If the chatbot has been initialized with a recipe (could be other values in the future), it will initialize the chatbot with the recipe
        else:
            messages = [
            {
                
                "role": "system",
                "content": f"You are a master chef who has provided a recipe {self.recipe} for the user about which they would like to ask some follow up questions.  Your chat history\
                            so far is {self.chat_history.messages}.  Please respond as a friendly chef who is happy to answer the user's questions thoroughly."
                        
            },
        ]
        # Flexible way to add a user message to the chatbot that carries the context of the chatbot
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


