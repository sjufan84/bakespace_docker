""" Dependencies for the FastAPI app """
import os
import toml
from google.oauth2 import service_account
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_openai_api_key():
    """ Get the OpenAI API key from the environment. """
    return os.getenv("OPENAI_API_KEY")

def get_openai_org():
    """ Get the OpenAI organization from the environment. """
    return os.getenv("OPENAI_ORG")

def get_google_vision_credentials():
    """ Get the Google Vision credentials from the environment. """
    config = toml.load("secrets.toml")
    return service_account.Credentials.from_service_account_info(config['gcp_service_account'])

def get_stability_api_key():
    """ Get the stability API key from the environment. """
    return os.getenv("STABLE_DIFFUSION_API_KEY")

def get_openai_client():
    """ Get the OpenAI client. """
    return OpenAI(api_key=get_openai_api_key(), organization=get_openai_org(), max_retries=3, timeout=10)
