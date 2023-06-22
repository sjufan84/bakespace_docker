from pydantic import BaseModel
from pydantic.fields import Field

# Create a model for the Image class
class Image(BaseModel):
    url: str = Field(description="The url of the generated image")
    name: str = Field(description="The name of the generated image")