# services/chat_history_service.py

# Define a class to handle the chat history
class ChatMessageHistory:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })

    def add_user_message(self, content):
        self.add_message("user", content)

    def add_ai_message(self, content):
        self.add_message("ai", content)


