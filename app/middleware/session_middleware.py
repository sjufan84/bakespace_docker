"""Initiating the middleware"""

# Initial Imports
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
        store = RedisStore(session_id)
        user_data = store.redis.get(session_id)

        # Add user data to the request state
        if user_data is not None:
            request.state.user_data = user_data

        # Proceed to the next middleware or route handler
        response = await call_next(request)

        # Set the session_id in the response headers for client to use in further interactions
        response.headers["session_id"] = session_id

        return response


# Create a RedisStore class to store the session_id
class RedisStore:
    """ Define a class to store the session_id. """
    def __init__(self, session_id: str):
        self.redis = redis.Redis(decode_responses=True)
        self.session_id = session_id 


def get_redis_store(request: Request) -> RedisStore:
    """ Create a function to get the RedisStore. """
    session_id = request.headers.get("session_id")
    # You can include any configuration logic here if needed
    return RedisStore(session_id)


app = FastAPI()

app.add_middleware(SessionMiddleware)
