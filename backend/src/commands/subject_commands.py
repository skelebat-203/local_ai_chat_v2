"""Subject and persona management command handlers."""

def handle_list_personas(retriever):
    """Handle /p command."""
    personas = retriever.list_personas()
    print(f"Available personas: {', '.join(personas)}")

def handle_list_subjects(retriever):
    """Handle /s command."""
    subjects = retriever.list_subjects()
    print(f"Available subjects: {', '.join(subjects)}")


def handle_view_subject(retriever, chat):
    """Handle /view_subject command - view and optionally update subject instructions."""
    current_subject = chat.current_subject or retriever.default_subject

    print(f"\n=== Subject: {current_subject} ===\n")

    try:
        # Load current instructions
        instructions = retriever.load_subject_instructions(current_subject)
        print("Current Instructions:")
        print("-" * 50)
        print(instructions)
        print("-" * 50)

        # Ask if user wants to update
        if get_confirmation("\nDo you want to update these instructions?"):
            print("\nEnter new instructions (press Enter when done):\n")
            new_instructions = get_user_input("> ")

            if new_instructions:
                success = retriever.update_subject_instructions(current_subject, new_instructions)
                if success:
                    print_success("Subject instructions updated successfully.")

                    # Rebuild system prompt with new instructions
                    current_persona = chat.current_persona or retriever.default_persona
                    system_prompt = retriever.build_system_prompt(current_persona, current_subject)
                    chat.set_system_prompt(system_prompt)
                    print_success("System prompt updated with new instructions.")
                else:
                    print_error("Failed to update subject instructions.")
            else:
                print_warning("No instructions provided. Update cancelled.")

    except FileNotFoundError as e:
        print_error(f"Error: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")


def handle_view_persona(retriever, chat):
    """Handle /view_persona command - view and optionally update persona instructions."""
    current_persona = chat.current_persona or retriever.default_persona
    is_default = current_persona.lower() == retriever.default_persona.lower()

    print(f"\n=== Persona: {current_persona} ===\n")

    try:
        # Load current persona instructions
        persona_instructions = retriever.load_persona(current_persona)
        print("Current Instructions:")
        print("-" * 50)
        print(persona_instructions)
        print("-" * 50)

        # Only allow editing if not default persona
        if is_default:
            print("\n⚠ Default persona cannot be updated.")
        else:
            # Ask if user wants to update
            if get_confirmation("\nDo you want to update these instructions?"):
                print("\nEnter new instructions (press Enter when done):\n")
                new_instructions = get_user_input("> ")

                if new_instructions:
                    success = retriever.update_persona_instructions(current_persona, new_instructions)
                    if success:
                        print_success("Persona instructions updated successfully.")

                        # Rebuild system prompt with new instructions
                        current_subject = chat.current_subject or retriever.default_subject
                        system_prompt = retriever.build_system_prompt(current_persona, current_subject)
                        chat.set_system_prompt(system_prompt)
                        print_success("System prompt updated with new instructions.")
                    else:
                        print_error("Failed to update persona instructions.")
                else:
                    print_warning("No instructions provided. Update cancelled.")

    except FileNotFoundError as e:
        print_error(f"Error: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")


def handle_new_subject(retriever, chat, subject_name):
    """Handle /s_new command."""
    if not subject_name:
        print_error("Usage: /s_new [subject_name]")
        return False

    try:
        subject_created = retriever.create_subject_folder(subject_name)
        if subject_created:
            print_success(f"'{subject_name}' created.")

            if get_confirmation("Do you want to add subject instructions?"):
                print("\nThe next prompt will be saved as instructions for this subject.")
                print("Enter your instructions (press Enter when done):\n")

                instructions = get_user_input("> ")

                if instructions:
                    retriever.save_subject_instructions(subject_name, instructions)
                    print_success("Instructions saved.")
                else:
                    print_warning("No instructions provided.")

                print(f"\nWhat is your first prompt for '{subject_name}'?")
            else:
                print(f"\nWhat is your first prompt for '{subject_name}'?")

            system_prompt = retriever.build_system_prompt(retriever.default_persona, subject_name)
            chat.set_system_prompt(system_prompt)
            chat.set_subject_info(retriever.default_persona, subject_name)
            chat.clear_history()
            print_success(f"Loaded Subject: {subject_name}")
            return True
        else:
            print_error(f"Subject '{subject_name}' already exists.")
            return False

    except Exception as e:
        print_error(f"Error creating subject: {e}")
        return False


def handle_new_persona(retriever, chat, persona_name):
    """Handle /p_new command."""
    if not persona_name:
        print("Usage: /p_new [persona_name]")
        return False

    if not persona_name.replace('_', '').replace('-', '').isalnum():
        print_error("Persona name must be alphanumeric (underscores and hyphens allowed)")
        return False

    persona_file = retriever.personas_path / f"{persona_name.lower()}.md"
    if persona_file.exists():
        print_error(f"Persona '{persona_name}' already exists")
        return False

    try:
        retriever.personas_path.mkdir(parents=True, exist_ok=True)
        print(f"{persona_name} created.")
        print("The next prompt will be saved as instructions for this persona.")

        persona_description = get_user_input("\n> ")

        if not persona_description:
            print_error("Persona description cannot be empty")
            return False

        with open(persona_file, 'w', encoding='utf-8') as f:
            f.write(persona_description)

        print("\nPersona description saved.")

        current_subject = chat.current_subject or retriever.default_subject
        system_prompt = retriever.build_system_prompt(persona_name, current_subject)
        chat.set_system_prompt(system_prompt)
        chat.set_subject_info(persona_name, current_subject)
        chat.clear_history()

        print_success(f"Loaded Persona: {persona_name}")
        print(f"What is your first prompt for {persona_name}?")
        return True

    except Exception as e:
        print_error(f"Error creating persona: {e}")
        return False


