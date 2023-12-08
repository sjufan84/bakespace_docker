""" This module defines the chat routes for the API. """
from typing import List, Optional
import logging
import json
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from app.utils.assistant_utils import poll_run_status, get_assistant_id, upload_files
from app.models.runs import (
  CreateThreadRunRequest, CreateMessageRunRequest, CreateThreadRequest, GetChefResponse
)
from app.dependencies import get_openai_client  


# Define a router object
router = APIRouter()

class RecipeSpec(BaseModel):
    specifications: str
    serving_size: Optional[str] = "Family-Size"
    chef_type: Optional[str] = None

# Set the allowed chef types
allowed_chef_types = ["home_cook", "pro_chef", "adventurous_chef", None]


# Define a function to initialize the chatbot with context and an optional recipe
# Create a route to initialize a general chat session
@router.post("/initialize_general_chat", response_description=
            "The thread id for the run to be added to, the session id, and the message content.",
            summary="Initialize a general chat session.",
            tags=["Chat Endpoints"],
            responses={200: {"thread_id": "The thread id for the run to be added to.",
            "session_id" : "The session id.", "message_content" : "The message content."}})
async def initialize_general_chat(context : CreateThreadRequest):
  """ Endpoint to initialize a general chat session. """
  client = get_openai_client()
  session_id = context.session_id
  if context.serving_size:
    message_content = context.message_content + " " + "Serving size: " + context.serving_size
  else:
    message_content = context.message_content

  message_content = "The context for this chat thread is " + message_content
  
  message_thread = client.beta.threads.create(
    messages=[
      {
        "role": "user",
        "content": f"{message_content}",
        "metadata": context.message_metadata  
      },
    ]
  )
  return {"thread_id" : message_thread.id, "session_id" : session_id, "message_content" : message_content}

  
@router.post("/get_chef_response", response_description=
            "The thread id for the run to be added to, the chef response, and the session id.",
            summary="Get a response from the chef to the user's question.",
            tags=["Chat Endpoints"],
            responses={200: {"thread_id": "The thread id for the run to be added to.",
            "chef_response" : "The response from the chef", "session_id" : "The session id."}})
async def get_chef_response(chef_response: GetChefResponse):
  """ Endpoint to get a response from the chatbot to a user's question. """
  client = get_openai_client()
  # Check to make sure that there is a session_id and a thread_id
  if not chef_response.session_id:
    raise ValueError("Session ID is required.")
  # Get the assistant id based on the chef type
  assistant_id = get_assistant_id(chef_response.chef_type)

  if chef_response.serving_size:
    message_content = chef_response.message_content + " " + "Serving size: " + chef_response.serving_size
  else:
    message_content = chef_response.message_content
  if chef_response.thread_id:
    # Create and send the message
    message = client.beta.threads.messages.create(
        chef_response.thread_id,
        content=message_content,
        role="user",
        metadata=chef_response.message_metadata,
    )
    # Log the message
    logging.info(f"Message created: {message}")

    # Create the run
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=chef_response.thread_id
    )
    # Poll the run status
    response = poll_run_status(run_id=run.id, thread_id=run.thread_id)

    return {"chef_response" : response["message"], "thread_id" : chef_response.thread_id, "session_id" : chef_response.session_id}
  
  else:
    run = client.beta.threads.create_and_run(
    assistant_id=assistant_id,
    thread={
      "messages": [
          {
            "role" : "user",
            "content" : message_content, 
            "metadata" : chef_response.message_metadata
      }]}
    )
    # Poll the run status
    response = json.dumps(poll_run_status(run_id=run.id, thread_id=run.thread_id))

    return response

  
  
@router.get("/view_chat_history", response_description="The chat history returned as a dictionary.",
            tags=["Chat Endpoints"])
async def view_chat_history():
    """ Endpoint to view the chat history. """

# ------------------------------------------------------------------------------------------
# Below we define the endpoints for the assistants API calls.  We want to migrate the
# current end point structure to this one ultimately.
@router.post("/create_thread_run",
            summary="Create a thread and run", 
            description='This endpoint creates a new thread and runs it using\
            the provided assistant_id and thread. The run status is then polled\
            and the response is returned.  The response is a JSON object formatted as\
            {"message" : "The message response from the run", "tool_return_values" :\
            "A JSON object containing the tools used and their return values"}')
