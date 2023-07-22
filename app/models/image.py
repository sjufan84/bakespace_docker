""" This module contains the Image class """
from pydantic import BaseModel, Field

# Create a model for the Image class
class Image(BaseModel):
    """ A class to represent an image """
    url: str = Field(description="The url of the generated image")

# @TODO add fields for the image class to integrate with Bakespace API