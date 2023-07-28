"""Initiating the middleware"""

# Initial Imports
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from fastapi import FastAPI, Request, Depends, Query
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
            # You can return an error response or assign a default session_id
            return Response("No session_id provided", status_code=400)

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

def get_session_id(session_id: str = Query(...)):
    """ Dependency function to get the session id from the query parameters """
    return session_id

def get_redis_store(session_id: str = Depends(get_session_id)) -> RedisStore:
    """ Create a function to get the RedisStore. """
    # You can include any configuration logic here if needed
    return RedisStore(session_id)



app = FastAPI()

app.add_middleware(SessionMiddleware)
