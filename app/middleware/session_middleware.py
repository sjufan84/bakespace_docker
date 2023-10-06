"""Initiating the middleware"""

# Initial Imports
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse
from fastapi import Request, Response
import redis
import uuid


class SessionMiddleware(BaseHTTPMiddleware):
    """ Define a class to represent the session middleware. """
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        session_id = None
        # Extract the session_id from the headers
        if request.url.path not in ["/openapi.json", "/docs"]:
            session_id = request.query_params.get("session_id")
            if session_id is None:
                session_id = str(uuid.uuid4())
                #return JSONResponse(content={"detail": "session_id missing"}, status_code=400)

        # You might not need to store the session_id in Redis at this point
        # since you said that user data is retrieved during each API call

        # Proceed to the next middleware or route handler
        response = await call_next(request)

        # Set the session_id in the response headers for client to use in further interactions
        if session_id is not None:
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
    session_id = request.query_params.get("session_id")
    # You can include any configuration logic here if needed
    return RedisStore(session_id)


