#!/usr/bin/env python3

import sys
from pathlib import Path
from ollama_engineer import OllamaEngineer

# --------------------------------------------------------------------------------
# Console UI utilities
# --------------------------------------------------------------------------------

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

def try_handle_add_command(user_input: str, engineer: OllamaEngineer) -> bool:
    """Try to handle an 'add' command for adding file content to context."""
    if user_input.startswith("add "):
        file_path = user_input[4:].strip()
        if engineer.ensure_file_in_context(file_path):
            print_color(f"✓ Added '{file_path}' to conversation context", Colors.GREEN)
        else:
            print_color(f"✗ File not found: '{file_path}'", Colors.RED)
        return True
    return False

# --------------------------------------------------------------------------------
# Main interactive loop
# --------------------------------------------------------------------------------

def main():
    # Initialize the Ollama Engineer
    engineer = OllamaEngineer()
    
    # Print session folder info
    session_folder = engineer.get_session_folder()
    print_color(f"Session folder: {session_folder}", Colors.CYAN)
    
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
            if try_handle_add_command(user_input, engineer):
                continue
                
            # Look for potential file references
            referenced_files = engineer.guess_files_in_message(user_input)
            for file_path in referenced_files:
                engineer.ensure_file_in_context(file_path)
            
            # Get response from Ollama Engineer
            response = engineer.process_message(user_input)
            
            # Handle file creations
            if response.files_to_create:
                for file_to_create in response.files_to_create:
                    success, msg = engineer.create_file(file_to_create.path, file_to_create.content)
                    if success:
                        print_color(f"✓ {msg}", Colors.GREEN)
                    else:
                        print_color(f"✗ {msg}", Colors.RED)
            
            # Handle file edits
            if response.files_to_edit:
                show_diff_table(response.files_to_edit)
                print_color("\nApply these changes? (y/n): ", Colors.YELLOW, end='')
                if input().lower().startswith('y'):
                    for edit in response.files_to_edit:
                        success, msg = engineer.apply_diff_edit(
                            edit.path,
                            edit.original_snippet,
                            edit.new_snippet
                        )
                        if success:
                            print_color(f"✓ {msg}", Colors.GREEN)
                        else:
                            print_color(f"✗ {msg}", Colors.RED)
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
    main()
