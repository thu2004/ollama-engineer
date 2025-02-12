# Ollama Engineer 

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![image](https://github.com/user-attachments/assets/cc1b3a1b-8a98-49cf-af26-d3c4606d0779)

## Overview

This repository contains a powerful coding assistant application that integrates with Ollama to process user conversations and generate structured JSON responses. It offers both a command-line interface and a modern Streamlit web UI, allowing users to read local file contents, create new files, and apply diff edits to existing files in real time. While making this fork of DeepSeek Engineer our goal was to reduce the dependencies and to be able to use any self-hosted model while not adding more code than necessary to achieve this result.

## Requirements

- Python 3.8 or higher
- Ollama installed and running with a model

## Key Features

1. Dual Interface Support
   - Command-line interface for quick interactions
   - Modern Streamlit web UI for enhanced visual experience

2. Ollama Integration
   - Uses local Ollama instance with the qwen2.5-coder:14b model
   - Streams responses for real-time interaction
   - Structured JSON output for precise code modifications

3. Data Models
   - Leverages Pydantic for type-safe handling of file operations, including:
     • FileToCreate – describes files to be created or updated
     • FileToEdit – describes specific snippet replacements in an existing file
     • AssistantResponse – structures chat responses and potential file operations

4. System Prompt
   - A comprehensive system prompt guides conversation, ensuring all replies strictly adhere to JSON output with optional file creations or edits

5. Helper Functions
   - read_local_file: Reads a target filesystem path and returns its content as a string
   - create_file: Creates or overwrites a file with provided content
   - show_diff_table: Presents proposed file changes in a clear, readable format
   - apply_diff_edit: Applies snippet-level modifications to existing files

6. File Management
   - Command-line: Use "/add path/to/file" to quickly read a file's content
   - Streamlit UI: Drag-and-drop file upload with syntax-highlighted preview
   - All files are organized in session-specific folders under tmp/

7. Conversation Flow
   - Maintains conversation history to track messages between user and assistant
   - Streams the assistant's replies via Ollama, parsing them as JSON
   - Visual diff previews for code changes

## Using the Streamlit UI

The Streamlit interface provides a modern, user-friendly way to interact with Ollama Engineer:

1. Starting the UI
   ```bash
   streamlit run streamlit_app.py
   ```

2. Features
   - **File Upload**: Drag and drop files directly into the UI
   - **Chat Interface**: Natural conversation with syntax-highlighted code
   - **Visual Diff**: Side-by-side comparison of code changes
   - **File Management**: Browse and preview uploaded files in the sidebar
   - **Session Management**: Reset conversation and start fresh anytime

3. Advantages
   - More intuitive file handling with visual feedback
   - Better code visualization with syntax highlighting
   - Easy approval/rejection of proposed changes
   - Persistent chat history within the session
   - Mobile-friendly responsive design

## Prerequisites

1. Install Ollama from https://ollama.ai
2. Pull the qwen2.5-coder model:
   ```bash
   ollama pull qwen2.5-coder:14b
   ```

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/dustinwloring1988/ollama-engineer.git
   cd ollama-engineer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start Ollama server (if not already running)

4. Run the application:
   ```bash
   python main.py
   ```

5. Enjoy multi-line streaming responses, file read-ins with "/add path/to/file", and precise file edits when approved.


## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install pre-commit hooks (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Project Structure

```
ollama-engineer/
├── main.py           # Main application file
├── requirements.txt  # Project dependencies
├── README.md        # Project documentation
└── .gitignore       # Git ignore rules
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

1. **Ollama Connection Issues**
   - Ensure Ollama is running (`ollama serve`)
   - Check if the default port (11434) is available
   - Verify your firewall settings

2. **Model Issues**
   - Try re-pulling the model: `ollama pull qwen2.5-coder:14b`
   - Check Ollama logs for any errors

3. **Python Environment Issues**
   - Ensure you're using Python 3.8+
   - Try recreating your virtual environment
   - Verify all dependencies are installed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original DeepSeek Engineer project for inspiration
- Ollama team for providing local LLM capabilities
- QWen team for the excellent code-focused model

> **Note**: This is a modified version of the original DeepSeek Engineer project, adapted to work with Ollama and the qwen2.5-coder model locally. It provides similar capabilities without requiring API keys or external services.
