from fastapi import APIRouter

# Create instances of APIRouter for each router
router_chat = APIRouter()
router_recipe = APIRouter()
router_pairings = APIRouter()
router_image = APIRouter()
# router_text_extraction = APIRouter()


# Import the router files to register the routes
from .chat_routes import router as chat_routes
from .recipe_routes import router as recipe_routes
from .pairings_routes import router as pairings_routes
from .image_routes import router as image_routes
#from .text_extraction import app as text_extraction -- @TODO: migrate the rest of the text extraction functions from the Streamlit app to the FastAPI app

# Register the routers to the corresponding instances
router_chat.include_router(chat_routes)
router_recipe.include_router(recipe_routes)
router_pairings.include_router(pairings_routes)
router_image.include_router(image_routes)
#router_text_extraction.include_router(text_extraction)

# Export the routers as a list for convenience
routers = [router_chat, router_recipe, router_pairings, router_image]




