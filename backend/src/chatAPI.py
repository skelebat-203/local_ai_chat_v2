"""API surface for the PyWebView frontend."""

from core.chat import ChatSession
from commands.command_handler import CommandHandler

class ChatAPI:
    def __init__(self, chat_session: ChatSession, command_handler: CommandHandler) -> None:
        self.chat = chat_session
        self.command_handler = command_handler

    def send_message(self, text: str) -> dict:
        """Called from JS: window.pywebview.api.send_message(text)."""
        should_exit, modified = self.command_handler.handle_command(text)
        if should_exit:
            return {"reply": "Goodbye.", "history": self._format_history()}

        user_input = modified or text

        try:
            reply = self.chat.send_message(user_input)
        except Exception as e:
            reply = f"Error from backend: {e}"

        history = self._format_history()
        return {"reply": reply, "history": history}

    def _format_history(self) -> list[dict]:
        formatted: list[dict] = []
        for msg in getattr(self.chat, "history", []):
            role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "assistant")
            content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
            formatted.append({"role": role, "content": content})
        return formatted
