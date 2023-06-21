from pydantic import BaseModel

# Create a model for the Image class
class Image(BaseModel):
    url: str
    name: str