async def create_thread_run(create_run_request: CreateThreadRunRequest):
  """ Create a thread and run """
  client = get_openai_client()
  if create_run_request.serving_size:
    message_content = create_run_request.message_content + " " + "Serving size: " + create_run_request.serving_size
  else:
    message_content = create_run_request.message_content
  run = client.beta.threads.create_and_run(
  assistant_id=get_assistant_id(create_run_request.chef_type),  
  thread={
    "messages": [
        {
          "role" : "user",
          "content" : message_content, 
          "metadata" : create_run_request.message_metadata
    }]}   
  )
  # Poll the run status
  response = json.dumps(poll_run_status(run_id=run.id, thread_id=run.thread_id))

  return response
  
# Define the endpoint to add a message to the thread and run
@router.post("/add_message_and_run", 
            summary="Add a message to a thread and run", 
            description='This endpoint adds a message to an existing\
            thread and runs it. The message is created with the provided\
            thread_id, role, content, and file_ids. The run status\
            is then polled and the response is returned. The response\
            is a JSON object formatted as\
            {"message" : "The message response from the run", "tool_return_values" :\
            "A JSON object containing the tools used and their return values"}')
async def add_message_and_run(message_request: CreateMessageRunRequest):
    """ Add a message to the thread and run """
    client = get_openai_client()
    # Get the assistant id based on the chef type
    assistant_id = get_assistant_id(message_request.chef_type)

    # Create and send the message
    message = client.beta.threads.messages.create(
        message_request.thread_id,
        content=message_request.message_content,
        role="user",
        metadata=message_request.message_metadata,
    )
    # Log the message
    logging.info(f"Message created: {message}")

    # Create the run
    run = client.beta.threads.runs.create(
        assistant_id=assistant_id,
        thread_id=message_request.thread_id
    )
    # Poll the run status
    response = json.dumps(poll_run_status(run_id=run.id, thread_id=run.thread_id))

    return response

# Define an endpoint allow the user to upload an image file and return extracted text
@router.post("/extract_text_from_image", 
            summary="Extract text from an image", 
            description='This endpoint extracts text from an image.\
            The image is uploaded and the text is extracted using\
            Google Cloud Vision. The extracted text is returned.')
async def extract_text_from_image(files: List[UploadFile] = File(None)):
    """ Extract text from an image """
    # If there are uploaded files, pass them to the upload_files function
    #if files:
    #    file_contents = [await file.read() for file in files]
    # Extract the text from the image
    #extracted_text = await extract_image_text(file_contents)
    # Format the extracted text
    #formatted_text = format_recipe(extracted_text)

    #return formatted_text

# Create upload_files endpoint
@router.post("/upload_files", 
            summary="Upload files", 
            description='This endpoint uploads files to the cloud.\
            The files are uploaded and the file IDs are returned.')
async def upload_assistant_files(files: List[UploadFile] = File(None)):
  """ Upload files to OpenAI and return the file IDs """
  file_contents = [await file.read() for file in files]
  file_ids = await upload_files(file_contents)
  return file_ids

# Create an endpoint to retrieve the run steps from a run
@router.get("/list_run_steps", 
            summary="List the steps from a run", 
            description='This endpoint lists the steps from a run.\
            The steps are returned as a JSON object.')
async def list_run_steps(thread_id: str = None, run_id: str = None, limit: int = 20, order: str = "desc"):
  """ List the steps from a run """
  client = get_openai_client()
  # Check to see if there is a thread_id in the call, if not,
  # load the thread_id from the store
  if not thread_id:
      raise ValueError("Thread ID is required.")
  # Check to see if there is a run_id in the call, if not,
  # load the run_id from the store
  if not run_id:
      raise ValueError("Run ID is required.")
  # Load the steps from redis
  run_steps = client.beta.threads.runs.steps.list(
      thread_id=thread_id,
      run_id=run_id,
      limit=limit,
      order=order
  )
  return run_steps