""" Redis service for interacting with the Redis database. """
import json
from redis.exceptions import RedisError
from app.middleware.session_middleware import RedisStore, get_redis_store


class RedisService:
  """ RedisService is a class that represents a Redis service. """
  def __init__(self, store: RedisStore = None):
    self.store = get_redis_store()
    self.session_id = self.store.session_id

  def load_chat_history(self):
      """ Load the chat history from Redis. """
      try:
          # Load the chat history from redis.
          # If there is not chat history, return an empty list
          chat_history = self.store.redis.get(f'{self.session_id}:chat_history')
          if chat_history:
              return json.loads(chat_history)
          return []
      except RedisError as e:
          print(f"Failed to load chat history from Redis: {e}")
          return []

  def save_chat_history(self):
      """ Save the chat history to Redis. """
      try:
          chat_history_json = json.dumps(self.chat_history)
          self.store.redis.set(f'{self.session_id}:chat_history', chat_history_json)
      except RedisError as e:
          print(f"Failed to save chat history to Redis: {e}")
      return self.chat_history

  def get_recipe(self, recipe_name):
      """ Get a recipe from Redis. """
      try:
          recipe = self.store.redis.get(f'{self.session_id}:{recipe_name}')
          if recipe:
              return json.loads(recipe)
          return []
      except RedisError as e:
          print(f"Failed to get recipe from Redis: {e}")
          return []

  def save_recipe(self, recipe_name, recipe):
      """ Save a recipe to Redis. """
      try:
          recipe_json = json.dumps(recipe)
          self.store.redis.set(f'{self.session_id}:{recipe_name}', recipe_json)
      except RedisError as e:
          print(f"Failed to save recipe to Redis: {e}")
      return self.recipe

  def save_recipe_image(self, recipe_name, recipe_image):
      """ Save a recipe image to Redis. """
      try:
          self.store.redis.set(f'{self.session_id}:{recipe_name}:image', recipe_image)
      except RedisError as e:
          print(f"Failed to save recipe image to Redis: {e}")
      return self.recipe_image

  def get_recipe_image(self, recipe_name):
      """ Get a recipe image from Redis. """
      try:
          recipe_image = self.store.redis.get(f'{self.session_id}:{recipe_name}:image')
          if recipe_image:
              return recipe_image
          return []
      except RedisError as e:
          print(f"Failed to get recipe image from Redis: {e}")
          return []

  def save_recipe_pairings(self, recipe_name, recipe_pairings):
      """ Save a recipe pairings to Redis. """
      try:
          recipe_pairings_json = json.dumps(recipe_pairings)
          self.store.redis.set(f'{self.session_id}:{recipe_name}:pairings', recipe_pairings_json)
      except RedisError as e:
          print(f"Failed to save recipe pairings to Redis: {e}")
      return self.recipe_pairings

  def get_recipe_pairings(self, recipe_name):
      """ Get a recipe pairings from Redis. """
      try:
          recipe_pairings = self.store.redis.get(f'{self.session_id}:{recipe_name}:pairings')
          if recipe_pairings:
              return json.loads(recipe_pairings)
          return []
      except RedisError as e:
          print(f"Failed to get recipe pairings from Redis: {e}")
          return []