def handle_persona_subject_switch(retriever, chat, user_input):
    """
    Handle persona/subject switching via flexible formats, for example:
      - "Persona: X"
      - "Subject: Y"
      - "Persona: X, Subject: Y"
      - "Persona: X, Subject: Y, prompt"
      - "Subject: Y, Persona: X, prompt"

    Returns:
        None      -> if no persona/subject keywords found (treat as normal input)
        ""        -> if it was a meta-only line (switch only, no prompt to send)
        <prompt>  -> if there is remaining prompt text after switching
    """
    persona, subject, prompt, is_meta_only = retriever.parse_subject_command(user_input)

    # If neither persona nor subject was found, this is not a switch command
    if persona is None and subject is None:
        return None

    try:
        # Determine the target persona and subject, falling back to current/default
        current_persona = chat.current_persona or retriever.default_persona
        current_subject = chat.current_subject or retriever.default_subject

        target_persona = persona if persona is not None else current_persona
        target_subject = subject if subject is not None else current_subject

        # Validate persona file (if not default/found, fall back with warning)
        actual_persona = target_persona
        persona_file = retriever.personas_path / f"{target_persona.lower()}.md"
        if not persona_file.exists():
            print_warning(f"Persona '{target_persona}' not found, using default")
            print(f"\t- You can use '/p_new {target_persona}' to create a new persona")
            actual_persona = retriever.default_persona

        # Validate subject folder (if not found, fall back with warning)
        actual_subject = target_subject
        subject_folder = retriever.subjects_path / target_subject
        if not subject_folder.exists():
            print_warning(f"Subject '{target_subject}' not found, using default")
            print(f"\t- You can use '/s_new {target_subject}' to create a new subject")
            actual_subject = retriever.default_subject

        # Build new system prompt and update chat session
        system_prompt = retriever.build_system_prompt(actual_persona, actual_subject)
        chat.set_system_prompt(system_prompt)
        chat.set_subject_info(actual_persona, actual_subject)
        chat.clear_history()

        print_success(f"Loaded Persona: {actual_persona}")
        print_success(f"Loaded Subject: {actual_subject}")

        # Item 3: meta vs "switch + prompt"
        if is_meta_only:
            # Just switch persona/subject; no prompt to send
            return ""
        else:
            # Switch and then treat remaining text as the user's prompt
            return prompt if prompt else ""

    except FileNotFoundError as e:
        print_error(f"Error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None

def handle_delete_persona(retriever, chat, persona_name: str) -> bool:
    """Handle deletepersona command."""
    if not persona_name:
        print_error("Usage: deletepersona persona_name")
        return False

    currentpersona = (chat.current_persona or retriever.default_persona).lower()
    if persona_name.lower() == retriever.default_persona.lower():
        print_error("Default persona cannot be deleted.")
        return False

    if persona_name.lower() == currentpersona:
        printwarning("You are deleting the currently loaded persona.")

    if not get_confirmation(f"Are you sure you want to delete persona '{persona_name}'?"):
        printwarning("Delete persona cancelled.")
        return False

    success = retriever.delete_persona(persona_name)
    if success:
        print_success(f"Persona '{persona_name}' deleted.")
        # If we just deleted the current persona, fall back to default
        if persona_name.lower() == currentpersona:
            systemprompt = retriever.buildsystemprompt(
                retriever.default_persona,
                chat.current_subject or retriever.default_subject,
            )
            chat.setsystemprompt(systemprompt)
            chat.setsubjectinfo(retriever.default_persona,
                                chat.current_subject or retriever.default_subject)
            chat.clearhistory()
            print_success("Reverted to default persona.")
    else:
        print_error(f"Failed to delete persona '{persona_name}'.")
    return success


def handle_delete_subject(retriever, chat, subject_name: str) -> bool:
    """Handle deletesubject command."""
    if not subject_name:
        print_error("Usage: deletesubject subject_name")
        return False

    currentsubject = chat.current_subject or retriever.default_subject
    if subject_name == retriever.default_subject:
        print_error("Default subject cannot be deleted.")
        return False

    if subject_name == currentsubject:
        printwarning("You are deleting the currently loaded subject and its chats.")

    if not get_confirmation(
        f"Are you sure you want to delete subject '{subject_name}' and all its chats?"
    ):
        printwarning("Delete subject cancelled.")
        return False

    success = retriever.delete_subject(subject_name)
    if success:
        print_success(f"Subject '{subject_name}' deleted.")
        # If we just deleted the current subject, fall back to default
        if subject_name == currentsubject:
            systemprompt = retriever.buildsystemprompt(
                chat.current_persona or retriever.default_persona,
                retriever.default_subject,
            )
            chat.setsystemprompt(systemprompt)
            chat.setsubjectinfo(chat.current_persona or retriever.default_persona,
                                retriever.default_subject)
            chat.clearhistory()
            print_success("Reverted to default subject.")
    else:
        print_error(f"Failed to delete subject '{subject_name}'.")
    return success
