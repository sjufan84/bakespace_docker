""" This module defines the image service."""
import requests
from dotenv import load_dotenv
from redis import RedisError
from app.middleware.session_middleware import RedisStore
from app.dependencies import get_stability_api_key

load_dotenv()

# Define an ImageService class
class ImageService:
    """ A class to represent the image service. """
    def __init__(self, store: RedisStore = None):
        self.store = store
        self.session_id = self.store.session_id
        self.image = self.load_image_url()
        if not self.image:
            self.image = None

    def generate_image_url(self, image_prompt):
        """ Generate an image for a recipe """

        # Load the stable diffusion api key
        api_key = get_stability_api_key()
        r = requests.post(
            "https://api.deepai.org/api/stable-diffusion",

            data={
                'text':  f'{image_prompt}',
                'grid_size': "1",
            },
            headers={'api-key': api_key},
            timeout=100
        )
        # Save the image to redis
        self.save_image_url(r.json()['output_url'])

        # Return the json object containing the image url
        return r.json()

    def load_image_url(self):
        """ Load an image from the store by the image_name """
        try:
            image = self.store.redis.get(f'{self.session_id}_image')
            if image:
                return image
            else:
                return None
        except RedisError as e:
            print(f"Failed to load image from Redis: {e}")
            return None

    def save_image_url(self, image):
        """ Save an image to the store by the image_name """
        try:
            # Save the recipe to redis
            self.store.redis.set(f'{self.session_id}_image', image)
        except RedisError as e:
            print(f"Failed to save image to Redis: {e}")
        return image

    def delete_image_url(self):
        """ Delete an image from the store by the image_name """
        try:
            # Delete the recipe from redis
            self.store.redis.delete(f'{self.session_id}_image')
        except RedisError as e:
            print(f"Failed to delete image from Redis: {e}")
        return {"message": "Image deleted."}
