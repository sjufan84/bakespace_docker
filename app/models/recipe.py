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
    prep_time: Union[int, str] = Field(None, description="The preparation time for the recipe.")
    cook_time: Optional[Union[str, int]] = Field(None, description="The cooking time for the recipe.\
      This could be null if the recipe is raw or doesn't require cooking.")
    serving_size: Union[str, int] = Field("4-6", description="The serving size of the recipe.")
    calories: Optional[Union[str, int]] = Field(None, description="The estimated calories for one\
      serving of the dish.")
    fun_fact: str = Field("", description="A fun fact about the recipe.\
    Should be creative, interesting, and a conversation starter.  Could be a historical\
    fact about the ingredients or recipe, etc.")
    is_food: bool = Field(True, description="Whether or not the submitted text is related to food.")
    pairs_with: str = Field("", description="A pairing for the recipe.  It could be a wine pairing, side\
    dish, etc.  Whatever seems the most appropriate for the recipe.")

class FormattedRecipe(BaseModel):
    """ A recipe object for the Anthropic API. """
    recipe_name: str = Field(..., description="The name of the recipe.")
    ingredients: List[str] = Field(..., description="The ingredients of the recipe.")
    directions: List[str] = Field(..., description="The directions for the recipe.")
    prep_time: Union[int, str] = Field(None, description="The preparation time for the recipe.")
    cook_time: Union[str, int] = Field(None, description="The cooking time for the recipe.\
      This could be null if the recipe is raw or doesn't require cooking.")
    serving_size: Union[str, int] = Field("", description="The serving size of the recipe.")
    calories: Optional[Union[str, int]] = Field(None, description="The estimated calories for one\
      serving of the dish.")
    is_food: bool = Field(True, description="Whether or not the submitted text is related to food.")
    pairs_with: str = Field("", description="A pairing for the recipe.\
    It could be a wine pairing, side dish, etc.  Whatever seems the most appropriate for the recipe.")
    fun_fact: str = Field("", description="A fun fact about the recipe or ingredients.  Should be\
    creative, interesting, and a conversation starter.  Could be a historical\
    fact about the ingredients or recipe, etc.")
    source: Optional[str] = Field(None, description="The source of the recipe i.e. AllRecipes,\
    Bakespace, etc. if applicable.")

class FormattedRecipeResponse(BaseModel):
    """ Define the response model for the upload files endpoint. """
    formatted_recipe: FormattedRecipe = Field(..., description="The formatted recipe.")
    session_id: Union[str, None] = Field(..., description="The session_id.")
    thread_id: Optional[str] = Field(None, description="The thread_id.")

class FormatRecipeTextRequest(BaseModel):
    """ Define the request model for the format recipe text endpoint. """
    recipe_text: str = Field(..., description="The raw recipe text.")
    thread_id: Optional[str] = Field(None, description="The thread_id.")

class CreateRecipeRequest(BaseModel):
    """ Request body for creating a new recipe """
    specifications: str = Field(..., description="The specifications for the recipe.")
    serving_size: Optional[str] = Field("4-6", description="The serving size for the recipe.")
    chef_type: Optional[str] = Field("home_cook", description="The type of chef creating the recipe.")
    thread_id: Optional[str] = Field(None, description="The thread id for the chat session.")

class CreateRecipeResponse(BaseModel):
    recipe: Recipe = Field(..., description="The recipe object.")
    session_id: Union[str, None] = Field(..., description="The session id for the chat session.")
    thread_id: Union[str, None] = Field(None, description="The thread id for the chat session.")
