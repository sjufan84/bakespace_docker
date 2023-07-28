"""Initiating the middleware"""

# Initial Imports
from fastapi import FastAPI, Request
import redis






# Create a RedisStore class to store the session_id
class RedisStore:
    """ Define a class to store the session_id. """
    def __init__(self, session_id: str):
        self.redis = redis.Redis(decode_responses=True)
        self.session_id = session_id 


def get_redis_store(request: Request, session_id : str) -> RedisStore:
    """ Create a function to get the RedisStore. """
    session_id = request.query_params.get("session_id")
    # You can include any configuration logic here if needed
    return RedisStore(session_id)


app = FastAPI()

