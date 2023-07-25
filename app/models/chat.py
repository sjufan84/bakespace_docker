"""
Basic chat models
"""
from enum import Enum
from pydantic import BaseModel, Field

# Create a model for the role class which is an Enum with the values "ai" or "user"
class Role(str, Enum):
    """ Define the Role model. """
    ai = "ai"
    user = "user"

# Create a model for the message class
class Message(BaseModel):
    """ Define the Message model. """
    content: str = Field(description="The content of the message")
    role: Role = Field(description="The role of the message. One of 'ai' or 'user'")

class InitialMessage(BaseModel):
    """ Define the InitialMessage model. """
    session_id : str = Field(description="The session id.")
    chat_history : dict = Field(description="The chat history.")
    initial_message: Message = Field(description="The initial message.")
    
class ChefResponse(BaseModel):
    """ Define the ChefResponse model. """
    session_id : str = Field(description="The session id.")
    chat_history : dict = Field(description="The chat history.")
    chef_response: Message = Field(description="The chef response.")

class ChatHistory(BaseModel):
    """ Define the ChatHistory model. """
    session_id : str = Field(description="The session id.")
    chat_history : dict = Field(description="The chat history.")
 