""" This file contains all the dependencies for the app. """
import os
import toml
from google.oauth2 import service_account
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
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
    """ Get the stability API key from the environment. """
    return os.getenv("STABLE_DIFFUSION_API_KEY")

def get_openai_client():
    """ Get the OpenAI client. """
    return OpenAI(api_key=get_openai_api_key(), organization=get_openai_org(), max_retries=3, timeout=10)
