""" This module defines the chat routes for the API. """
from typing import List, Optional
import logging
import json
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from app.services.run_service import RunService
from app.utils.assistant_utils import poll_run_status, get_assistant_id, upload_files
from app.models.runs import (
  CreateThreadRunRequest, CreateMessageRunRequest
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

@router.post("/get_recipe_chef_response", response_description="""
            The response from the chef as a message object and\
            the chat_history as a list of messages.""",
)
async def get_recipe_chef_response():
    """ Endpoint to get a response from the chef to the user's question about a recipe. """
  
@router.post("/get_chef_response", response_description=
            "The response from the chef as a message object and\
            the chat_history as a list of messages.",
            summary="Get a response from the chef to the user's question.",
            tags=["Chat Endpoints"],
            responses={200: {"description": "OK"}})
async def get_chef_response():
    """ Endpoint to get a response from the chatbot to a user's question. """
   
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