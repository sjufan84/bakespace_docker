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
        # Extract the session_id from the query parameters
        session_id = request.query_params.get("session_id")

        if session_id is None:
            # Handle the case when there is no session_id provided.
            return Response("No session_id provided", status_code=400)

        # Store the session_id in the request state so it can be accessed later
        request.state.session_id = session_id

        # Proceed to the next middleware or route handler
        response = await call_next(request)

        return response

# Create a RedisStore class to store the session_id
class RedisStore:
    """ Define a class to store the session_id. """
    def __init__(self, session_id: str):
        self.redis = redis.Redis(decode_responses=True)
        self.session_id = session_id 

def get_redis_store(request: Request):
    """ Create a function to get the RedisStore. """
    # You can include any configuration logic here if needed
    return RedisStore(request.state.session_id)




app = FastAPI()

app.add_middleware(SessionMiddleware)
