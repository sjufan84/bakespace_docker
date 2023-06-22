from fastapi import FastAPI
from .routes import *

app = FastAPI()

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

# Include routers
app.include_router(chat_routes)
app.include_router(recipe_routes)
app.include_router(pairings)
app.include_router(image_routes)
