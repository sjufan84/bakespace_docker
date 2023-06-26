from fastapi import APIRouter

# Create instances of APIRouter for each router
router_chat = APIRouter()
router_recipe = APIRouter()
router_pairings = APIRouter()
router_image = APIRouter()
#router_extraction = APIRouter()


# Import the router files to register the routes
from .chat_routes import router as chat_routes
from .recipe_routes import router as recipe_routes
from .pairings_routes import router as pairings_routes
from .image_routes import router as image_routes
#from .extraction_routes import router as extraction_routes

# Register the routers to the corresponding instances
router_chat.include_router(chat_routes)
router_recipe.include_router(recipe_routes)
router_pairings.include_router(pairings_routes)
router_image.include_router(image_routes)
#router_extraction.include_router(extraction_routes)

# Export the routers as a list for convenience
routers = [router_chat, router_recipe, router_pairings, router_image]




