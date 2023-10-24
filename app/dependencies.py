""" This file contains all the dependencies for the app. """
import os
import logging
import toml
from fastapi import Depends, Query
from google.oauth2 import service_account
from dotenv import load_dotenv
from app.middleware.session_middleware import RedisStore, get_redis_store
from app.services.chat_service import ChatService
from app.services.recipe_service import RecipeService
from app.services.extraction_service import ExtractionService
from app.services.pairing_service import PairingService
load_dotenv()

def get_openai_api_key():
    """ Function to get the OpenAI API key. """
    return os.getenv("OPENAI_KEY2")

def get_openai_org():
    """ Function to get the OpenAI organization. """
    return os.getenv("OPENAI_ORG2")

def get_google_vision_credentials():
    """ Function to get the Google Vision credentials. """
    config = toml.load("secrets.toml")
    return service_account.Credentials.from_service_account_info(config['gcp_service_account'])

def get_stability_api_key():
    """ Function to get the Stability API key. """
    return os.getenv("STABLE_DIFFUSION_API_KEY")

def get_anthropic_api_key():
    """ Function to get the Anthropic API key. """
    return os.getenv("ANTHROPIC_API_KEY")

def get_session_id(session_id: str = Query(...)):
    """ Dependency function to get the session id from the header """
    return session_id

def get_chat_service(store: RedisStore = Depends(get_redis_store)):
    """ Dependency function to get the chat service. Takes in session_id and store. """
    logging.debug("Initializing chat service.")
    return ChatService(store=store)

def get_recipe_service(store: RedisStore = Depends(get_redis_store)):
    """ Dependency function to get the recipe service. """
    logging.debug("Initializing recipe service.")
    return RecipeService(store=store)

def get_extraction_service(store: RedisStore = Depends(get_redis_store)):
    """ Dependency function to get the extraction service. """
    logging.debug("Initializing extraction service.")
    return ExtractionService(store=store)

# A new dependency function:
def get_pairing_service(store: RedisStore = Depends(get_redis_store)) -> PairingService:
    """ Dependency function to get the recipe service """
    return PairingService(store=store)
