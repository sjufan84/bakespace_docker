""" Create a model for the Pairing class """
from typing import Optional
from pydantic import BaseModel, Field


# Create a Pairing class that inherits from the BaseModel class
class Pairing(BaseModel):
    """ Define the Pairing model."""
    pairing_text: str = Field(description="The text of the generated pairing")
    pairing_reason: str = Field(description="The reason why the pairing is\
    appropriate for the recipe")
    # Attach a thread id to the pairing
    thread_id: Optional[str] = Field(description="The thread id that the pairing is\
    associated with")
