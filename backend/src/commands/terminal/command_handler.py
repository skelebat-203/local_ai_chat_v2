"""Central command handler and router."""

from commands.terminal.chat_commands import (
    handle_chat_history, handle_chat_history_by_subject,
    handle_clear_history, handle_status, handle_streaming_toggle,
    handle_exit, handle_delete_chat, handle_chat_move,
)
from commands.terminal.subject_commands import (
    handle_list_personas, handle_list_subjects,
    handle_new_subject, handle_new_persona,
    handle_persona_subject_switch, handle_view_subject,
    handle_view_persona,handle_delete_persona,
    handle_delete_subject
) 
from utils.ui import print_commands

class CommandHandler:
    """Handles routing and execution of user commands."""

    def __init__(self, retriever, chat, logger):
        self.retriever = retriever
        self.chat = chat
        self.logger = logger
        self.text_streaming = True

    def handle_command(self, user_input):
        """
        Route and handle user commands.

        Returns:
            tuple: (should_exit, modified_input)
            - should_exit: True if user wants to exit
            - modified_input: Modified input (e.g., extracted prompt after persona/subject switch)
        """
        cmd = user_input.lower()

        # Exit command
        if cmd == "/exit":
            return handle_exit(self.chat, self.logger), None

        # Help command
        if cmd == "/help":
            print_commands()
            return False, None

        # Streaming toggle
        if cmd == "/pref_streaming":
            self.text_streaming = handle_streaming_toggle(self.text_streaming)
            return False, None

        # List commands
        if cmd == "/p":
            handle_list_personas(self.retriever)
            return False, None

        if cmd == "/s":
            handle_list_subjects(self.retriever)
            return False, None

        # View and update commands
        if cmd == "/s_inst":
            handle_view_subject(self.retriever, self.chat)
            return False, None

        if cmd == "/p_inst":
            handle_view_persona(self.retriever, self.chat)
            return False, None

        # Status command
        if cmd == "/status":
            handle_status(self.chat, self.text_streaming)
            return False, None

        # Clear history
        if cmd == "/clear":
            handle_clear_history(self.chat)
            return False, None

        # Chat history commands
        if cmd == "/c_history":
            handle_chat_history(self.retriever, self.chat)
            return False, None

        if cmd.startswith("/c_history_"):
            subject_name = user_input[14:].strip()
            handle_chat_history_by_subject(self.retriever, self.chat, subject_name)
            return False, None

        # New subject command
        if cmd.startswith("/s_new"):
            parts = user_input.split(maxsplit=1)
            subject_name = parts[1].strip() if len(parts) > 1 else ""
            handle_new_subject(self.retriever, self.chat, subject_name)
            return False, None

        # New persona command
        if cmd.startswith("/p_new"):
            parts = user_input.split(maxsplit=1)
            persona_name = parts[1].strip() if len(parts) > 1 else ""
            handle_new_persona(self.retriever, self.chat, persona_name)
            return False, None

        # Check for persona/subject switch
        prompt = handle_persona_subject_switch(self.retriever, self.chat, user_input)
        if prompt is not None:
            return False, prompt if prompt else None
        
        # Delete persona command
        if cmd.startswith("/p_delete"):
            parts = user_input.split(maxsplit=1)
            persona_name = parts[1].strip() if len(parts) > 1 else ""
            handle_delete_persona(self.retriever, self.chat, persona_name)
            return False, None

        # Delete subject command
        if cmd.startswith("/s_delete"):
            parts = user_input.split(maxsplit=1)
            subject_name = parts[1].strip() if len(parts) > 1 else ""
            handle_delete_subject(self.retriever, self.chat, subject_name)
            return False, None

        # Delete chat command
        if cmd.startswith("/c_delete"):
            parts = user_input.split(maxsplit=1)
            idx = parts[1].strip() if len(parts) > 1 else ""
            handle_delete_chat(self.retriever, self.chat, idx)
            return False, None

        if cmd.startswith("/c_move"):
            # No extra parsing needed; handler does interactive flow
            handle_chat_move(self.retriever, self.chat, None)
            return False, None
 
        if cmd.startswith("/swap"):
            # formats:
            #   /swap           -> toggle llama3 <-> qwen2.5-coder
            #   /swap llama3    -> set explicitly
            #   /swap qwen      -> set explicitly (short alias)

            parts = user_input.split(maxsplit=1)
            if len(parts) == 1:
                # toggle
                current = self.chat.model
                if current == "llama3":
                    new_model = "qwen2.5-coder:32b"
                else:
                    new_model = "llama3"
            else:
                # explicit target
                target = parts[1].strip().lower()
                if target in ("llama3", "llama"):
                    new_model = "llama3"
                elif target in ("qwen2.5-coder", "qwen"):
                    new_model = "qwen2.5-coder"
                else:
                    print("Unknown model. Use: llama3 or qwen2.5-coder.")
                    return False, None

            self.chat.set_model(new_model)
            # optional: clear history when swpyWebViewing models
            # self.chat.clear_history()

            return False, None

        # Not a command, return original input
        return False, user_input
