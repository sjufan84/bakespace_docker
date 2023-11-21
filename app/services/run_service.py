""" Helper functions for running threads. """
from app.dependencies import get_openai_client

# Create a class for the recipe service
class RunService:
    """ A class to represent the recipe service. """
    def __init__(self, thread_id: str = None):
      """ Initialize the run service """
      self.thread_id = thread_id

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
