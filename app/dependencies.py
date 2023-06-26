import os
from dotenv import load_dotenv
load_dotenv()

def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")

def get_openai_org():
    return os.getenv("OPENAI_ORG")

def get_google_vision_credentials():
    return os.getenv("GOOGLE_VISION_CREDENTIALS")
