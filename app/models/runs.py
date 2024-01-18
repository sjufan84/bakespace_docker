""" Run objects for the app """
import os
import sys
from typing import Optional, Union, List
from pydantic import BaseModel, Field
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd()))))
from app.models.recipe import Recipe

class CreateThreadRequest(BaseModel):
    """ Create Thread Request Model """
    message_content: str = Field(..., description="The content of the message to be added to the thread.")
    message_metadata: Optional[object] = Field({}, description="The metadata for the message.  A mapping of\
      key-value pairs that can be used to store additional information about the message.")
    chef_type: Optional[str] = Field(..., description="The type of chef the user is.\
    Must be one of ['adventurous_chef', 'home_cook', 'pro_chef']")
    serving_size: Optional[str] = Field(None, description="The serving size for the recipe.")

class GetChefResponse(BaseModel):
  """ Get Chef Response Model """
  message_content: str = Field(..., description="The content of the message to be added to the thread.")
  message_metadata: Optional[object] = Field({}, description="The metadata for the message.  A mapping of\
    key-value pairs that can be used to store additional information about the message.")
  chef_type: Optional[str] = Field(
      "home_cook", description="The type of chef that the user wants to talk to.")
  serving_size: Optional[str] = Field(None, description="The serving size for the recipe.")
  thread_id: str = Field(None, description="The thread id for the run to be added to.")
  save_recipe: Optional[bool] = Field(False, description="Whether or not to use the 'save_recipe' tool.")

class ClearChatResponse(BaseModel):
  """ Return class for the clear_chat_history endpoint """
  message: str = Field("Chat history cleared", description="The message returned from the endpoint.")
  session_id: Union[str, None] = Field(..., description="The session id for the chat session.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  thread_id: Union[str, None] = Field(None, description="The thread id for the chat session.")

class ViewChatResponse(BaseModel):
  """ Return class for the view_chat_history endpoint """
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  session_id: str = Field(..., description="The session id for the chat session.")
  thread_id: Union[str, None] = Field(None, description="The current thread id for the chat session.")

class InitializeChatResponse(BaseModel):
  """ Return class for the initialize_chat endpoint """
  thread_id: str = Field(..., description="The thread id for the run to be added to.")
  message_content: str = Field(..., description="The message content.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  session_id: Union[str, None] = Field(..., description="The session id for the chat session.")

class GetChefRequestResponse(BaseModel):
  """ Return class for the get_chef_response endpoint """
  chef_response: str = Field(..., description="The response from the chef.")
  thread_id: str = Field(..., description="The thread id for the chat session.")
  session_id: Union[str, None] = Field(..., description="The session id for the chat session.")
  chat_history: List[dict] = Field(..., description="The chat history for the chat session.")
  adjusted_recipe: Optional[Recipe] = Field(None, description="The adjusted recipe object.")
