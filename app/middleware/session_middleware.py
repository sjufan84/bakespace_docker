""" This module contains the SessionMiddleware class and RedisStore class """
# import uuid
import os
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import FastAPI, Request, Response
import redis
import logging

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

redis_password = os.getenv('REDIS_PASSWORD')

r = redis.Redis(
    host = 'redis-11565.c124.us-central1-1.gce.cloud.redislabs.com',
    port = 11565,
    password = redis_password)

session_id = None
class SessionMiddleware(BaseHTTPMiddleware):
    """ SessionMiddleware is a class that represents a middleware for sessions """
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        session_id = request.headers.get("Session-ID")  # Using hyphenated header field
        logger.debug(f"Received Session-ID: {session_id}")

        # Optional: Validate session_id here

        response = await call_next(request)

        if session_id:  # Only set the session_id header if it's not None
            response.headers["Session-ID"] = session_id  # Ensuring header field consistency
            logger.debug(f"Set Session-ID in response headers: {session_id}")

        return response

class RedisStore:
    """ RedisStore is a class that represents a Redis store for a session """
    def __init__(self, session_id: str):
        self.redis = r
        self.session_id = session_id
        logger.debug(f"Initialized RedisStore with Session-ID: {session_id}")

def get_redis_store(request: Request) -> RedisStore:
    """ get_redis_store is a function that returns a RedisStore object """
    session_id = request.headers.get("Session-ID")  # Ensuring header field consistency
    logger.debug(f"Getting RedisStore with Session-ID: {session_id}")
    return RedisStore(session_id)

# Initialize FastAPI app and add middleware
app = FastAPI()
app.add_middleware(SessionMiddleware)
logger.debug("Added SessionMiddleware to FastAPI app")
