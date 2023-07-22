""" Create a model for the Pairing class """
from pydantic. import BaseModel, Field


# Create a Pairing class that inherits from the BaseModel class
class Pairing(BaseModel):
    """ Define the Pairing model."""
    pairing_text: str = Field(description="The text of the generated pairing")
    pairing_reason: str = Field(description="The reason why the pairing is appropriate for the recipe")
    
    # @TODO create a way to return mutliple pairings
