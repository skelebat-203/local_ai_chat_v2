"""Chat-related command handlers."""

from pathlib import Path

def handle_chat_history(retriever, chat):
    """Handle /c_history command - view all chats."""
    all_chats = retriever.list_all_chats()
    if not all_chats:
        print("No chat history found.")
        return None

    print_section_header("All Chat History")
    for idx, chat_info in enumerate(all_chats, 1):
        subject, filename, file_path = chat_info
        print(f"{idx}. [{subject}] {filename}")
    print("=" * 60)

    try:
        selection = get_user_input("\nEnter number to open chat (or press Enter to cancel): ")
        if not selection:
            return None

        chat_idx = int(selection) - 1
        if 0 <= chat_idx < len(all_chats):
            subject, filename, file_path = all_chats[chat_idx]
            return _load_chat_file(retriever, chat, file_path, subject, filename)
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input.")
        return None


def handle_chat_history_by_subject(retriever, chat, subject_name):
    """Handle /c_history_[subject] command - view chats for specific subject."""
    if not subject_name:
        print("Please specify a subject: /c_history_[subject]")
        return None

    chats = retriever.list_chats_by_subject(subject_name)
    if not chats:
        print(f"No chat history found for subject '{subject_name}'.")
        return None

    print_section_header(f"Chat History for: {subject_name}")
    for idx, chat_info in enumerate(chats, 1):
        filename, file_path = chat_info
        print(f"{idx}. {filename}")
    print("=" * 60)

    try:
        selection = get_user_input("\nEnter number to open chat (or press Enter to cancel): ")
        if not selection:
            return None

        chat_idx = int(selection) - 1
        if 0 <= chat_idx < len(chats):
            filename, file_path = chats[chat_idx]
            return _load_chat_file(retriever, chat, file_path, subject_name, filename)
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input.")
        return None


def _load_chat_file(retriever, chat, file_path, subject_name, filename):
    """Helper function to load a chat file."""
    loaded_history = retriever.load_chat_file(file_path)
    chat.load_history(loaded_history)

    system_prompt = retriever.build_system_prompt(retriever.default_persona, subject_name)
    chat.set_system_prompt(system_prompt)
    chat.set_subject_info(retriever.default_persona, subject_name)

    print_success(f"Loaded chat from {filename}")
    print_success(f"Subject: {subject_name}")
    print_success("You can now continue this conversation")

    display_chat_history(loaded_history)

    chat.original_chat_file = file_path
    return True


def handle_clear_history(chat):
    """Handle /clear command."""
    chat.clear_history()
    print_success("Conversation history cleared")


def handle_status(chat, text_streaming):
    """Handle /status command."""
    persona = chat.current_persona or "None"
    subject = chat.current_subject or "None"
    streaming_status = "on" if text_streaming else "off"
    print(f"Persona: {persona}")
    print(f"Current Subject: {subject}")
    print(f"Model: {chat.model}")
    print(f"Text Streaming: {streaming_status}")


def handle_streaming_toggle(text_streaming):
    """Handle /pref_streaming command."""
    current_state = "on" if text_streaming else "off"
    target_state = "off" if text_streaming else "on"

    response = get_user_input(f"Turn text streaming {target_state}? 'y' / 'n'? ").lower()

    if response == 'y':
        text_streaming = not text_streaming
        new_state = "on" if text_streaming else "off"
        print(f"Text streaming is now {new_state}. What would you like to discuss?")
    elif response == 'n':
        print("No change. What would you like to discuss?")
    else:
        print("Invalid response. No change made.")

    return text_streaming


def handle_exit(chat, logger):
    """Handle /exit command."""
    if chat.current_subject and chat.conversation_history:
        from utils.ui import get_confirmation, print_success
        
        if get_confirmation(f"Save chat to '{chat.current_subject}'?"):
            log_file = logger.save_chat(chat.current_subject, chat.conversation_history)
            print_success(f"Chat saved to {log_file}")

            if hasattr(chat, 'original_chat_file') and chat.original_chat_file.exists():
                chat.original_chat_file.unlink()
                print_success(f"Removed old chat file: {chat.original_chat_file.name}")
    
    print("Goodbye!")
    return True

