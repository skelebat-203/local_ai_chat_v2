"""UI utilities for terminal interface."""

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

COMMANDS_TEXT = f'''
{"=" * 60}
Commands:
Keyboard Navigation 
• UP, DOWN, LEFT, and Right arrow keys - navigate throught the prompt
• ALT + ENTER - Submit a prompt or Save and exit
• ESC + ENTER - Submit a prompt or Save and exit

General
• /status - Show current meta data for chat
• /clear - Clear conversation history
• /swap - Change AI model 
• /pref_streaming - Toggle text streaming on/off
 
Create new
• /s_new [subject_name]- Create a new subject by entering the command followed by the subject name
• /p_new [persona_name] - Create a new persona by entering the command followed by the persona name

View / Update
• /help - List all commands
• /p - List available personas
• /s - List available subjects
• /p_inst - view and optionally update persona instructions
• /s_inst - view and optionally update subject instructions
• /c_history - List all chats across subjects
• /c_history_[subject] - List chats for specific subject
• /c_move - Move a chat to a different subject
 
Delete
• /p_delete [persona_name] - Delete [persona]
• /s_delete [subject_name] - Delete [subject]
• /c_delete [chat_name] - Delete [chat]
{"=" * 60}
'''

WELCOME_TEXT = f'''
{"=" * 60}
Subject-Aware Chat pyWebViewlication (Ollama + Llama3)
{"=" * 60}
Format:
Persona: <name>, Subject: <name>, <prompt>
\t- Load persona and subject, then send prompt
Note: You can chat immediately without setting persona/subject.
• ALT + ENTER - Submit a prompt or Save and exit
• /help - List all commands
'''


def print_welcome():
    """Print welcome message."""
    print(WELCOME_TEXT)


def print_commands():
    """Print available commands."""
    print(COMMANDS_TEXT)


def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_success(message):
    """Print success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print error message."""
    print(f"✗ {message}")


def print_warning(message):
    """Print warning message."""
    print(f"⚠ {message}")

def get_user_input(prompt_text="\nUser:\n"):
    """Get user input with arrow key navigation support."""
    print("(Press Alt+Enter to submit)")
    try:
        user_input = prompt(prompt_text, multiline=True)
        return user_input.strip()
    except KeyboardInterrupt:
        return ""
    except EOFError:
        return "exit"

def get_confirmation(message):
    """Get yes/no confirmation from user."""
    response = input(f"{message} (y/n): ").lower().strip()
    return response == 'y'


def display_chat_history(history):
    """Display formatted chat history."""
    print_section_header("Previous Chat:")
    for msg in history:
        role = msg['role'].capitalize()
        content = msg['content']
        print(f"\n{role}: {content}")
    print("\n" + "=" * 60)
