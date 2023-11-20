""" Run objects for the app """
import os
import sys
from typing import List, Optional
from pydantic import BaseModel, Field
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(os.getcwd()))))


class CreateMessageRunRequest(BaseModel):
    """ Create Run Request Model """
    thread_id: str = Field(..., description="The thread id for the run to be added to.")
    chef_type: str = Field("home_cook", description="The assistant choice for the run to be\
    added to. Must be one of ['adventurous_chef', 'home_cook', 'pro_chef']")
    message_content: str = Field(..., description="The content of the message to be added to the thread.")
    file_ids: Optional[List[str]] = []

class CreateThreadRunRequest(BaseModel):
    """ Create Thread Run Request Model """
    message_content: str = Field(..., description="The content of the message to be added to the thread.")  
    chef_type: str = Field(..., description="The type of chef the user is.\
    Must be one of ['adventurous_chef', 'home_cook', 'pro_chef']") 
    serving_size: Optional[str] = Field(None, description="The serving size for the recipe.")

class ListStepsRequest(BaseModel):
    """ List Steps Request Model """
    thread_id: str = Field(..., description="The thread id for the run to be added to.")
    run_id: str = Field(..., description="The run id for the run to be added to.")
    limit: int = Field(20, description="The number of steps to return.")
    order: str = Field("desc", description="The order to return the steps in. Must be one of ['asc', 'desc']")
