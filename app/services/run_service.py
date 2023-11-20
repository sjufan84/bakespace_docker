""" Helper functions for running threads. """
from redis import RedisError
from app.middleware.session_middleware import RedisStore
from app.dependencies import get_openai_client

# Create a class for the recipe service
class RunService:
    """ A class to represent the recipe service. """
    def __init__(self, store: RedisStore = None):
        self.store = store
        # Get the session_id from the store
        self.session_id = self.store.session_id
        # Get the thread from the store
        self.thread = self.load_thread()
        if not self.thread:
            self.thread = None
        # Get the run_id from the store
        self.run_ids = self.store.redis.lrange(f'{self.session_id}:run_ids', 0, -1)
        if not self.run_ids:
            self.run_ids = None
        # Check for the chef_type in the store
        self.chef_type = self.store.redis.get(f'{self.session_id}:chef_type')
        if not self.chef_type:
            self.chef_type = "home_cook"

    # Create a function to save a thread id to the store by the thread_id
    async def save_thread(self, thread_id: str):
        """ Save a thread id to the store by the thread_id """
        try:
            # Save the thread id to redis
            self.store.redis.set(f'{self.session_id}:thread_id', thread_id)
            return True
        except RedisError as e:
            print(f"Failed to save thread to Redis: {e}")
            return False

    # Create a function to load the current thread from the store
    async def load_thread(self):
        """ Load the current thread from the store """
        try:
            # Load the thread from redis
            thread_id = self.store.redis.get(f'{self.session_id}:thread_id')
            if thread_id:
                return thread_id
            else:
                return None
        except RedisError as e:
            print(f"Failed to load thread from Redis: {e}")
            return None

    # Create a function to load the list of run ids from the store
    async def load_run_ids(self):
        """ Load the list of run ids from the store """
        try:
            # Load the run ids from redis
            run_ids = self.store.redis.lrange(f'{self.session_id}:run_ids', 0, -1)
            if run_ids:
                return run_ids
            else:
                return None
        except RedisError as e:
            print(f"Failed to load run ids from Redis: {e}")
            return None

    # Create a function to save a run id to the store by the run_id
    async def save_run_id(self, run_id: str):
        """ Save a run id to the store by the run_id """
        try:
            # Save the run id to redis
            self.store.redis.rpush(f'{self.session_id}:run_ids', run_id)
            return True
        except RedisError as e:
            print(f"Failed to save run id to Redis: {e}")
            return False

    # Create a function to load messages from the store by the thread_id
    async def load_messages(self, thread_id: str = None, limit: int = 10):
        """ Load messages from the store by the thread_id """
        try: 
           # Check to see if there is a thread_id in the call, if not,
           # load the thread_id from the store
            if not thread_id:
                thread_id = self.load_thread()
            # Load the messages from redis
            messages = self.store.redis.lrange(f'{thread_id}:messages', 0, limit)
            if messages:
                return messages
            else:
                return None
        # If there is an error, return None
        except RedisError as e:
            print(f"Failed to load messages from Redis: {e}")
            return None

    async def get_chat_messages_from_messages(self, messages):
        """ Get the chat messages from the messages """
        chat_messages = []
        for message in messages:
            if isinstance(message["role"], "assistant") or isinstance(message["role"], "user"):
                chat_message = {
                    "role": message["role"],
                    "content": message["content"]
                }
            # Append the chat message to the list of chat messages
            chat_messages.append(chat_message)
        return chat_messages

    async def list_run_steps(self, thread_id: str = None, run_id: str = None, limit: int = 20, order: str = "desc"):
      """ List the steps from a run """
      client = get_openai_client()
      # Check to see if there is a thread_id in the call, if not,
      # load the thread_id from the store
      if not thread_id:
          thread_id = self.load_thread()
      # Check to see if there is a run_id in the call, if not,
      # load the run_id from the store
      if not run_id:
          run_id = self.load_run_ids()
      # Load the steps from redis
      run_steps = client.beta.threads.runs.steps.list(
          thread_id=thread_id,
          run_id=run_id,
          limit=limit,
          order=order
      )
      return run_steps

    async def get_tool_calls(self, thread_id: str = None, run_id: str = None):
        """ Get the tool calls from the run """
        tool_calls_list = []
        # Check to see if there is a thread_id in the call, if not,
        # load the thread_id from the store
        if not thread_id:
            thread_id = self.load_thread()
        # Check to see if there is a run_id in the call, if not,
        # load the run_id from the store
        if not run_id:
            run_id = self.load_run_ids()
        # Load the tool calls from redis
        steps = await self.list_run_steps(thread_id=thread_id, run_id=run_id)
        if steps:
          for step in steps:
            if step.type == "tool_calls" and step.step_details.type == "tool_calls":
              tool_calls = [step.step_details.tool_calls.type for tool_call in step.step_details.tool_calls]  
              tool_calls_list.append(tool_calls)
        else:
          tool_calls_list = None

        return tool_calls_list

    async def load_chef_type(self):
      """ Load the chef type from the store """
      try:
        # Load the chef type from redis
        chef_type = self.store.redis.get(f'{self.session_id}:chef_type')
        if chef_type:
          return chef_type
        else:
          return "home_cook"
      except RedisError as e:
        print(f"Failed to load chef type from Redis: {e}")
        return None  

    async def save_chef_type(self, chef_type: str): 
      """ Save the chef type to the store """
      try:
        # Save the chef type to redis
        self.store.redis.set(f'{self.session_id}:chef_type', chef_type)
        return True
      except RedisError as e:
        print(f"Failed to save chef type to Redis: {e}")
        return False
