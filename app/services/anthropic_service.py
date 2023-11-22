""" Service to access Anthropic's API
This will initially be used as a fallback for the OpenAI API.
"""
from typing import Optional, List
import os
import json
import regex as re
from dotenv import load_dotenv  
from pydantic import BaseModel, Field
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from app.models.pairing import Pairing

# Load the environment variables
load_dotenv()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))


# Create pydantic models for the Anthropic API
class ChatMessage(BaseModel):
    """ Anthropic chat message. """
    message: str = Field(..., description="The message from the chatbot.")
    role: str = Field(..., description="The role of the message.  One of either 'assistant' or 'user'.")  

class ChatHistory(BaseModel):
    """ Chat history object. """
    chat_history: List[ChatMessage] = Field(..., description="The chat history.")

class AnthropicRecipe(BaseModel):
    """ A recipe object for the Anthropic API. """
    recipe_name: str = Field(..., description="The name of the recipe.")
    ingredients: List[str] = Field(..., description="The ingredients of the recipe.")
    directions: List[str] = Field(..., description="The directions for the recipe.")
    prep_time: int = Field(..., description="The preparation time for the recipe.")
    cook_time: Optional[int] = Field(..., description="The cooking time for the recipe.\
      This could be null if the recipe is raw or doesn't require cooking.")
    serving_size: str = Field(..., description="The serving size of the recipe.")
    calories: Optional[int] = Field(..., description="The estimated calories for one\
      serving of the dish.")
    fun_fact: str = Field(..., description="A fun or interesting fact about the recipe.\
      This could be one of its ingredients, the region of the world it is from, etc.")

class PairingRequest(BaseModel):
    """ A request object for the Anthropic API. """
    recipe: AnthropicRecipe = Field(..., description="The recipe to generate a pairing for.")
    chef_type: str = Field("pro_chef", description="The type of chef to use for the Anthropic API.")
    chat_history: Optional[List[ChatMessage]] = Field(None, description="The chat history for the Anthropic API.")
    pairing_type: str = Field(..., description="The type of pairing to generate i.e. wine, beer, etc.")

class ChatRequest(BaseModel):
    """ A request object for the Anthropic API. """
    user_prompt: str = Field(..., description="The prompt for the Anthropic API.")
    chef_type: str = Field("pro_chef", description="The type of chef to use for the Anthropic API.")
    chat_history: Optional[List[ChatMessage]] = Field(None, description="The chat history for the Anthropic API.")  

class RecipeRequest(BaseModel):
    """ A request object for the Anthropic API. """
    specifications: str = Field(..., description="The specifications for the recipe.")
    serving_size: str = Field("4", description="The serving size for the recipe.")
    chef_type: str = Field("pro_chef", description="The type of chef to use for the Anthropic API.")
    chat_history: Optional[List[ChatMessage]] = Field(None, description="The chat history for the Anthropic API.")

class AdjustRecipeRequest(BaseModel):
    """ A request object for the Anthropic API. """
    recipe: AnthropicRecipe = Field(..., description="The recipe to adjust.")
    adjustments: str = Field(..., description="The adjustments to make to the recipe.")
    chef_type: str = Field("pro_chef", description="The type of chef to use for the Anthropic API.")
    chat_history: Optional[List[ChatMessage]] = Field(None, description="The chat history for the Anthropic API.")

prompts_dict = {
  "pro_chef" : {
    "initial_prompt" : """You are a master chef in the style of Gordon Ramsay, brash,
    demanding, and passionate acting as a user's personal sous chef to answer any
    questions they may have, create recipes, pairings, etc.  You are on a site called
    "BakeSpace" that is a social network for people to connect over recipes,
    personalized cookbooks, and conversation.  Please respond as a chef who has
    the personality and style of Gordon Ramsay, professional, intense, and high energy.
    You are like Gordon Ramsay, but you are not him.  Do not say Gordon Ramsay, Gordon,
    or Ramsay in your response.  Do not break character.
    It's okay to joke around with the user, but still answer their question and do not
    insult them or refuse to answer their question.""",
    "temperature" : 0.7,
    "max_tokens_to_sample" : 1000,
    "model" : "claude-2.1"
  }
}

def extract_json_from_response(response_text):
    # Use regular expressions to find the JSON data enclosed in triple backticks with "json" identifier
    pattern = r'```json(.*?)```'
    match = re.search(pattern, response_text, re.DOTALL)
    
    if match:
        json_text = match.group(1)
        
        try:
            # Parse the JSON data
            extracted_json = json.loads(json_text)
            return extracted_json
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("No JSON data found in the response.")
        return None

def format_prompt(system_prompt: str, user_prompt: str, chat_history: List[ChatMessage] = None):
  """ Format the prompt for the Anthropic API. """
  prompt = f"{system_prompt}.  Your chat history so far is {chat_history}. {HUMAN_PROMPT} {user_prompt} {AI_PROMPT}"
  
  return prompt

