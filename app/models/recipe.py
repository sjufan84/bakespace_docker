# Create a model for the Recipe class 
# These mimic the values from the BakeSpace API

from typing import List, Optional
from pydantic import BaseModel

# The core model for the recipe.  This will also be used by the parser to parse the output from the model
class Recipe(BaseModel):
    #recipeid: int -- this could be generated by the database
    name: str
    #author: str
    #foodimg: str -- @TODO populate the foodimg field from the image generated by the image service
    #fullimg: str
    desc: Optional[str]
    preptime: int
    cooktime: int
    totaltime: int
    servings: int
    directions: List[str]
    ingredients: List[str]
    calories: Optional[int]
    recipe_text: str
    # created_on: date.today()
    