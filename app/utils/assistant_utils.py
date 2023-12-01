""" Utilities to support the run endpoints """
import os
import sys
import time
import json
from typing import List
from fastapi import UploadFile, Query, Depends
#from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
# Add the app directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.recipe_service import ( # noqa E402
  adjust_recipe, # noqa E402
  format_recipe, # noqa E402
  initial_pass, # noqa E402
  save_recipe, # noqa E402
) # noqa E402
from services.anthropic_service import AnthropicRecipe, create_recipe # noqa E402
from services.pairing_service import generate_pairings # noqa E402
from services.image_service import generate_image # noqa E402
from app.models.pairing import Pairing # noqa E402
from app.services.run_service import RunService # noqa E402
from app.dependencies import get_openai_client # noqa E402

# Load environment variables
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_KEY2")
organization = os.getenv("OPENAI_ORG2")

# Create the OpenAI client
client = OpenAI(api_key=api_key, organization=organization, max_retries=3, timeout=10)

# Create the chef_type / assistant_id dictionary
id_dict = {
    "home_cook": "asst_DXoYw6E9Nky5RfJ0D7OhPhDd",
    "pro_chef": "asst_zt5sYkWN1nuNw6SO1e2D8RZO",
    "adventurous_chef": "asst_7JDTkQhCiGWTE9i0VqBdvnpX"
}

def get_thread_tool_outputs(thread_id: str = None):
  """ Get the function outputs from the thread """
  if not thread_id:
    raise ValueError("Thread ID is required.")
  function_outputs = []
  run_steps = list_thread_run_steps(thread_id=thread_id)
  for step in run_steps:
    if step.step_details.tool_calls.function:
      function_outputs.append({
        "function_name": step.step_details.tool_calls.function.name,
        "output": step.step_details.tool_calls.function.output,
        "arguments": step.step_details.tool_calls.function.arguments})
  return function_outputs

# Define a function to iterate through the tool calls and return the
# outputs for a specific tool'
def get_specific_thread_tool_outputs(tool_names: List[str], thread_id: str = None):
    """ Get the tool outputs for specific tools in a thread """
    filtered_tool_outputs = []
    if not thread_id:
        raise ValueError("Thread ID is required.")
    tool_outputs = get_thread_tool_outputs(thread_id=thread_id)
    # Iterate through the tool outputs and if the tool name is in the list
    # of tool names, append the output to the list
    for tool_output in tool_outputs:
        if tool_output["function_name"] in tool_names:
            filtered_tool_outputs.append(tool_output)

    return filtered_tool_outputs

functions_dict = {
    "adjust_recipe": {
        "function" : adjust_recipe,
        # For each field in the returned recipe, map a key to the field name
        "metadata_message": "Current adjusted condrecipe: ",
    },
    "create_recipe": {
        "function" : create_recipe,
        "metadata_message": "Current recipe: ",
    },
    "format_recipe": {
        "function" : format_recipe,
        "metadata_message": "Current formatted recipe: ",
    },
    #"generate_pairings": {
    #    "function" : generate_pairings,
    #    "metadata_message": "Current pairings: ",
    #},
    "generate_image": {
        "function" : generate_image,
        "metadata_message": "Current image: ",
    },
    "initial_pass": {
        "function" : initial_pass,
        "metadata_message": "Current initial pass: ",
    },
    "save_recipe": {
        "function" : save_recipe,
        "metadata_message": "Current saved recipe: ",
    }
}

# Define a function to add messages to the thread for metadata storage
def add_message(thread_id: str, function_name: str = None,
  meta_map: dict = None):
  """ Add a message to the thread """ 
  if not thread_id:
    raise ValueError("Thread ID is required.")
  if not function_name:
    raise ValueError("Function name is required.")
  if not meta_map:
    raise ValueError("Metadata is required.")
  # Create the message
  thread_message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=functions_dict[function_name]["metadata_message"],
    metadata=meta_map
  )

  return thread_message

def get_session_id(session_id: str = Query(...)):
    """ Dependency function to get the session id from the header """
    return session_id

def get_run_service(session_id:str = Depends(get_session_id)):
   return RunService(session_id)  

