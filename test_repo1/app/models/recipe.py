# Create a model for the Recipe class 
# These mimic the values from the BakeSpace API
# We will need to rework the models to parse the output
# That will match these values

from datetime import date
from typing import List
from pydantic import BaseModel


class Recipe(BaseModel):
    #recipeid: int
    name: str
    #author: str
    #foodimg: str
    #fullimg: str
    desc: str
    preptime: int
    cooktime: int
    servings: int
    directions: List[str]
    ingredients: List[str]
    calories: int
    #created_on: date.today()
    