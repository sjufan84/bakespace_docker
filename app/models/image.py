""" This module contains the Image class """
from typing import Optional
from pydantic import BaseModel, Field

# Create a model for the Image class
class Image(BaseModel):
    """ A class to represent an image """
    url: str = Field(description="The url of the generated image")
    thread_id: Optional[str] = Field(description="The thread id that the image is\
    associated with")
    recipe_id: Optional[str] = Field(description="The recipe id that the image is\
    associated with")