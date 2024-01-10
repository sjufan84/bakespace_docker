""" Define the Recipe model.  The schema mirrors the Bakespace data model."""
from typing import List, Optional, Union
from pydantic import BaseModel, Field

# The core model for the recipe.  This will also be
# used by the parser to parse the output from the model
class Recipe(BaseModel):
    """ Define the Recipe model. """
    recipe_name: str = Field(..., description="The name of the recipe.")
    ingredients: List[str] = Field(..., description="The ingredients of the recipe.")
    directions: List[str] = Field(..., description="The directions for the recipe.")
    prep_time: Optional[Union[int, str]] = Field(..., description="The preparation time for the recipe.")
    cook_time: Optional[Union[str, int]] = Field(..., description="The cooking time for the recipe.\
      This could be null if the recipe is raw or doesn't require cooking.")
    serving_size: Optional[Union[str, int]] = Field(..., description="The serving size of the recipe.")
    calories: Optional[Union[str, int]] = Field(..., description="The estimated calories for one\
      serving of the dish.")
    fun_fact: Optional[str] = Field(None, description="A fun fact about the recipe.")


class FormattedRecipe(BaseModel):
    """ A recipe object for the Anthropic API. """
    recipe_name: str = Field(..., description="The name of the recipe.")
    ingredients: List[str] = Field(..., description="The ingredients of the recipe.")
    directions: List[str] = Field(..., description="The directions for the recipe.")
    prep_time: Optional[Union[int, str]] = Field(..., description="The preparation time for the recipe.")
    cook_time: Optional[Union[str, int]] = Field(..., description="The cooking time for the recipe.\
      This could be null if the recipe is raw or doesn't require cooking.")
    serving_size: Optional[Union[str, int]] = Field(..., description="The serving size of the recipe.")
    calories: Optional[Union[str, int]] = Field(..., description="The estimated calories for one\
      serving of the dish.")
