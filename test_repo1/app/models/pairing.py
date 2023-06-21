# Create a model for the Pairing class
from pydantic import BaseModel

# The pairing should have the following attributes:
#    - pairing_type: str
#    - pairing_text: str

class Pairing(BaseModel):
    pairing_type: str
    pairing_text: str
