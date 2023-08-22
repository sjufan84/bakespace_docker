""" Define the Recipe model.  The schema mirrors the Bakespace data model."""
from typing import Optional, List, Union
from pydantic import BaseModel, Field

# The core model for the recipe.  This will also be 
# used by the parser to parse the output from the model
class Recipe(BaseModel):
    """ Define the Recipe model. """
    name: str = Field(description = "The name of the recipe.")
    desc: Optional[str] = Field(description =
    "A short description of the recipe.")
    ingredients: Union[str, List[str]] = Field(description =
    "The ingredients for the recipe.")
    directions: Union[str, List[str]] = Field(description =
     "The directions for preparing the recipe.")
    preptime: Optional[int] = Field(description = 
    "The time it takes to prepare the recipe.")
    cooktime: Optional[int] = Field(description = 
    "The time it takes to cook the recipe.")
    totaltime: Optional[int] = Field(description = 
    "The total time it takes to prepare and cook the recipe.")
    servings: Optional[int] = Field(description = 
    "The number of servings the recipe makes.")
    calories: Optional[int] = Field(description = 
    "The number of calories in the recipe.")
    
    # Ingredients / instructions 
    @property
    def recipe_text(self):
        """ Return the recipe text. """
        return f"{self.name} {self.desc} {self.preptime} {self.cooktime}\
    {self.totaltime} {self.servings} {self.directions} {self.ingredients} {self.calories}"
    
    class Config:
        """ Configure the Recipe model.  Returns a Recipe object as a dictionary. """
        schema_extra = {
            "examples": [
                {
                    "name": "Chocolate Chip Cookies",
                    "desc": "A delicious chocolate chip cookie recipe.",
                    "ingredients": """
                        "1 cup flour",
                        "1 cup sugar",
                        "1 cup chocolate chips"
                    """,
                    "directions": """
                        "Preheat oven to 350 degrees.",
                        "Mix ingredients together.",
                        "Bake for 15 minutes."
                    """,
                    "preptime": 10,
                    "cooktime": 15,
                    "totaltime": 25,
                    "servings": 12,
                    "calories": 250
                }
            ]
        }

