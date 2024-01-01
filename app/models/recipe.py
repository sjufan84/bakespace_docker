""" Define the Recipe model.  The schema mirrors the Bakespace data model."""
from typing import List, Optional
from pydantic import BaseModel, Field

# The core model for the recipe.  This will also be
# used by the parser to parse the output from the model
class Recipe(BaseModel):
    """ Define the Recipe model. """
    # recipeid: int -- this could be generated by the database
    name: str = Field(description = "The name of the recipe.")
    desc: Optional[str] = Field(description = "A short description of the recipe.")
    preptime: int = Field(description = "The time it takes to prepare the recipe.")
    cooktime: Optional[int] = Field(description = "The time it takes to cook the recipe.")
    totaltime: int = Field(description = "The total time it takes to prepare and cook the recipe.")
    servings: int = Field(description =
                          "The number of servings or approximate number of servings of the recipe.")
    directions: List[str] = Field(description = "The directions for preparing the recipe.")
    ingredients: List[str] = Field(description = "The ingredients for the recipe.")
    calories: Optional[int] = Field(description =
                                    "The estimated calories for one serving of the recipe.  Does not\
    have to be exact.")

    @property
    def recipe_text(self):
        """ Return the recipe text. """
        return f"{self.name} {self.desc} {self.preptime} {self.cooktime}\
        {self.totaltime} {self.servings} {self.directions} {self.ingredients} {self.calories}"

    class Config:
        """ Configure the Recipe model.  Returns a Recipe object as a dictionary. """
        json_schema_extra = {
            "examples": [
                {
                    "name": "Chocolate Chip Cookies",
                    "desc": "A delicious chocolate chip cookie recipe.",
                    "ingredients": [
                        "1 cup flour",
                        "1 cup sugar",
                        "1 cup chocolate chips"
                    ],
                    "directions": [
                        "Preheat oven to 350 degrees.",
                        "Mix ingredients together.",
                        "Bake for 15 minutes."
                    ],
                    "preptime": 10,
                    "cooktime": 15,
                    "totaltime": 25,
                    "servings": 12,
                    "calories": 250
                }
            ]
        }

class FormattedRecipe(BaseModel):
    """ A recipe object for the Anthropic API. """
    recipe_name: str = Field(..., description="The name of the recipe.")
    ingredients: List[str] = Field(..., description="The ingredients of the recipe.")
    directions: List[str] = Field(..., description="The directions for the recipe.")
    prep_time: int = Field(..., description="The preparation time for the recipe.")
    cook_time: Optional[int] = Field(..., description="The cooking time for the recipe.\
      This could be null if the recipe is raw or doesn't require cooking.")
    serving_size: Optional[str] = Field(..., description="The serving size of the recipe.")
    calories: Optional[int] = Field(..., description="The estimated calories for one\
      serving of the dish.")