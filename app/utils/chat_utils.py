""" This module contains helper functions for chat routes. """
from anthropic import HUMAN_PROMPT, AI_PROMPT

def format_claude_prompt(user_prompt):
    """ Format the prompt for the Claude model."""
     # The format for the prompt should be "Human:" \
    # followed by the user's prompt.  Then on a new line,
    # it should say "Assitant:"  followed by blank space.
    # The user prompt can include variables in the form 
    # {{variable_name}}.  As in {{YOUR TEXT HERE}}
    formatted_prompt=f"{HUMAN_PROMPT} {user_prompt} {AI_PROMPT}"
    return formatted_prompt