""" This module defines the ChatService class, which is responsible for managing the chatbot. """
import json
from typing import Union, Optional
import logging
from redis.exceptions import RedisError
from app.dependencies import get_openai_client
from app.middleware.session_middleware import RedisStore
client = get_openai_client()
# Create a dictionary to house the chef data to populate the chef model

# Establish the core models that will be used by the chat service
core_models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k"]

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

class ChatMessage:
    """ A class to represent a chat message. """
    def __init__(self, content, role, thread_id: Optional[str] = None):
        self.content = content
        self.role = role
        self.thread_id = thread_id

    def format_message(self):
        """ Format the message for the chat history. """
        # Return a dictionary with the format {"role": role, "content": content,
        # "thread_id": thread_id}
        return {"role": self.role, "content": self.content, "thread_id": self.thread_id}

class ChatService:
    """ A class to represent the chatbot. """
    def __init__(self, store: RedisStore = None):
        self.store = store
        self.session_id = self.store.session_id
        self.chef_type = self.store.redis.get(f'{self.session_id}:chef_type')
        chat_history = self.store.redis.get(f'{self.session_id}:chat_history')
        if chat_history:
            self.chat_history = chat_history
        else:
            self.chat_history = []
        if self.chef_type:
            self.chef_type = self.chef_type
        else:
            self.chef_type = "home_cook"
            self.save_chef_type()
        self.thread_id = self.store.redis.get(f'{self.session_id}:thread_id')
        if self.thread_id:
            self.thread_id = self.thread_id
        else:
            self.thread_id = None

    def load_chat_history(self):
        """ Load the chat history from Redis. """
        try:
            # Load the chat history from redis.  If there is not chat history, return an empty list
            chat_history = self.store.redis.get(f'{self.session_id}:chat_history')
            if chat_history:
                return json.loads(chat_history)
            return []
        except RedisError as e:
            logger.log(logger.ERROR, "Failed to load chat history from Redis: %s", e)
            return []

    def save_chat_history(self):
        """ Save the chat history to Redis. """
        try:
            chat_history_json = json.dumps(self.chat_history)
            self.store.redis.set(f'{self.session_id}:chat_history', chat_history_json)
        except RedisError as e:
            logger.log(logger.ERROR, "Failed to save chat history to Redis: %s", e)
        return self.chat_history

    def save_chef_type(self):
        """ Save the chef type to Redis. """
        try:
            self.store.redis.set(f'{self.session_id}:chef_type', self.chef_type)
        except RedisError as e:
            logger.log(logger.ERROR, "Failed to save chef type to Redis: %s", e)
        return self.chef_type

    # Define a function to load the chef type from Redis
    def load_chef_type(self):
        """ Load the chef type from Redis. """
        try:
            chef_type = self.store.redis.get(f'{self.session_id}:chef_type')
            if chef_type:
                return chef_type
            return "home_cook"
        except RedisError as e:
            logger.log(logger.ERROR, "Failed to load chef type from Redis: %s", e)
            return "home_cook"

    def add_user_message(self, message: str, thread_id: Optional[str] = None):
        """ Add a message from the user to the chat history. """
        # Format the message and add it to the chat history
        user_message = ChatMessage(message, "user", thread_id).format_message()
        self.chat_history = self.load_chat_history()
        self.chat_history.append(user_message)
        # Save the chat history to redis
        return self.save_chat_history()

    # Define a function to add a message from the chef to the chat history
    def add_chef_message(self, message: str, thread_id: Optional[str] = None):
        """ Add a message from the chef to the chat history. """
        chef_message = ChatMessage(message, "ai", thread_id).format_message()
        self.chat_history.append(chef_message)
        # Save the chat history to redis
        return self.save_chat_history()

    # Define a function to set the thread_id
    def set_thread_id(self, thread_id: str):
        """ Set the thread_id. """
        try:
            self.store.redis.set(f'{self.session_id}:thread_id', thread_id)
        except RedisError as e:
            logger.log(logger.ERROR, "Failed to set thread_id in Redis: %s", e)
        return thread_id

    # Define a function to load the thread_id
    def get_thread_id(self):
        """ Get the thread_id. """
        try:
            thread_id = self.store.redis.get(f'{self.session_id}:thread_id')
            if thread_id:
                return thread_id
            return None
        except RedisError as e:
            logger.log(logger.ERROR, "Failed to load thread_id from Redis: %s", e)
            return None

    # @TODO Define a function to add a message to a thread

    # Define a function to initialize the chatbot with context and an optional recipe
    async def initialize_general_chat(self, context: Union[str, None] = None, chef_type: str = None) -> dict:
        """ Initialize the chatbot with an optional context for general chat. """
        # Set the chef type if it is passed in
        if chef_type:
            self.chef_type = chef_type
            self.save_chef_type()
        # Set the initial message
        initial_message = {
            "role": "system",
            "content": f"""
            The context, if any, is {context}  Your chat history so far is {self.chat_history}.
            Please remember that you are on a website called "Bakespace" that
            is a social and recipe platform that allows users to create, upload, and share recipes as
            well as create cookbooks for themselves and other users to enjoy.
            """
        }
        # Add the initial message to the chat history
        self.chat_history = [initial_message]

        # Save the chat history to redis
        self.save_chat_history()

        # Log the chat history
        logger.log(logger.INFO, "Chat history: %s", self.chat_history)

        # Return the initial message, session_id, and chat_history as a json object
        logger.log(logger.INFO, "Session id: %s", self.session_id)

        return {"chat_history": self.chat_history, "session_id": self.session_id}

    def clear_chat_history(self):
        """ Clear the chat history. """
        self.chat_history = []
        self.save_chat_history()
        # Reset the thread_id
        self.set_thread_id("")

        # Return the session_id, the chat_history, and "Chat history cleared" as a json object
        return {"session_id": self.session_id, "chat_history": self.load_chat_history(),
                "message": "Chat history cleared"}

    def view_chat_history(self):
        """ View the chat history. """
        # Return the chat_history and the session_id as a json object
        return {
            "chat_history": self.load_chat_history(), "session_id": self.session_id
        }

    def check_status(self):
        """ Return the session id and any user data from Redis. """
        return {"session_id": self.session_id, "chat_history": self.load_chat_history(),
                "chef_type": self.chef_type, "thread_id": self.thread_id}
