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

class ChatResponse(BaseModel):
    session_id: str = Field(description="The session id.")
    chat_history: list[Message] = Field(description="The chat history.")


class InitialMessage(BaseModel):
    """ Define the InitialMessage model. """
    initial_message: Message = Field(description="The initial message of the chat session")
    

    class Config:
        """ Example response schema """
        schema_extra = {
            "examples": [
                {
                    "role": "system",
                    "content": "You are a master chef answering a user's questions about cooking.  The context, if any,\
                        is None.  Your chat history so far is []",
                    "session_id": "The session id.",
                    "chat_history": [
                        {
                            "content": "The content of the message.",
                            "role": "system"
                        },
                        {
                            "content": "The content of the message.",
                            "role": "user"
                        },
                        {
                            "content": "The content of the message.",
                            "role": "ai"
                        }
                    ]
                },
                {
                   "role": "system",
                     "content": "You are a master chef who has generated a recipe that the user\
                        would like to ask questions about.  Your chat history so far is []"
                }
            ]
        }

class ChefResponse(BaseModel):
    """ Define the ChefResponse model. """
    chef_response: Message = Field(description="The chef's response.")

    class Config:
        """ Example response schema """
        schema_extra = {
            "examples": [
                {
                    "chef_response": {
                        "content": "The chef's response.",
                        "role": "ai"
                    },
                    "session_id": "The session id.",
                    "chat_history": [
                        {
                            "content": "The content of the message.",
                            "role": "system"
                        },
                        {
                            "content": "The content of the message.",
                            "role": "user"
                        },
                        {
                            "content": "The content of the message.",
                            "role": "ai"
                        }
                    ]
                }
            ]
        }

class ChatSession(BaseModel):
    """ Define the ChatSession model. """
    context: str = Field(description="The context of the chat session")
    messages: list[Message] = Field(description="The messages of the chat session")