""" This module contains the ChatMessage class. """
class ChatMessage:
    """ A class to represent a chat message. """
    def __init__(self, content, role):
        self.content = content
        self.role = role
    def format_message(self):
        """ Format the message for the chat history. """
        # Return a dictionary with the format {"role": role, "content": content}
        return {"role": self.role, "content": self.content}
