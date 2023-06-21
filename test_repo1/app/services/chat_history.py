# services/chat_history.py

class ChatMessageHistory:
    def __init__(self):
        self.messages = []

    def add_user_message(self, content: str):
        self.add_message("user", content)

    def add_ai_message(self, content: str):
        self.add_message("ai", content)
