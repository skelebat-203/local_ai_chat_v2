import os
from pathlib import Path

class SubjectRetriever:
    def __init__(self, basepath="."):
        self.basepath = Path(basepath)
        self.personas_path = self.basepath / "personas"
        self.subjects_path = self.basepath / "subjects"
        self.default_persona = "default"
        self.default_subject = "no_subject"

    def load_persona(self, persona_name=None):
        """Load persona instructions from personas folder, defaults to default.md"""
        if persona_name is None:
            persona_name = self.default_persona

        persona_file = self.personas_path / f"{persona_name.lower()}.md"
        if persona_file.exists():
            with open(persona_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Try to load default persona if requested persona doesn't exist
            if persona_name != self.default_persona:
                default_file = self.personas_path / f"{self.default_persona}.md"
                if default_file.exists():
                    print(f"⚠ Persona '{persona_name}' not found, using default")
                    with open(default_file, 'r', encoding='utf-8') as f:
                        return f.read()
            raise FileNotFoundError(f"Persona '{persona_name}' not found at {persona_file}")

    def load_subject_instructions(self, subject_name=None):
        """Load instructions.md from specific subject folder, defaults to no_subject"""
        if subject_name is None:
            subject_name = self.default_subject

        instructions_file = self.subjects_path / subject_name / "instructions.md"
        if instructions_file.exists():
            with open(instructions_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Try to load default subject if requested subject doesn't exist
            if subject_name != self.default_subject:
                default_file = self.subjects_path / self.default_subject / "instructions.md"
                if default_file.exists():
                    print(f"⚠ Subject '{subject_name}' not found, using default")
                    with open(default_file, 'r', encoding='utf-8') as f:
                        return f.read()
            raise FileNotFoundError(f"Instructions for subject '{subject_name}' not found at {instructions_file}")

    def update_persona_instructions(self, persona_name, new_instructions):
        """
        Update instructions for an existing persona.

        Args:
            persona_name: Name of the persona to update
            new_instructions: New instructions text

        Returns:
            bool: True if successful, False otherwise
        """
        persona_file = self.personas_path / f"{persona_name.lower()}.md"

        if not persona_file.exists():
            return False

        try:
            with open(persona_file, 'w', encoding='utf-8') as f:
                f.write(new_instructions)
            return True
        except Exception as e:
            print(f"Error updating persona: {e}")
            return False

    def update_subject_instructions(self, subject_name, new_instructions):
        """
        Update instructions for an existing subject.

        Args:
            subject_name: Name of the subject to update
            new_instructions: New instructions text

        Returns:
            bool: True if successful, False otherwise
        """
        instructions_file = self.subjects_path / subject_name / "instructions.md"

        if not instructions_file.exists():
            return False

        try:
            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write(new_instructions)
            return True
        except Exception as e:
            print(f"Error updating subject instructions: {e}")
            return False

    def load_chat_logs(self, subject_name):
        """Load all chat logs from subject folder"""
        subject_folder = self.subjects_path / subject_name
        chat_logs = []

        if subject_folder.exists():
            chatlog_file = subject_folder / "chatlog.md"
            if chatlog_file.exists():
                with open(chatlog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        chat_logs.append(content)

            for file in sorted(subject_folder.glob("chat_*.md")):
                if file.name != "chatlog.md":
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            chat_logs.append(content)

        return "\n---\n".join(chat_logs) if chat_logs else ""

    def build_system_prompt(self, persona_name=None, subject_name=None):
        """Build complete system prompt with persona and subject"""
        persona = self.load_persona(persona_name)
        instructions = self.load_subject_instructions(subject_name)

        # Only load chat history if subject is explicitly provided
        chat_history = ""
        if subject_name and subject_name != self.default_subject:
            chat_history = self.load_chat_logs(subject_name)

        system_prompt = f"""# Persona
{persona}

# Subject Instructions
{instructions}"""

        if chat_history:
            system_prompt += f"""

# Previous Chat History
{chat_history}"""

        return system_prompt

    def parse_subject_command(self, user_input):
        """
        Parse commands like:
          - "Persona: writer"
          - "Subject: Fantasy story"
          - "Persona: writer, Subject: Fantasy story"
          - "Persona: writer, Subject: Fantasy story, prompt"
          - "Subject: Fantasy story, Persona: writer, prompt"

        Returns:
            (persona, subject, prompt, is_meta_only)

        persona: extracted persona name or None
        subject: extracted subject name or None
        prompt:  remaining text after persona/subject declarations (may be "")
        is_meta_only: True if line only contains persona/subject declarations
                      (no extra prompt text)
        """
        text = user_input.strip()
        lower_text = text.lower()

        # Quick check: if neither keyword is present, treat as normal prompt
        if "persona" not in lower_text and "subject" not in lower_text:
            return None, None, text, False

        persona = None
        subject = None
        prompt_parts = []

        # Split by comma to support:
        # "Persona: X, Subject: Y, rest of prompt"
        parts = text.split(',')

        for part in parts:
            raw = part.strip()
            lower = raw.lower()

            if lower.startswith("persona"):
                # Everything after the first ':' is the persona name
                if ':' in raw:
                    persona_value = raw.split(':', 1)[1].strip()
                    if persona_value:
                        persona = persona_value
            elif lower.startswith("subject"):
                # Everything after the first ':' is the subject name
                if ':' in raw:
                    subject_value = raw.split(':', 1)[1].strip()
                    if subject_value:
                        subject = subject_value
            else:
                # Any segment that is not a persona/subject declaration is part of the prompt
                if raw:
                    prompt_parts.append(raw)

        prompt = ', '.join(prompt_parts).strip()

        # Meta‑only if we found at least a persona or subject
        # and there is no extra prompt text
        is_meta_only = (persona is not None or subject is not None) and (prompt == "")

        return persona, subject, prompt, is_meta_only

    def list_personas(self):
        """List all available personas"""
        if self.personas_path.exists():
            return [f.stem for f in self.personas_path.glob("*.md")]
        return []

    def list_subjects(self):
        """List all available subjects"""
        if self.subjects_path.exists():
            return [d.name for d in self.subjects_path.iterdir() if d.is_dir()]
        return []

    def list_all_chats(self):
        """List all chat files across all subjects with timestamps
        Returns: list of tuples (subject_name, chat_filename, file_path)
        """
        all_chats = []
        if self.subjects_path.exists():
            for subject_dir in self.subjects_path.iterdir():
                if subject_dir.is_dir():
                    for chat_file in sorted(subject_dir.glob("chat_*.md")):
                        all_chats.append((subject_dir.name, chat_file.name, chat_file))
        # Sort by timestamp (filename contains timestamp)
        all_chats.sort(key=lambda x: x[1])
        return all_chats

    def list_chats_by_subject(self, subject_name):
        """List all chat files in a specific subject folder
        Returns: list of tuples (chat_filename, file_path)
        """
        chats = []
        subject_folder = self.subjects_path / subject_name
        if subject_folder.exists():
            for chat_file in sorted(subject_folder.glob("chat_*.md")):
                chats.append((chat_file.name, chat_file))
        # Sort by timestamp
        chats.sort(key=lambda x: x[0])
        return chats

    def load_chat_file(self, chat_file_path):
        """Load a specific chat file and parse it into conversation history
        Returns: list of message dictionaries
        """
        conversation_history = []

        try:
            with open(chat_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading chat file: {e}")
            return []

        # Parse the markdown format back into conversation history
        lines = content.split('\n')
        current_role = None
        current_content = []

        for line in lines:
            # Check for both formats: **User:** and **user:**
            if line.strip().lower().startswith('**user:**'):
                if current_role and current_content:
                    conversation_history.append({
                        "role": current_role,
                        "content": '\n'.join(current_content).strip()
                    })
                current_role = "user"
                current_content = []
            elif line.strip().lower().startswith('**assistant:**'):
                if current_role and current_content:
                    conversation_history.append({
                        "role": current_role,
                        "content": '\n'.join(current_content).strip()
                    })
                current_role = "assistant"
                current_content = []
            elif current_role is not None:
                # Only add content if we've identified a role
                current_content.append(line)

        # Add the last message
        if current_role and current_content:
            conversation_history.append({
                "role": current_role,
                "content": '\n'.join(current_content).strip()
            })

        # Debug: print what was loaded
        print(f"Loaded {len(conversation_history)} messages from chat file")

        # Ensure we always return a list, even if empty
        return conversation_history if conversation_history else []

    def create_subject_folder(self, subject_name):
        """
        Create a new subject folder.

        Args:
            subject_name: Name of the subject folder to create

        Returns:
            bool: True if created, False if already exists
        """
        subject_path = self.subjects_path / subject_name

        # Check if subject already exists
        if subject_path.exists():
            return False

        # Create the subject folder
        subject_path.mkdir(parents=True, exist_ok=True)
        return True

    def save_subject_instructions(self, subject_name, instructions):
        """
        Save instructions for a subject.

        Args:
            subject_name: Name of the subject
            instructions: Instructions text to save
        """
        subject_path = self.subjects_path / subject_name

        # Ensure subject folder exists
        if not subject_path.exists():
            subject_path.mkdir(parents=True, exist_ok=True)

        # Save instructions.md file
        instructions_file = subject_path / "instructions.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(f"# {subject_name} Instructions\n\n")
            f.write(instructions)

        return instructions_file
    # in SubjectRetriever

    def delete_persona(self, persona_name: str) -> bool:
        """Delete a persona .md file (cannot delete default)."""
        persona_name = persona_name.lower()
        if persona_name == self.default_persona.lower():
            print("Default persona cannot be deleted.")
            return False

        persona_file = self.personas_path / f"{persona_name}.md"
        if not persona_file.exists():
            print(f"Persona '{persona_name}' not found.")
            return False

        try:
            persona_file.unlink()
            return True
        except Exception as e:
            print(f"Error deleting persona: {e}")
            return False

    def delete_subject(self, subject_name: str) -> bool:
        """Delete an entire subject folder, including chatlogs."""
        if subject_name == self.default_subject:
            print("Default subject cannot be deleted.")
            return False

        subject_path = self.subjects_path / subject_name
        if not subject_path.exists():
            print(f"Subject '{subject_name}' not found.")
            return False

        try:
            # Delete all files and subfolders
            for root, dirs, files in os.walk(subject_path, topdown=False):
                root_path = Path(root)
                for f in files:
                    (root_path / f).unlink()
                for d in dirs:
                    (root_path / d).rmdir()
            subject_path.rmdir()
            return True
        except Exception as e:
            print(f"Error deleting subject: {e}")
            return False

    def delete_chat_file(self, subject_name: str, chat_filename: str) -> bool:
        """Delete a specific chat.md file in a subject folder."""
        subject_folder = self.subjects_path / subject_name
        chat_path = subject_folder / chat_filename

        if not chat_path.exists():
            print(f"Chat '{chat_filename}' not found in subject '{subject_name}'.")
            return False

        try:
            chat_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting chat file: {e}")
            return False
 
    def move_chat_to_subject(self, source_subject: str, chat_filename: str, target_subject: str) -> bool:
        """
        Move a chat file from one subject folder to another.

        Returns:
            True if successful, False otherwise.
        """
        source_folder = self.subjects_path / source_subject
        target_folder = self.subjects_path / target_subject

        # Ensure source exists
        source_path = source_folder / chat_filename
        if not source_path.exists():
            print(f"Chat {chat_filename} not found in subject {source_subject}.")
            return False

        # Ensure target folder exists
        try:
            target_folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating target subject folder {target_subject}: {e}")
            return False

        target_path = target_folder / chat_filename

        try:
            # Copy then delete (safer than rename across filesystems)
            target_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
            source_path.unlink()
            return True
        except Exception as e:
            print(f"Error moving chat from {source_subject} to {target_subject}: {e}")
            return False
