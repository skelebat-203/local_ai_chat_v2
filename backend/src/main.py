"""Main entry point for the chat application (PyWebView UI only)."""

import sys
from pathlib import Path

import webview  # pywebview

# Base paths
BASE_PATH = Path(__file__).parent          # .../backend/src
ROOT_PATH = BASE_PATH.parent.parent        # .../local_chat_bot
DATA_PATH = ROOT_PATH / "data"
FRONTEND_PATH = ROOT_PATH / "frontend" / "index.html"

# Make src importable
sys.path.insert(0, str(BASE_PATH))

# Shared core
from core.retriever import SubjectRetriever
from core.chat import ChatSession
from core.logger import ChatLogger

# PyWebView
from chatAPI import ChatAPI


def initialize_components():
    retriever = SubjectRetriever(str(DATA_PATH))
    chat = ChatSession(model="llama3")
    logger = ChatLogger(str(DATA_PATH))

    # Load defaults (optional; logs warning if missing)
    try:
        default_system_prompt = retriever.build_system_prompt()
        chat.set_system_prompt(default_system_prompt)
        chat.set_subject_info(retriever.default_persona, retriever.default_subject)
    except Exception as e:
        # Just log to stdout; no terminal helpers needed
        print(f"Could not load defaults: {e}")

    return retriever, chat, logger


def run_pywebview_ui():
    from commands.command_handler import CommandHandler

    retriever, chat, logger = initialize_components()
    command_handler = CommandHandler(retriever, chat, logger)
    api = ChatAPI(chat, command_handler)

    if not FRONTEND_PATH.exists():
        print(f"index.html not found at {FRONTEND_PATH}")
        sys.exit(1)

    webview.create_window(
        title="Local Chat",
        url=str(FRONTEND_PATH),
        width=1000,
        height=780,
        resizable=True,
        js_api=api,
    )

    webview.start(debug=True)


if __name__ == "__main__":
    run_pywebview_ui()
