""" This file is used to register the routes for the API.
Each route is registered to a router instance, and the router
instances are exported as a list for convenience. """
from fastapi import APIRouter
# Import the router files to register the routes
from app.routes.chat_routes import router as chat_routes
from app.routes.pairings_routes import router as pairings_routes
from app.routes.image_routes import router as image_routes
from app.routes.extraction_routes import router as extraction_routes
from app.routes.redis_routes import router as redis_routes

# Create instances of APIRouter for each router
router_chat = APIRouter()
router_pairings = APIRouter()
router_image = APIRouter()
router_extraction = APIRouter()
router_redis = APIRouter()

# Register the routers to the corresponding instances
router_chat.include_router(chat_routes)
router_pairings.include_router(pairings_routes)
router_image.include_router(image_routes)
router_extraction.include_router(extraction_routes)
router_redis.include_router(redis_routes)

# Export the routers as a list for convenience
routers = [router_chat, router_pairings, router_image,
router_extraction, router_redis]
