from pydantic import BaseModel
from pydantic.fields import Field

# Create a model for the message class
class Message(BaseModel):
    content: str = Field(description="The content of the message")
    role: str = Field(description="The role of the message sender")

    # @TODO -- what other fields do we need for the message class?