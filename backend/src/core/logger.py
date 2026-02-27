import os
from datetime import datetime
from pathlib import Path
 
class ChatLogger:
    def __init__(self, basepath="."):
        self.basepath = Path(basepath)
        self.subjects_path = self.basepath / "subjects"

    def save_chat(self, subject_name, conversation_history, append=False):
        """Save chat log to the specified subject folder
        
        Args:
            subject_name: Name of the subject folder
            conversation_history: List of message dictionaries
            append: If True, append to existing chatlog.md, else create new file
        """
        subject_folder = self.subjects_path / subject_name
        
        # Ensure subject folder exists
        if not subject_folder.exists():
            raise FileNotFoundError(f"Subject folder '{subject_name}' does not exist")
        
        # Determine log file
        if append:
            log_file = subject_folder / "chatlog.md"
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
            log_file = subject_folder / f"chat_{timestamp}.md"
        
        # Format the conversation
        log_content = self.format_conversation(conversation_history)
        
        # Write to file
        mode = 'a' if (append and log_file.exists()) else 'w'
        with open(log_file, mode, encoding='utf-8') as f:
            if mode == 'a':
                f.write("\n---\n")  # Separator for appended sessions
                f.write(f"# Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(log_content)
        
        return log_file
    
    def format_conversation(self, conversation_history):
        """Format conversation history as markdown"""
        formatted = []
        for msg in conversation_history:
            role = msg['role'].capitalize()
            content = msg['content']
            formatted.append(f"**{role}:**\n{content}\n")
        return "\n".join(formatted)
    
    def create_subject_folder(self, subject_name):
        """Create a new subject folder with instructions.md template"""
        subject_folder = self.subjects_path / subject_name
        subject_folder.mkdir(parents=True, exist_ok=True)
        
        # Create instructions.md if it doesn't exist
        instructions_file = subject_folder / "instructions.md"
        if not instructions_file.exists():
            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write(f"# Instructions for {subject_name}\n\n")
                f.write("Add your subject-specific instructions here.\n")
        
        return subject_folder
