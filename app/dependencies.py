""" This file contains all the dependencies for the app. """
import os
import json
from google.oauth2 import service_account
from dotenv import load_dotenv
from openai import OpenAI
import anthropic

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
    return OpenAI(api_key=get_openai_api_key(), organization=get_openai_org(), max_retries=3, timeout=55)

def get_query_filter_client():
    """ Get the Query Filter client. """
    return OpenAI(api_key=get_openai_api_key(), organization=get_openai_org(), max_retries=1, timeout=25)

def get_anthropic_client():
    anthropic_client = anthropic.Client(
        api_key=os.getenv("ANTHROPIC_KEY"), max_retries=3, timeout=35)

    return anthropic_client
