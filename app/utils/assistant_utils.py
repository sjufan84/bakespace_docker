""" Utilities to support the run endpoints """
import asyncio
import json
import logging
import os
import sys
from dotenv import load_dotenv
# Add the app directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.recipe_service import ( # noqa E402
  # adjust_recipe, # noqa E402
  format_recipe, # noqa E402
  #save_recipe, # noqa E402 # noqa E402
  create_recipe # noqa E402
) # noqa E402
# from services.image_service import generate_image # noqa E402
from app.models.recipe import Recipe # noqa E402
from app.dependencies import get_openai_client # noqa E402

logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

logger = logging.getLogger("main")

# Create the OpenAI client
client = get_openai_client()

# Create the chef_type / assistant_id dictionary
id_dict = {
    "home_cook": "asst_DXoYw6E9Nky5RfJ0D7OhPhDd",
    "pro_chef": "asst_zt5sYkWN1nuNw6SO1e2D8RZO",
    "adventurous_chef": "asst_7JDTkQhCiGWTE9i0VqBdvnpX"
}

def adjust_recipe(adjusted_recipe):
    """ Return an adjusted recipe object """
    return adjusted_recipe

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

    # "generate_image": {
    #    "function" : generate_image,
    #    "metadata_message": "Current image: ",
    # },

    # "save_recipe": {
    #     "function" : save_recipe,
    #     "metadata_message": "Current saved recipe: ",
    # }
}


async def call_named_function(function_name: str, **kwargs):
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

async def retrieve_run_status(thread_id, run_id):
    try:
        # Assuming client has an async method for retrieving run status
        return client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    except Exception as e:
        logging.error(f"Error retrieving run status: {e}")
        return None

async def poll_run_status(run_id: str, thread_id: str):
    run_status = await retrieve_run_status(thread_id, run_id)
    if run_status is None:
        return None

    tool_return_values = []

    while run_status.status not in ["completed", "failed", "expired", "cancelling", "cancelled"]:
        if run_status.status == "requires_action":
            tool_outputs = []
            tool_calls = run_status.required_action.submit_tool_outputs.tool_calls

            async def process_tool_call(tool_call):
                function_name = tool_call.function.name
                logging.info(f"Processing tool call for function {function_name}")
                tool_call_id = tool_call.id
                logging.debug(f"Processing tool call {tool_call_id} for function {function_name}")
                parameters = json.loads(tool_call.function.arguments)
                logging.debug(
                    f"Processing tool call {tool_call_id}\
                    for function {function_name} with parameters {parameters}"
                )

                function_output = await call_named_function(function_name=function_name, **parameters)

                tool_outputs.append({
                    "tool_call_id": tool_call_id,
                    "output": json.dumps(function_output)
                })

                tool_return_values.append({
                    "tool_name": function_name,
                    "output": function_output
                })

            # Process each tool call in parallel
            await asyncio.gather(*(process_tool_call(tool_call) for tool_call in tool_calls))

            try:
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id, run_id=run_id, tool_outputs=tool_outputs)
                run_status = run
            except Exception as e:
                logging.error(f"Error submitting tool outputs: {e}")
                return None
        else:
            await asyncio.sleep(1.5)  # Non-blocking sleep
            run_status = await retrieve_run_status(thread_id, run_id)
            if run_status is None:
                return None

    try:
        final_messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
    except Exception as e:
        logging.error(f"Error retrieving final messages: {e}")
        return None

    return {
        "thread_id": thread_id,
        "message": final_messages.data[0].content[0].text.value if final_messages else "No final message",
        "run_id": run_id,
        "tool_return_values": tool_return_values[0]["output"] if tool_return_values else "No tool return values"
    }

def get_assistant_id(chef_type: str):
  """ Load the assistant id from the store """
  assistant_id = id_dict[chef_type]
  return assistant_id

def create_thread(role: str, content: str, metadata = None):
  logger.info(f"Creating thread with role {role} and content {content}")
  thread = client.beta.threads.create(
      messages=[
          {
              "role": role,
              "content": content,
              "metadata": metadata
          },
      ]
  )
  logger.info(f"Created thread with id {thread.id}")
  return thread.id
