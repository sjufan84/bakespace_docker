from pydantic import BaseModel
from pydantic.fields import Field
from enum import Enum

# Create a model for the role class which is an Enum with the values "ai" or "user"
class Role(str, Enum):
    ai = "ai"
    user = "user"

# Create a model for the message class
class Message(BaseModel):
    content: str = Field(description="The content of the message")
    role: Role = Field(description="The role of the message. One of 'ai' or 'user'")

class ChatSession(BaseModel):
    context: str = Field(description="The context of the chat session")
    messages: list[Message] = Field(description="The messages of the chat session")

   
