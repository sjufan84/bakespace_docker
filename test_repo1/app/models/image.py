from pydantic import BaseModel
from pydantic.fields import Field

# Create a model for the Image class
class Image(BaseModel):
    url: str = Field(description="The url of the generated image")

# @TODO add fields for the image class to integrate with Bakespace API