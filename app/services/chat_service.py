import requests
from langchain.memory import ChatMessageHistory
from langchain.schema import messages_to_dict
from ..dependencies import get_openai_api_key, get_openai_org
import openai
import streamlit as st
from typing import List

# Define a class to handle the chatbot using OpenAI and langchain
class ChatService:
    # Initialize the chatbot with the initial message depending on the context
    def __init__(self):
        # Initialize the chat history
        self.chat_history = ChatMessageHistory()
        # Initialize the chat history dictionary
        self.chat_history_dict = {}
        # Initialize the initial message
        self.initial_message = {}
    
    # Save the chat_history to a dictionary
    def save_chat_history_dict(self):
        self.chat_history_dict = messages_to_dict(self.chat_history.messages)
        return self.chat_history_dict
    
    def add_user_message(self, message: str):
        self.chat_history.add_user_message(message)
        return self.save_chat_history_dict()

    def add_chef_message(self, message: str):
        self.chat_history.add_ai_message(message)
        return self.save_chat_history_dict()

    # Define a function to initialize the chatbot with an initial message
    def initialize_chat(self, context: str):
        initial_message = {"role": "system", 
                                "content": f"You are a master chef answering questions from a user given the provided context {context}."}
        # Return the initial message
        self.initial_message = initial_message
        return initial_message
        

    # Define a function to get a response from the chatbot
    def get_chef_response(self, question: str, chat_messages: List[dict]):
        # Set your API key
        openai.api_key = get_openai_api_key()
        openai.organization = get_openai_org()

        # Define the messages to feed to the model -- we are passing in the conversation up to this point as context
                
        messages = [
            {
                "role": "system",
                "content": f"You are a master chef answering a user's culinary questions. Your chat history so far is {chat_messages}.\
                        Please respond as a friendly chef who is happy to answer the user's questions thoroughly."
            },
            {
                "role": "user",
                "content": f"{question}"
            },
        ]

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

            chef_response = response.choices[0].message.content
    
        return chef_response

    # Define a function to clear the chat history
    def clear_chat_history(self):
        self.chat_history.clear()
