#!/usr/bin/env python3

import os
import json
from pathlib import Path
from textwrap import dedent
from typing import List, Dict, Any, Optional
import requests
from pydantic import BaseModel

# --------------------------------------------------------------------------------
# 1. Configure Ollama client settings
# --------------------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "qwen2.5-coder:14b"

class FileToCreate(BaseModel):
    path: str
    content: str

class FileToEdit(BaseModel):
    path: str
    original_snippet: str
    new_snippet: str

class AssistantResponse(BaseModel):
    assistant_reply: str
    files_to_create: Optional[List[FileToCreate]] = None
    files_to_edit: Optional[List[FileToEdit]] = None

# --------------------------------------------------------------------------------
# 2. Core system prompt
# --------------------------------------------------------------------------------
SYSTEM_PROMPT = dedent("""\
    You are an elite software engineer called Ollama Engineer with decades of experience across all programming domains.
    Your expertise spans system design, algorithms, testing, and best practices.
    You provide thoughtful, well-structured solutions while explaining your reasoning.

    Core capabilities:
    1. Code Analysis & Discussion
       - Analyze code with expert-level insight
       - Explain complex concepts clearly
       - Suggest optimizations and best practices
       - Debug issues with precision

    2. File Operations:
       a) Read existing files
          - Access user-provided file contents for context
          - Analyze multiple files to understand project structure
       
       b) Create new files
          - Generate complete new files with proper structure
          - Create complementary files (tests, configs, etc.)
       
       c) Edit existing files
          - Make precise changes using diff-based editing
          - Modify specific sections while preserving context
          - Suggest refactoring improvements

    Output Format:
    You must provide responses in this JSON structure:
    {
      "assistant_reply": "Your main explanation or response",
      "files_to_create": [
        {
          "path": "path/to/new/file",
          "content": "complete file content"
        }
      ],
      "files_to_edit": [
        {
          "path": "path/to/existing/file",
          "original_snippet": "exact code to be replaced",
          "new_snippet": "new code to insert"
        }
      ]
    }

    Guidelines:
    1. For normal responses, use 'assistant_reply'
    2. When creating files, include full content in 'files_to_create'
    3. For editing files:
       - Use 'files_to_edit' for precise changes
       - Include enough context in original_snippet to locate the change
       - Ensure new_snippet maintains proper indentation
       - Prefer targeted edits over full file replacements
    4. Always explain your changes and reasoning
    5. Consider edge cases and potential impacts
    6. Follow language-specific best practices
    7. Suggest tests or validation steps when appropriate

    Remember: You're a senior engineer - be thorough, precise, and thoughtful in your solutions.
""")

class OllamaEngineer:
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model_name: str = MODEL_NAME):
        self.base_url = base_url
        self.model_name = model_name
        self.conversation_history = []
        self.initialize_conversation()

    def initialize_conversation(self):
        """Initialize the conversation with system prompt"""
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def read_local_file(self, file_path: str) -> str:
        """Return the text content of a local file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def create_file(self, path: str, content: str):
        """Create (or overwrite) a file at 'path' with the given 'content'."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Record the action in conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": f"✓ Created/updated file at '{file_path}'"
        })
        
        # Add the actual content to conversation context
        normalized_path = self.normalize_path(str(file_path))
        self.conversation_history.append({
            "role": "system",
            "content": f"Content of file '{normalized_path}':\n\n{content}"
        })

    def apply_diff_edit(self, path: str, original_snippet: str, new_snippet: str) -> bool:
        """
        Reads the file at 'path', replaces the first occurrence of 'original_snippet' with 'new_snippet'.
        Returns True if successful, False otherwise.
        """
        try:
            content = self.read_local_file(path)
            if original_snippet in content:
                updated_content = content.replace(original_snippet, new_snippet, 1)
                self.create_file(path, updated_content)
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"✓ Applied diff edit to '{path}'"
                })
                return True
            return False
        except FileNotFoundError:
            return False

    def ensure_file_in_context(self, file_path: str) -> bool:
        """
        Ensures the file content is in the conversation context.
        Returns True if successful, False if file not found.
        """
        try:
            content = self.read_local_file(file_path)
            normalized_path = self.normalize_path(file_path)
            self.conversation_history.append({
                "role": "system",
                "content": f"Content of file '{normalized_path}':\n\n{content}"
            })
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def normalize_path(path_str: str) -> str:
        """Return a canonical, absolute version of the path."""
        return str(Path(path_str).resolve())

    def process_message(self, user_message: str) -> AssistantResponse:
        """
        Process a user message and return an AssistantResponse.
        This is the main entry point for getting responses from the model.
        """
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Prepare the API request
        api_url = f"{self.base_url}/api/chat"
        request_body = {
            "model": self.model_name,
            "messages": self.conversation_history,
            "stream": False  # For simplicity, we're not streaming in the core library
        }

        # Make the API call
        try:
            response = requests.post(api_url, json=request_body)
            response.raise_for_status()
            response_data = response.json()
            
            # Parse the response
            message_content = response_data["message"]["content"]
            
            # Try to parse as JSON
            try:
                parsed_response = json.loads(message_content)
                assistant_response = AssistantResponse(**parsed_response)
            except (json.JSONDecodeError, ValueError):
                # If not valid JSON, treat as plain text response
                assistant_response = AssistantResponse(assistant_reply=message_content)

            # Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": message_content
            })

            return assistant_response

        except Exception as e:
            # In case of any error, return a simple error response
            return AssistantResponse(
                assistant_reply=f"Error processing request: {str(e)}"
            )

    def reset_conversation(self):
        """Reset the conversation history to initial state"""
        self.initialize_conversation()
