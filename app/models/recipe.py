""" Define the Recipe model.  The schema mirrors the Bakespace data model."""
from typing import List, Optional
from pydantic import BaseModel, Field

# The core model for the recipe.  This will also be
# used by the parser to parse the output from the model
class Recipe(BaseModel):
    """ Define the Recipe model. """
    #recipeid: int -- this could be generated by the database
    name: str = Field(description = "The name of the recipe.")
    desc: Optional[str] = Field(description = "A short description of the recipe.")
    preptime: int = Field(description = "The time it takes to prepare the recipe.")
    cooktime: int = Field(description = "The time it takes to cook the recipe.")
    totaltime: int = Field(description = "The total time it takes to prepare and cook the recipe.")
    servings: int = Field(description = "The number of servings the recipe makes.")
    directions: List[str] = Field(description = "The directions for preparing the recipe.")
    ingredients: List[str] = Field(description = "The ingredients for the recipe.")
    calories: Optional[int] = Field(description = "The number of calories in the recipe.")

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
                    "preptime": 10,
                    "cooktime": 15,
                    "totaltime": 25,
                    "servings": 12,
                    "directions": [
                        "Preheat oven to 350 degrees.",
                        "Mix ingredients together.",
                        "Bake for 15 minutes."
                    ],
                    "ingredients": [
                        "1 cup flour",
                        "1 cup sugar",
                        "1 cup chocolate chips"
                    ],
                    "calories": 250
                }
            ]
        }

class FormattedRecipe(BaseModel):
    """ Define the Recipe model. """
    #recipeid: int -- this could be generated by the database
    name: str = Field(description = "The name of the recipe.")
    desc: Optional[str] = Field(description = "A short description of the recipe.")
    preptime: Optional[int] = Field(description = "The time it takes to prepare the recipe.")
    cooktime: Optional[int] = Field(description = "The time it takes to cook the recipe.")
    totaltime: Optional[int] = Field(description = "The total\
                            time it takes to prepare and cook the recipe.")
    servings: Optional[int] = Field(description = "The number of servings the recipe makes.")
    directions: List[str] = Field(description = "The directions for preparing the recipe.")
    ingredients: List[str] = Field(description = "The ingredients for the recipe.")
    calories: Optional[int] = Field(description = "The number of calories in the recipe.")

    @property
    def recipe_text(self):
        """ Return the recipe text. """
        # Concatenate the name, description, prep time, cook time,
        # total time, servings, directions, ingredients, and calories
        # If any of the values are None, don't include them
        recipe_text = f"{self.name} {self.desc} {self.preptime}\
        {self.cooktime} {self.totaltime} {self.servings} {self.directions}\
        {self.ingredients} {self.calories}"
        return recipe_text

    class Config:
        """ Configure the Recipe model.  Returns a Recipe object as a dictionary. """
        schema_extra = {
            "examples": [
                {
                    "name": "Chocolate Chip Cookies",
                    "desc": "A delicious chocolate chip cookie recipe.",
                    "preptime": 10,
                    "cooktime": 15,
                    "totaltime": 25,
                    "servings": 12,
                    "directions": [
                        "Preheat oven to 350 degrees.",
                        "Mix ingredients together.",
                        "Bake for 15 minutes."
                    ],
                    "ingredients": [
                        "1 cup flour",
                        "1 cup sugar",
                        "1 cup chocolate chips"
                    ],
                    "calories": 250
                }
            ]
        }
