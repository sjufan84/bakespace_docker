# services/chat_history_service.py

# Define a class to handle the chat history
class ChatMessageHistory:
    """ A class to represent the chat history."""
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        """ Add a message to the chat history. """
        self.messages.append({
            "role": role,
            "content": content
        })

    def add_user_message(self, content):
        """ Add a message from the user to the chat history. """
        self.add_message("user", content)

    def add_ai_message(self, content):
        """ Add a message from the AI to the chat history. """
        self.add_message("ai", content)


