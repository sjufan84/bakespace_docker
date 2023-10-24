""" Define the core models for the chat service
using langchain's chatmodels """
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from ..dependencies import get_openai_api_key, get_openai_org, get_anthropic_api_key


# Tools  
def generate_recipe(prompt, chef_type):
  
  return parse_recipe(recipe_text)

def parse_recipe(text):
  # Use parser to extract structured recipe
  recipe = RecipeParser.parse(text) 
  return recipe

def chat_about_recipe(prompt, recipe):
  model = OpenAI(name="recipe_chatbot")
  response = model.generate(prompt, recipe=recipe)
  return response

tools = [
  Tool("GenerateRecipe", generate_recipe),
  Tool("ParseRecipe", parse_recipe),
  Tool("ChatRecipe", chat_about_recipe)
]

# Chat model
chat_llm = OpenAI(name="master_chef_chatbot")

# Agent
agent = initialize_agent(tools, chat_llm, agent=Agent.FUNCTIONS)

# Sample conversations
specs = "chicken pasta for 2 people"
chef_type = "home"
response = agent.run(f"Chef, can you give me a {specs} recipe in a {chef_type} style?")
recipe = response.recipe

question = "How long will this take to make?"  
response = agent.run(question, recipe=recipe)
print(response)

# Modify recipe
adjustments = "double the garlic, cook the chicken less"
response = agent.run(adjustments, recipe=recipe)
new_recipe = response.recipe
    