def call_named_function(function_name: str, **kwargs):
    try:
        # Check if the function name exists in the dictionary
        if function_name in functions_dict:
            # Call the function
            function_output = functions_dict[function_name]["function"](**kwargs)
            # Return the function output
            return function_output
        else:
            return f"Function {function_name} not found."
    except TypeError as e:
        return f"Error in calling {function_name}: {e}"
'''

class Message(BaseModel):
    role: str = "user"
    content: str = Field(..., description="The content of the message")

# Create the endpoint url for the function we want to call
fastapi_base_url = "http://localhost:8000"

# Define a function to create a run
def create_run(thread_id: str, assistant_id: str):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run
'''

def poll_run_status(run_id: str, thread_id: str):
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    tool_return_values = []

    while run_status.status not in ["completed", "failed", "expired", "cancelling", "cancelled"]:
        if run_status.status == "requires_action":
            # Handle the action required by the assistant
            tool_outputs = []
            
            tool_calls = run_status.required_action.submit_tool_outputs.tool_calls

            for tool_call in tool_calls:
                # Extract necessary details
                function_name = tool_call.function.name
                tool_call_id = tool_call.id
                parameters = json.loads(tool_call.function.arguments)

                # Call the function
                function_output = call_named_function(function_name=function_name, **parameters)
                
                # Append the tool output
                tool_outputs.append({
                    "tool_call_id": tool_call_id,
                    "output": function_output
                })
                # Add a message to the thread for metadata storage
                #add_message(thread_id=thread_id,
                #function_name=function_name, meta_map=parameters)
                # Append the tool return values
                tool_return_values.append({
                    "tool_name" : function_name,
                    "output": function_output
                })

            # Submit the tool outputs to the run
            run = client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)
            run_status = run
        else:
            # If the status is "queued" or "in-progress", wait and then retrieve status again
            time.sleep(1.45)
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

    # Gather the final messages after completion
    final_messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)

    return {
        "thread_id": thread_id, 
        "message": final_messages.data[0].content[0].text.value,
        "run_id": run_id,
        "tool_return_values": tool_return_values
    }



# Define a function to receive and upload files to the assistant
async def upload_files(files: List[UploadFile]):
    """ Takes in the list of file objects and uploads them to the assistant """
    file_ids_list = []
    for file in files:
        # Upload the file
        response = client.files.create(file=file, purpose="assistants")
        # Append the file url to the list
        file_id = response.id
        file_ids_list.append(file_id)
    return file_ids_list

async def create_assistant_files(file_ids: List[str], assistant_id: str = None):
  """ Create the assistant files """
  if not assistant_id:
    run_service = get_run_service()
    chef_type = run_service.load_chef_type()
    assistant_id = id_dict[chef_type]
  assistant_files_list = []
  for file_id in file_ids:
    assistant_file = client.beta.assistants.files.create(
      assistant_id=assistant_id, 
      file_id=file_id
    )
    assistant_files_list.append(assistant_file)

  return assistant_files_list

def get_assistant_id(chef_type: str):
  """ Load the assistant id from the store """
  #run_service = get_run_service()
  # Check to see if there is a chef_type in the call, if not,
  # load the chef_type from the store
  # Set the assistant id
  assistant_id = id_dict[chef_type]
  return assistant_id

def list_runs(thread_id: str):
    """ List the runs from a thread """
    client = get_openai_client()
    # Check to see if there is a thread_id in the call, if not,
    # load the thread_id from the store
    if not thread_id:
        raise ValueError("Thread ID is required.")
    # Load the runs from redis
    runs = client.beta.threads.runs.list(thread_id=thread_id)
    return runs

def list_thread_run_steps(thread_id: str):
      """ List the steps from a thread """
      client = get_openai_client()
      # Check to see if there is a thread_id in the call, if not,
      # load the thread_id from the store
      if not thread_id:
        raise ValueError("Thread ID is required.")
      # List the runs from the thread
      runs = list_runs(thread_id=thread_id)
      steps_list = []
      for run in runs:
        steps = client.beta.threads.runs.steps.list(
          thread_id=thread_id,
          run_id=run.id
        )
        steps_list.append(steps)

      return steps_list