# Define the basic chat function
def chat(request: ChatRequest):
  """ Chat with the Anthropic API. """
  # Call the chat function
  system_prompt = prompts_dict[request.chef_type]["initial_prompt"] + f"Please answer the user's\
    question {request.user_prompt}"
  prompt = format_prompt(system_prompt,
  request.user_prompt, request.chat_history)
  chef_type = request.chef_type
  # Convert the user message into a ChatMessage object
  user_message = ChatMessage(message=request.user_prompt, role="user")
  # If there is no chat history, create one
  if not request.chat_history:
    chat_history = [user_message]
  else:
    chat_history = request.chat_history + [user_message]
  response =  anthropic.completions.create(
    prompt=prompt,
    temperature=prompts_dict[request.chef_type]["temperature"],
    max_tokens_to_sample=prompts_dict[chef_type]["max_tokens_to_sample"],
    model="claude-2.1",
    stream=False,
  )
  # Convert the response into a ChatMessage object
  chef_message = ChatMessage(message=response.completion, role="assistant")
  # Add the chef message to the chat history
  chat_history.append(chef_message)

  # Return the response
  return {"chef_response" : response.completion, "chat_history" : chat_history}

# Define the basic recipe generation function
def create_recipe(request: RecipeRequest):
  """ Create a recipe with the Anthropic API. """
  # Create a prompt for the model to generate the recipe based on the user's specifications,
  # serving size, and chef type
  chef_type = request.chef_type
  system_prompt = prompts_dict[request.chef_type]["initial_prompt"]
  system_prompt += f"""The user would like you to generate
  a recipe for them with the following specifications: {request.specifications}.
  The serving size is {request.serving_size}. Please generate a recipe for them.
  Return the recipe portion of your response as JSON object in the following format:\n\n
  {AnthropicRecipe.schema_json(indent=2)} """

  user_prompt = f"Hi, Chef.  Please help me generate a recipe based on the specifications {request.specifications}\
  for a serving size of {request.serving_size}."

  # Convert the user message into a ChatMessage object
  user_message = ChatMessage(message=user_prompt, role="user")
  # If there is no chat history, create one
  if not request.chat_history:
    chat_history = [user_message]
  else:
    chat_history = request.chat_history + [user_message]
  prompt = format_prompt(system_prompt, user_prompt, request.chat_history)

  # Call the chat function
  response = anthropic.completions.create(
    prompt=prompt,
    temperature=prompts_dict[chef_type]["temperature"],
    max_tokens_to_sample=prompts_dict[chef_type]["max_tokens_to_sample"],
    model="claude-2.1",
    stream=False
  )
  recipe = extract_json_from_response(response.completion)
  # Convert the response into a ChatMessage object
  chef_message = ChatMessage(message=response.completion, role="assistant")
  # Add the chef message to the chat history
  chat_history.append(chef_message)
  
  # Return the response
  return {"chef_response" : response.completion, "recipe" : recipe, "chat_history" : chat_history}

def adjust_recipe(request: AdjustRecipeRequest):
  """ Adjust a recipe based on the user's adjustments. """
  # Call the chat function
  initial_prompt = f"""You have created a recipe {request.recipe} for the user.
  The user would like to make some adjustments {request.adjustments} to the recipe.
  Please return the new recipe as a JSON object in the following format:

  {AnthropicRecipe.schema_json(indent=2)}"""

  system_prompt = prompts_dict[request.chef_type]["initial_prompt"] + initial_prompt
  user_prompt = "Please adjust the recipe"
  prompt = format_prompt(system_prompt, user_prompt, request.chat_history)
  
  response = anthropic.completions.create(
    prompt=prompt,
    temperature=prompts_dict[request.chef_type]["temperature"],
    max_tokens_to_sample=prompts_dict[request.chef_type]["max_tokens_to_sample"],
    model="claude-2.1",
    stream=False
  )
  recipe = extract_json_from_response(response.completion)

  # Return the response
  return {"chef_response" : response, "adjusted_recipe" : recipe}

# Create a function to generate a pairing
def generate_pairing(request: PairingRequest):
  """ Generate a pairing for a recipe. """
  # Create a prompt for the model to generate the pairing based on the recipe
  system_prompt = prompts_dict[request.chef_type]["initial_prompt"] + f"""
  You have created a recipe {request.recipe} for the user.
  Please generate a pairing for the recipe. Return the pairing portion
  of your response as a JSON object in the following format:\n\n
  {Pairing.schema_json(indent=2)}"""

  user_prompt = "Please generate a pairing for the recipe."
  prompt = format_prompt(system_prompt, user_prompt)

  # Call the chat function
  response = anthropic.completions.create(
    prompt=prompt,
    temperature=prompts_dict[request.chef_type]["temperature"],
    max_tokens_to_sample=prompts_dict[request.chef_type]["max_tokens_to_sample"],
    model="claude-2.1",
    stream=False
  )
  pairing = extract_json_from_response(response.completion)

  # Return the response
  return {"chef_response" : response, "pairing" : pairing}
