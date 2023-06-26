import os
from google.oauth2 import service_account
import toml
from dotenv import load_dotenv
load_dotenv()

def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")

def get_openai_org():
    return os.getenv("OPENAI_ORG")

def get_google_vision_credentials():
    config = toml.load("secrets.toml")
    return service_account.Credentials.from_service_account_info(config['gcp_service_account'])
