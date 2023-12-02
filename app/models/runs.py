""" Run objects for the app """
import os
import sys
from typing import Optional
from pydantic import BaseModel, Field
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd()))))


class CreateMessageRunRequest(BaseModel):
    """ Create Run Request Model """
    thread_id: str = Field(..., description="The thread id for the run to be added to.")
    chef_type: str = Field("home_cook", description="The assistant choice for the run to be\
    added to. Must be one of ['adventurous_chef', 'home_cook', 'pro_chef']")
    message_content: str = Field(..., description="The content of the message to be added to the thread.")
    message_metadata: Optional[object] = Field({}, description="The metadata for the message.  A mapping of\
    key-value pairs that can be used to store additional information about the message.")
    #file_ids: Optional[List[str]] = []

class CreateThreadRunRequest(BaseModel):
    """ Create Thread Run Request Model """
    message_content: str = Field(..., description="The content of the message to be added to the thread.")
    message_metadata: Optional[dict] = Field({}, description="The metadata for the message.")  
    chef_type: str = Field(..., description="The type of chef the user is.\
    Must be one of ['adventurous_chef', 'home_cook', 'pro_chef']") 
    serving_size: Optional[str] = Field(None, description="The serving size for the recipe.")

class ListStepsRequest(BaseModel):
    """ List Steps Request Model """
    thread_id: str = Field(..., description="The thread id for the run to be added to.")
    run_id: str = Field(..., description="The run id for the run to be added to.")
    limit: int = Field(20, description="The number of steps to return.")
    order: str = Field("desc", description="The order to return the steps in. Must be one of ['asc', 'desc']")

class CreateThreadRequest(BaseModel):
    """ Create Thread Request Model """
    message_content: str = Field(..., description="The content of the message to be added to the thread.")
    message_metadata: Optional[object] = Field({}, description="The metadata for the message.  A mapping of\
      key-value pairs that can be used to store additional information about the message.")  
    chef_type: Optional[str] = Field(..., description="The type of chef the user is.\
    Must be one of ['adventurous_chef', 'home_cook', 'pro_chef']") 
    serving_size: Optional[str] = Field(None, description="The serving size for the recipe.")
    session_id: str = Field(..., description="The session id.")

class GetChefResponse(BaseModel):
  """ Get Chef Response Model """
  message_content: str = Field(..., description="The content of the message to be added to the thread.")
  message_metadata: Optional[object] = Field({}, description="The metadata for the message.  A mapping of\
    key-value pairs that can be used to store additional information about the message.")
  chef_type: Optional[str] = Field("home_cook", description="The type of chef that the user wants to talk to.")
  serving_size: Optional[str] = Field(None, description="The serving size for the recipe.")
  thread_id: str = Field(None, description="The thread id for the run to be added to.")
  session_id: str = Field(None, description="The session id.")