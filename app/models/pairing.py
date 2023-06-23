# Create a model for the Pairing class
from pydantic import BaseModel, Field


# Create a Pairing class that inherits from the BaseModel class
class Pairing(BaseModel):
    pairing_text: str = Field(description="The text of the generated pairing")
    #pairing_recipe: Optional[str] = Field(description="The recipe for the pairing if it is a cocktail pairing or a different type that requires a recipe")
    pairing_reason: str = Field(description="The reason why the pairing is appropriate for the recipe")
    
    # @TODO create a way to return mutliple pairings
