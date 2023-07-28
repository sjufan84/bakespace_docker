"""Initiating the middleware"""

# Initial Imports
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from fastapi import FastAPI, Request
import redis


class SessionMiddleware(BaseHTTPMiddleware):
    """ We need the middleware to extract the session_id from the query parameters
    and inject the RedisStore into the request state. """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """ Define the dispatch method. """
        # Get the session_id from the query parameters
        session_id = request.query_params.get('session_id')
        # Inject the RedisStore into the request state
        request.state.store = get_redis_store(session_id)
        # Call the next middleware
        response = await call_next(request)
        # Return the response
        return response

# Create a RedisStore class to store the session_id
class RedisStore:
    """ Define a class to store the session_id. """
    def __init__(self, session_id: str):
        self.redis = redis.Redis(decode_responses=True)
        self.session_id = session_id 

# Define the "get_redis_store" function
# This function will be used as a dependency in the routes
# and should retrieve the session_id from the query parameters
# and return a RedisStore object
def get_redis_store(session_id: str):
    """ Define a function to get the RedisStore object. """
    return RedisStore(session_id)

app = FastAPI()

app.add_middleware(SessionMiddleware)
