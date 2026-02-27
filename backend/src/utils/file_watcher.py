#!/usr/bin/env python3
import os
import time
import shutil
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class PyFileHandler(FileSystemEventHandler):
    def __init__(self, project_dir, for_ai_dir):
        self.project_dir = Path(project_dir)
        self.for_ai_dir = Path(for_ai_dir)
        # Create for_ai directory if it doesn't exist
        self.for_ai_dir.mkdir(exist_ok=True)

    def on_modified(self, event):
        # Only process .py files that are actually files (not directories)
        if not event.is_directory and event.src_path.endswith(".py"):
            self.copy_to_txt(event.src_path)

    def on_created(self, event):
        # Handle newly created .py files too
        if not event.is_directory and event.src_path.endswith(".py"):
            self.copy_to_txt(event.src_path)

    def _get_mode_prefix(self, py_file: Path) -> str:
        """
        Determine if the file is under commands/pyWebView or commands/terminal.
        Returns 'pyWebView.' or 'terminal.' or ''.
        """
        parts = [str(p) for p in py_file.parts]
        if "commands" in parts:
            idx = parts.index("commands")
            if idx + 1 < len(parts):
                next_part = parts[idx + 1]
                if next_part in ("pyWebView", "terminal"):
                    return f"{next_part}."
        return ""

    def get_txt_filename(self, py_file):
        """Generate txt filename based on location and whether it's __init__.py."""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M')

        parts = py_file.parts

        # Special handling for commands pyWebView/terminal
        if "commands" in parts:
            try:
                idx = parts.index("commands")
                if idx + 1 < len(parts):
                    mode = parts[idx + 1]  # 'pyWebView' or 'terminal'
                    if mode in ("pyWebView", "terminal"):
                        # commands.[pyWebView|terminal].[file_name]
                        if py_file.name == "__init__.py":
                            base_name = f"commands.{mode}.init"
                        else:
                            base_name = f"commands.{mode}.{py_file.stem}"
                        return f"{base_name}_{timestamp}.txt"
            except ValueError:
                pass

        # All other files: [parent].[file_name] or [parent].init
        parent = py_file.parent.name

        if py_file.name == "__init__.py":
            base_name = f"{parent}.init"
        else:
            base_name = f"{parent}.{py_file.stem}"

        return f"{base_name}_{timestamp}.txt"
 
    def copy_to_txt(self, py_file_path):
        py_file = Path(py_file_path)

        # Skip files in the for_ai directory itself
        if self.for_ai_dir in py_file.parents:
            return

        # Determine the base name for matching old files
        parts = py_file.parts

        # Commands pyWebView/terminal pattern
        if "commands" in parts:
            try:
                idx = parts.index("commands")
                if idx + 1 < len(parts):
                    mode = parts[idx + 1]
                    if mode in ("pyWebView", "terminal"):
                        if py_file.name == "__init__.py":
                            base_pattern = f"commands.{mode}.init_*.txt"
                        else:
                            base_pattern = f"commands.{mode}.{py_file.stem}_*.txt"
                    else:
                        # commands but not pyWebView/terminal: fall back to parent.[file]
                        parent = py_file.parent.name
                        if py_file.name == "__init__.py":
                            base_pattern = f"{parent}.init_*.txt"
                        else:
                            base_pattern = f"{parent}.{py_file.stem}_*.txt"
            except ValueError:
                parent = py_file.parent.name
                if py_file.name == "__init__.py":
                    base_pattern = f"{parent}.init_*.txt"
                else:
                    base_pattern = f"{parent}.{py_file.stem}_*.txt"
        else:
            # Non-commands files: [parent].[file]
            parent = py_file.parent.name
            if py_file.name == "__init__.py":
                base_pattern = f"{parent}.init_*.txt"
            else:
                base_pattern = f"{parent}.{py_file.stem}_*.txt"


        # Delete any existing .txt files for this .py file (ignore timestamps)
        for existing_file in self.for_ai_dir.glob(base_pattern):
            try:
                existing_file.unlink()
                print(f"✗ Deleted old version: {existing_file.name}")
            except Exception as e:
                print(f"✗ Error deleting {existing_file.name}: {e}")

        # Generate new filename
        txt_filename = self.get_txt_filename(py_file)
        txt_file = self.for_ai_dir / txt_filename

        try:
            # Copy contents from .py to .txt
            shutil.copy2(py_file, txt_file)
            print(f"✓ Created {txt_filename}")
        except Exception as e:
            print(f"✗ Error copying {py_file.name}: {e}")


def main():
    # Find project root (backend directory)
    # Start from current file location and go up to find 'backend'
    current_file = Path(__file__).resolve()
    project_dir = current_file.parent

    # Navigate up until we find the backend directory
    while project_dir.name != "backend" and project_dir.parent != project_dir:
        project_dir = project_dir.parent

    # If we didn't find 'backend', use current working directory
    if project_dir.name != "backend":
        project_dir = Path.cwd()

    # Set for_ai directory at backend/src/utils/for_ai/
    for_ai_dir = project_dir / "src" / "utils" / "for_ai"

    print(f"Watching for .py file changes in: {project_dir}")
    print(f"Output directory: {for_ai_dir}")
    print("Press Ctrl+C to stop\n")

    event_handler = PyFileHandler(project_dir, for_ai_dir)
    observer = Observer()
    observer.schedule(event_handler, project_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching files")

    observer.join()


if __name__ == "__main__":
    main()
