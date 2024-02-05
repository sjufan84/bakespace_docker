from pydantic import Field, BaseModel
from typing import Optional

class ResponseMessage(BaseModel):
    """ A class to represent a chat message. """
    content: str = Field(..., description="The content of the message to be added to the thread.")
    role: str = Field(..., description="The role of the message to be added to the thread.")
    thread_id: Optional[str] = Field(None, description="The thread id for the run to be added to.")
    html: Optional[str] = Field(None, description="The text converted from markdown to html.")
