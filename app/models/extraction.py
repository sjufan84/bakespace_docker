""" The extraction model class. """
from pydantic import BaseModel, Field

class ExtractedTextResponse(BaseModel):
    """ Define the ExtractedTextResponse model. """
    text: str = Field(description="The extracted text.")
    status: str = Field(description="The status of the extraction.")