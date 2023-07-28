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
        session_id = request.query_params.get("session_id")

        print(f"Query parameters: {request.query_params}")  # Debug line
        print(f"Session ID: {session_id}")  # Debug line

        if not session_id:
            # Handle the case when there is no session_id provided.
            # You can return an error response or assign a default session_id
            return Response("No session_id provided", status_code=400)
        
        request.state.session_id = session_id

        # You might not need to store the session_id in Redis at this point
        # since you said that user data is retrieved during each API call

        # Proceed to the next middleware or route handler
        response = await call_next(request)

        # Set the session_id in the response headers for client to use in further interactions
        response.headers["session_id"] = request.state.session_id

        return response




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

app.add_middleware(SessionMiddleware)