def handle_delete_chat(retriever, chat, arg: str | None) -> bool:
    """
    deletechat            -> list all chats and prompt for index to delete
    deletechat 5          -> delete chat #5 from the all-chats list
    """
    all_chats = retriever.list_all_chats()
    if not all_chats:
        printwarning("No chats found.")
        return False

    # Show numbered list similar to your chathistory output
    for idx, (subject, filename, path) in enumerate(all_chats, start=1):
        print(f"{idx}. {filename} [{subject}]")

    if arg:
        try:
            choice = int(arg)
        except ValueError:
            print_error("deletechat expects a numeric index.")
            return False
    else:
        choice_str = get_user_input("Enter the number of the chat to delete: ")
        try:
            choice = int(choice_str)
        except ValueError:
            print_error("Invalid number.")
            return False

    if choice < 1 or choice > len(all_chats):
        print_error("Index out of range.")
        return False

    subject_name, chat_filename, path = all_chats[choice - 1]

    if not get_confirmation(
        f"Delete chat '{chat_filename}' in subject '{subject_name}'?"
    ):
        printwarning("Delete chat cancelled.")
        return False

    success = retriever.delete_chat_file(subject_name, chat_filename)
    if success:
        print_success("Chat deleted.")
        # If this was the currently loaded chat, you might also clear in‑memory history
        # chat.clearhistory()
    else:
        print_error("Failed to delete chat.")
    return success

def handle_chat_move(retriever, chat, arg: str | None) -> bool:
    """
    Handle /c_move command.

    Flow:
    1. Show numbered list of all chats: [subject] [chat_title]
    2. Prompt: "Enter the number of the chat to move or 'n' to exit: "
    3. On valid selection, show subjects list and prompt:
       "Enter the number of the subject to move to or 'n' to exit: "
    4. Perform move and inform user.
    """
    # 1. Get all chats
    all_chats = retriever.list_all_chats()
    if not all_chats:
        printwarning("No chats found.")
        return False

    print_section_header("Move Chat to Another Subject")

    # Display numbered list: [subject] [chat_title]
    # list_all_chats returns (subject, filename, filepath)
    for idx, (subject, filename, _path) in enumerate(all_chats, start=1):
        # For now, treat filename as the "title" (you can later swap in a parsed title)
        print(f"{idx}. [{subject}] {filename}")

    # 2. Ask which chat to move
    while True:
        choice_str = get_user_input("Enter the number of the chat to move or 'n' to exit: ")
        if choice_str.lower() == "n":
            # Exit and allow normal prompting
            return False

        try:
            choice = int(choice_str)
        except ValueError:
            printerror("Invalid number.")
            continue

        if choice < 1 or choice > len(all_chats):
            printerror("Invalid number.")
            continue

        # Valid chat selected
        source_subject, chat_filename, chat_path = all_chats[choice - 1]
        break

    # 3. Show available subjects
    subjects = retriever.list_subjects()
    if not subjects:
        printwarning("No subjects available to move into.")
        return False

    print_section_header("Available Subjects")
    for idx, subject in enumerate(subjects, start=1):
        print(f"{idx}. {subject}")

    # Ask which subject to move into
    while True:
        subject_choice_str = get_user_input("Enter the number of the subject to move to or 'n' to exit: ")
        if subject_choice_str.lower() == "n":
            return False

        try:
            subject_choice = int(subject_choice_str)
        except ValueError:
            printerror("Invalid number.")
            continue

        if subject_choice < 1 or subject_choice > len(subjects):
            printerror("Invalid number.")
            continue

        target_subject = subjects[subject_choice - 1]
        break

    # 4. Perform the move
    success = retriever.move_chat_to_subject(source_subject, chat_filename, target_subject)
    if success:
        printsuccess(f"{chat_filename} moved to {target_subject}")
        return True
    else:
        printerror("Failed to move chat.")
        return False
