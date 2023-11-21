""" Pairings routes for the API """
import logging
from typing import Union
from fastapi import APIRouter, Depends
from app.services.redis_service import RedisService
from app.services.pairing_service import generate_pairings
from app.models.recipe import Recipe

router = APIRouter()

@router.post("/generate_pairings", response_description="The pairings returned as a dictionary.")
# Generate pairings
async def get_pairings(pairing_type: str, recipe: Union[str, dict, Recipe], redis_service: RedisService = Depends(RedisService)):
    """ Route to generate a list of pairings based on the pairing type and recipe. """
    return generate_pairings(pairing_type, recipe)

