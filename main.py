#!/usr/bin/env python3

import sys
import random
from pathlib import Path
from ollama_engineer import OllamaEngineer

# --------------------------------------------------------------------------------
# 1. Console UI utilities
# --------------------------------------------------------------------------------

# Word lists for random folder names
ADJECTIVES = ['swift', 'bright', 'calm', 'wise', 'bold', 'kind', 'pure', 'warm', 'cool', 'soft']
NOUNS = ['river', 'mountain', 'forest', 'cloud', 'star', 'ocean', 'valley', 'meadow', 'wind', 'sun']
COLORS = ['azure', 'coral', 'jade', 'amber', 'ruby', 'pearl', 'gold', 'silver', 'bronze', 'crystal']

def generate_random_folder_name() -> str:
    """Generate a random 3-word folder name"""
    return f"{random.choice(ADJECTIVES)}_{random.choice(COLORS)}_{random.choice(NOUNS)}"

# Color codes for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_color(text: str, color: str = '', end='\n'):
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.END}", end=end)

def show_diff_table(files_to_edit):
    """Display a simple ASCII table showing the proposed edits."""
    if not files_to_edit:
        return
    
    print_color("\nProposed Edits:", Colors.BOLD + Colors.BLUE)
    print("-" * 80)
    
    for edit in files_to_edit:
        print_color(f"File: {edit.path}", Colors.CYAN)
        print_color("Original:", Colors.RED)
        print(edit.original_snippet)
        print_color("New:", Colors.GREEN)
        print(edit.new_snippet)
        print("-" * 80)

def try_handle_add_command(user_input: str) -> bool:
    """Try to handle an 'add' command for adding file content to context."""
    if user_input.startswith("add "):
        file_path = user_input[4:].strip()
        if engineer.ensure_file_in_context(file_path):
            print_color(f"✓ Added '{file_path}' to conversation context", Colors.GREEN)
        else:
            print_color(f"✗ File not found: '{file_path}'", Colors.RED)
        return True
    return False

def guess_files_in_message(user_message: str):
    """
    Attempt to guess which files the user might be referencing.
    Returns normalized absolute paths.
    """
    current_dir = Path.cwd()
    potential_files = []
    
    # Split message into words and look for potential file references
    words = user_message.split()
    for word in words:
        # Skip words that are clearly not file paths
        if len(word) < 2 or word.startswith(("http://", "https://")):
            continue
            
        # Try to construct a path
        potential_path = current_dir / word
        if potential_path.exists():
            potential_files.append(str(potential_path.resolve()))
            
    return potential_files

# --------------------------------------------------------------------------------
# 2. Main interactive loop
# --------------------------------------------------------------------------------

def main():
    global engineer
    
    # Create session folder for file operations
    session_folder = Path.cwd() / generate_random_folder_name()
    session_folder.mkdir(exist_ok=True)
    print_color(f"Session folder: {session_folder}", Colors.CYAN)
    
    # Initialize the Ollama Engineer
    engineer = OllamaEngineer()
    
    # Main interaction loop
    print_color("\nOllama Engineer CLI 🚀", Colors.BOLD + Colors.BLUE)
    print_color("Type 'exit' to quit, 'add <file>' to add file to context\n", Colors.CYAN)
    
    while True:
        try:
            # Get user input
            print_color("\nYou: ", Colors.BOLD, end='')
            user_input = input().strip()
            
            # Handle exit command
            if user_input.lower() in ('exit', 'quit'):
                break
                
            # Skip empty input
            if not user_input:
                continue
                
            # Try to handle special commands
            if try_handle_add_command(user_input):
                continue
                
            # Look for potential file references
            referenced_files = guess_files_in_message(user_input)
            for file_path in referenced_files:
                engineer.ensure_file_in_context(file_path)
            
            # Get response from Ollama Engineer
            response = engineer.process_message(user_input)
            
            # Handle file creations
            if response.files_to_create:
                for file_to_create in response.files_to_create:
                    engineer.create_file(file_to_create.path, file_to_create.content)
            
            # Handle file edits
            if response.files_to_edit:
                show_diff_table(response.files_to_edit)
                print_color("\nApply these changes? (y/n): ", Colors.YELLOW, end='')
                if input().lower().startswith('y'):
                    for edit in response.files_to_edit:
                        if engineer.apply_diff_edit(edit.path, edit.original_snippet, edit.new_snippet):
                            print_color(f"✓ Applied changes to {edit.path}", Colors.GREEN)
                        else:
                            print_color(f"✗ Failed to apply changes to {edit.path}", Colors.RED)
                else:
                    print_color("Changes discarded.", Colors.YELLOW)
            
            # Print the assistant's reply
            print_color("\nAssistant: ", Colors.BOLD + Colors.GREEN)
            print(response.assistant_reply)
            
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit properly")
        except Exception as e:
            print_color(f"\nError: {str(e)}", Colors.RED)

if __name__ == "__main__":
    engineer = None  # Global instance
    main()
