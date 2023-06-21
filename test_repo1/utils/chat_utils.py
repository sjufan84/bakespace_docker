# Importing the necessary libraries
import streamlit as st
import openai
import os
from langchain.memory import ChatMessageHistory
from langchain.schema import messages_to_dict
import requests
from dotenv import load_dotenv
load_dotenv()

history = ChatMessageHistory()

# Get the OpenAI API key and org key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")



# Define a function to initialize the chatbot
# This function will be re-used throughout the app
# And take in the initial message as a parameter as well
# as a chat type (e.g. "recipe" or "foodpedia", etc.
# to distinguish between different chatbots and how they are stored in memory
# Set it to the initial message in the chat history
def initialize_chat(initial_message : str):
    # Initialize the chatbot with the first message
    history.add_ai_message(initial_message)

# We need to define a function to save the chat history as a dictionary
# This will be used to save the chat history to the database and to display the chat history
def save_chat_history_dict():
    # Save the chat history as a dictionary
    chat_history_dict = messages_to_dict(st.session_state.history.messages)
    st.session_statechat_history_dict = chat_history_dict
    return chat_history_dict


# Now we need to define a function to add messages to the chatbot
# This will take in the message_type (e.g. "user" or "ai")
# and the message itself
# It will then add the message to the chat history
# and return the updated chat history
def add_message_to_chat(message : str, role : str):
    # Add the appropriate message to the chat history depending on the role
    if role == "user":
        st.session_state.history.add_user_message(message)
    elif role == "ai":
        st.session_state.history.add_ai_message(message)
    
    return st.session_state.history



# Define a function to update the chat summary    
#async def update_chat_summary():
#    messages = st.session_state.memory.chat_memory.messages
#    previous_summary = st.session_state.chat_summary
#    st.session_state.chat_summary = st.session_state.memory.predict_new_summary(messages, previous_summary)
#    return st.session_state.chat_summary
    




# Define the function to answer any follow up questions the user has about the recipe
def get_chef_response(question: str):

    
    messages = [
    {
        
        "role": "system",
        "content": f"You are a master chef who has provided a recipe {st.session_state.recipe} for the user about which they would like to ask some follow up questions.  Your chat history\
                    so far is {st.session_state.history.messages}.  Please respond as a friendly chef who is happy to answer the user's questions thoroughly."
                
    },
    {
        "role": "user",
        "content": f"I need to ask you a follow up question {question}."
    },
   
    ]

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
        st.session_state.response = response
    
    except (requests.exceptions.RequestException, openai.error.APIError):
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=messages,
        max_tokens=1250,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        temperature=1,
        top_p=0.9,
        n=1,
    )
        chef_response = response.choices[0].message.content
        st.session_state.response = response
        
        
    

    return chef_response

