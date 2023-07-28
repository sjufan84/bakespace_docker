"""Initiating the middleware"""

# Initial Imports
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from fastapi import FastAPI, Request
import redis


class SessionMiddleware(BaseHTTPMiddleware):
    """ We need the middleware to extract the session_id from the query parameters
    and pass it to the RedisStore class. """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """ Define the dispatch method. """
        # Get the session_id from the query parameters
        session_id = request.query_params.get("session_id")
        # Pass the session_id to the RedisStore class
        request.state.store = get_redis_store(session_id)
        # Return the response
        response = await call_next(request)
        return response

# Create a RedisStore class to store the session_id
class RedisStore:
    """ Define a class to store the session_id. """
    def __init__(self, session_id: str):
        """ Define the constructor. """
        # Set the session_id
        self.session_id = session_id
        # Create a connection to Redis
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        
    def get(self, key: str) -> str:
        """ Define a function to get the key. """
        # Get the value from Redis
        value = self.redis.get(f"{self.session_id}_{key}")
        # Return the value
        return value
    
    def set(self, key: str, value: str) -> None:
        """ Define a function to set the key. """
        # Set the value in Redis
        self.redis.set(f"{self.session_id}_{key}", value)
        
    def delete(self, key: str) -> None:
        """ Define a function to delete the key. """
        # Delete the value from Redis
        self.redis.delete(f"{self.session_id}_{key}")
        
    def exists(self, key: str) -> bool:
        """ Define a function to check if the key exists. """
        # Check if the key exists
        return self.redis.exists(f"{self.session_id}_{key}")
    
    def clear(self):
        """ Define a function to clear the session. """
        # Get all the keys
        keys = self.redis.keys(f"{self.session_id}*")
        # Delete all the keys
        self.redis.delete(*keys)

# Create a function to get the RedisStore
def get_redis_store(session_id: str) -> RedisStore:
    """ Define a function to get the RedisStore. """
    # Return the RedisStore
    return RedisStore(session_id)


app = FastAPI()

# Add the middleware
app.add_middleware(SessionMiddleware)