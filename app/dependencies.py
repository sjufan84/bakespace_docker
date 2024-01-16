""" This file contains all the dependencies for the app. """
import os
import json
from google.oauth2 import service_account
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# Load environment variables
load_dotenv()


def get_openai_api_key():
    """ Function to get the OpenAI API key. """
    return os.getenv("OPENAI_API_KEY")

def get_openai_org():
    """ Function to get the OpenAI organization. """
    return os.getenv("OPENAI_ORG")

'''def get_google_vision_credentials():
    """ Function to get the Google Vision credentials from an environment variable. """
    try:
      credentials = service_account.Credentials.from_service_account_file("credentials.json")
      return credentials
    except Exception as e:
      print(e)'''

def get_google_vision_credentials():
    """ Function to get the Google Vision credentials from an environment variable. """
    try:
      credentials = service_account.Credentials.from_service_account_info(json.loads(os.getenv("GOOGLE_CREDS")))
      return credentials
    except Exception as e:
      print(e)

def get_stability_api_key():
    """ Get the stability API key from the environment. """
    return os.getenv("STABLE_DIFFUSION_API_KEY")

def get_openai_client():
    """ Get the OpenAI client. """
    return OpenAI(api_key=get_openai_api_key(), organization=get_openai_org(), max_retries=3, timeout=10)

def get_anthropic_client():
    """ Get the Anthropic client. """
    return Anthropic(os.getenv("ANTHROPIC_KEY"))
