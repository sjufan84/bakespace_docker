""" Redis utilities """
import json
import redis
from redis.exceptions import RedisError
from fastapi import Query

r = redis.Redis(
  host='redis-11565.c124.us-central1-1.gce.cloud.redislabs.com',
  port=11565,
  password='yvl6wEThAapkABEhVcsEMMUToNJokxP9')

def get_session_id(session_id: str = Query(...)):
    """ Dependency function to get the session id from the header """
    return session_id

def save_recipe(recipe_name: str, recipe: dict):
    """ Save the recipe to Redis. """
    session_id = get_session_id() # Get the session id from the header
    try:
        recipe_json = json.dumps(recipe)
        r.set(f'{session_id}:{recipe_name}', recipe_json)
    except RedisError as e:
        print(f"Failed to save recipe to Redis: {e}")
    return print("Recipe saved successfully.")