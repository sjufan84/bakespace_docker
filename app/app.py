from fastapi import FastAPI
from .routes import *
from .middleware.session_middleware import SessionMiddleware

description = """
# BakespaceAI FastAPI

## Project Overview

BakespaceAI FastAPI is a powerful backend solution designed to provide an array of functionality to be integrated with Bakespace website. With this backend, users can interact with Large Language Models (LLMs) via several endpoints to personalize their culinary experiences.

## Functionality

BakespaceAI FastAPI supports:

**Recipe Generation**: Based on user and system inputs, such as allergies, preferences, and cooking skill level, an LLM is leveraged to generate a custom recipe. The output is parsed into a Pydantic model, ready for downstream use.

**Chat Features**: Post-recipe generation, users can engage in a chat with the LLM about their recipe. The langchain library provides the chatbot with context for intelligent conversation.

**Recipe Text Extraction**: Users can upload recipes in various formats, including PDF, Word doc, text file, or an image of a handwritten recipe. These recipes are formatted and can be saved, discussed, or included in cookbooks.

**Image Generation**: Integration with Stability AI's image generation API allows for recipe-based image prompts, generating unique visuals for each recipe.

**Pairings Generator**: Each recipe can be accompanied by beverage pairings generated by an LLM, offering a complete dining experience.

## Dependencies

This project leverages several Python libraries to deliver its functionalities. These include:

*FastAPI* | *Langchain* | *OpenAI* | *Pydantic* | *Python-dotenv* | *Requests* | *Uvicorn*

**FastAPI (0.98.0)**: This is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

**Langchain (0.0.209)**: A library used to parse and handle natural language text. In this project, it's used to process and analyze textual data.

**OpenAI (0.27.7)**: OpenAI's Python client library, used for interacting with the OpenAI API. It allows access to powerful AI models for tasks like translation, text completion, and more.

**Pydantic (1.10.9**): A data validation library used to set the data types of incoming request data. It also provides helpers to convert between types, and to parse complex data structures.

**Python-dotenv (1.0.0)**: This library is used to separate secret credentials and your code. It allows you to add, edit, and load environment variables from .env files.

**Requests (2.31.0)**: A simple, yet powerful HTTP library used to send HTTP requests. It abstracts the complexities of making requests behind a simple API.

**Uvicorn (0.22.0)**: An ASGI server that's needed to run your FastAPI applications. It provides a lightning-fast, asynchronous server for Python applications.

## Installation

To install these dependencies, use 'pip', the Python package installer:

```python
pip install -r requirements.txt
"""



app = FastAPI(
    title = "BakeSpace AI",
    description = description,
    version = "0.1",
    summary = "Backend to allow BakeSpace users to interact\
            with Large Language Models (LLMs) to personalize\
            their culinary experiences.",
            contact = {
                "name": "Dave Thomas",
                "url": "https://enoughwebapp.com",
                "email": "dave_thomas@enoughwebapp.com"
            },
            license_info = {
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT"
            }
)

# Add a middleware to your FastAPI application
app.add_middleware(SessionMiddleware)


# Include all the routers in your FastAPI application
for router in routers:
    app.include_router(router)
# Additional configuration or middleware setup if needed
# ...

# Import routers
from app.routes.chat_routes import router as chat_routes
from app.routes.recipe_routes import router as recipe_routes
from app.routes.pairings_routes import router as pairings
from app.routes.image_routes import router as image_routes
from app.routes.extraction_routes import router as extraction_routes

# Include routers
app.include_router(chat_routes)
app.include_router(recipe_routes)
app.include_router(pairings)
app.include_router(image_routes)
app.include_router(extraction_routes)
