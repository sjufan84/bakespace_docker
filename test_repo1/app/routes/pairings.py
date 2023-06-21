from fastapi import APIRouter, Depends, Form, Request, 
from ..main import get_openai_api_key, get_openai_org
from ..services.pairing_service import get_pairing
from typing import List, Optional

router = APIRouter()


# Routes for the pairing functions
# Get the pairing type i.e. wine, beer, etc.
@router.post("/get_pairing_type")
def get_pairing_type(request: Request, pairing_type: str = Form(...)):
    request.session['pairing_type'] = pairing_type
    # TODO: Return the correct template / redirect to the correct page on the bakespace frontend

@router.post("/generate_pairing")
# Generate the pairing
def generate_pairing(request: Request):
    recipe = request.session['recipe']
    pairing_type = request.session['pairing_type']
    pairing = get_pairing(recipe, pairing_type)
    request.session['pairing'] = pairing
    # TODO: Add the pairing to the database
    # TODO: Return the correct template / redirect to the correct page on the bakespace frontend

