"""Main entry point for the chat pyWebViewlication (terminal or pyWebView UI)."""
 
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

# Terminal UI helpers
from utils.ui import (
    print_welcome,
    get_user_input,
    print_warning,
)

# PyWebView
from chatAPI import ChatAPI


# ---------- Shared initialization ----------

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
        print(f"Could not load defaults: {e}")

    return retriever, chat, logger


# ---------- Terminal mode ----------

def run_terminal_ui():
    # Terminal-specific command handler
    from commands.terminal.command_handler import CommandHandler

    retriever, chat, logger = initialize_components()
    command_handler = CommandHandler(retriever, chat, logger)

    print_welcome()

    while True:
        try:
            user_input = get_user_input()
            if not user_input:
                continue

            should_exit, modified_input = command_handler.handle_command(user_input)
            if should_exit:
                break

            if modified_input:
                # Non-streaming: send message and print reply
                reply = chat.send_message(modified_input)
                print(f"\nAssistant:\n{reply}\n")

        except KeyboardInterrupt:
            print_warning("Use /exit to save and quit.")
        except Exception as e:
            print_warning(f"Error: {e}")

# ---------- PyWebView mode ----------

def run_pyWebView_ui():
    # pyWebView-specific command handler
    from commands.pyWebView.command_handler import CommandHandler

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


# ---------- Launcher ----------

if __name__ == "__main__":
    print("Select interface:")
    print("1) Terminal")
    print("2) pyWebView (PyWebview)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        run_terminal_ui()
    elif choice == "2":
        run_pyWebView_ui()
    else:
        print("Invalid choice. Exiting.")
