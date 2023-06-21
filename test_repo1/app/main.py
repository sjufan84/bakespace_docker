from fastapi import FastAPI
import os

app = FastAPI()

# Environment dependencies
def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")

def get_openai_org():
    return os.getenv("OPENAI_ORG")

# Import routers
from .routes import recipe_routes

# Include routers
app.include_router(recipe_routes.router)
