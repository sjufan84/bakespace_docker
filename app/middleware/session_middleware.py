""" This module contains the SessionMiddleware class and RedisStore class """
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import FastAPI, Request, Response
import redis

class SessionMiddleware(BaseHTTPMiddleware):
    """ SessionMiddleware is a class that represents a middleware for sessions """
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        session_id = None  # Initialize session_id to None

        if request.url.path not in ["/openapi.json", "/docs", "/redoc"]:
            session_id = request.query_params.get("session_id")

            if session_id is None:
                return Response("No session_id provided", status_code=400)

        response = await call_next(request)

        if session_id:  # Only set the session_id header if it's not None
            response.headers["session_id"] = session_id

        return response

class RedisStore:
    """ RedisStore is a class that represents a Redis store for a session """
    def __init__(self, session_id: str):
        self.redis = redis.Redis(decode_responses=True)
        self.session_id = session_id
        self.chef_type = "Home Cook"

def get_redis_store(request: Request) -> RedisStore:
    """ get_redis_store is a function that returns a RedisStore object """
    session_id = request.query_params.get("session_id")
    return RedisStore(session_id)

# Initialize FastAPI app and add middleware
app = FastAPI()
app.add_middleware(SessionMiddleware)
