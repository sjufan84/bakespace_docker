"""Initiating the middleware"""

# Initial Imports
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from fastapi import FastAPI, Request
import redis

class SessionMiddleware(BaseHTTPMiddleware):
    """ Define a class to represent the session middleware. """
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Extract the session_id from the headers
        session_id = request.headers.get("session_id")
        if session_id is None:
            # If there is no session_id in the headers, proceed without setting any user data
            return await call_next(request)

        # Get user data from Redis
        store = RedisStore()
        user_data = store.redis.get(session_id)

        # Add user data to the request state
        if user_data is not None:
            request.state.user_data = user_data

        # Proceed to the next middleware or route handler
        response = await call_next(request)

        return response

# Create a RedisStore class to store the session_id
class RedisStore:
    """ Define a class to store the session_id. """
    def __init__(self, session_id: Optional[str] = None):
        self.redis = redis.Redis(decode_responses=True)
        self.session_id = session_id or "default_key"

# Create a function to get the RedisStore
def get_redis_store() -> RedisStore:
    """ Create a function to get the RedisStore. """
    # You can include any configuration logic here if needed
    return RedisStore()


app = FastAPI()

app.add_middleware(SessionMiddleware)
