import streamlit as st
from pathlib import Path
from ollama_engineer import OllamaEngineer

# Initialize session state
if 'engineer' not in st.session_state:
    st.session_state.engineer = OllamaEngineer()
    st.session_state.messages = []
    st.session_state.file_content = {}
    st.session_state.pending_edits = None

# Page config
st.set_page_config(
    page_title="Ollama Engineer",
    page_icon="🚀",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("Ollama Engineer 🚀")
    st.markdown("Your AI Pair Programming Assistant")
    
    # File upload
    uploaded_file = st.file_uploader("Upload a file to analyze", type=['py', 'js', 'html', 'css', 'json', 'txt', 'md'])
    if uploaded_file:
        file_path = Path(st.session_state.engineer.get_session_folder()) / uploaded_file.name
        content = uploaded_file.getvalue().decode()
        success, msg = st.session_state.engineer.create_file(str(file_path), content)
        if success:
            st.success(f"Added file: {uploaded_file.name}")
            st.session_state.file_content[uploaded_file.name] = content
        else:
            st.error(msg)
    
    # Show uploaded files
    if st.session_state.file_content:
        st.markdown("### Uploaded Files")
        for filename in st.session_state.file_content:
            with st.expander(filename):
                st.code(st.session_state.file_content[filename])
    
    # Reset conversation button
    if st.button("Reset Conversation"):
        st.session_state.engineer.reset_conversation()
        st.session_state.messages = []
        st.session_state.pending_edits = None
        st.success("Conversation reset!")

# Main chat interface
st.title("Chat with Ollama Engineer")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle pending file edits if any
if st.session_state.pending_edits:
    st.markdown("### Pending File Changes")
    
    for edit in st.session_state.pending_edits:
        with st.expander(f"Changes to {edit.path}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original:**")
                st.code(edit.original_snippet)
            with col2:
                st.markdown("**New:**")
                st.code(edit.new_snippet)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply Changes"):
            for edit in st.session_state.pending_edits:
                success, msg = st.session_state.engineer.apply_diff_edit(
                    edit.path, 
                    edit.original_snippet, 
                    edit.new_snippet
                )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            st.session_state.pending_edits = None
    with col2:
        if st.button("Discard Changes"):
            st.session_state.pending_edits = None
            st.info("Changes discarded")

# Chat input
if prompt := st.chat_input("Ask me anything about coding..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.engineer.process_message(prompt)
            
            # Handle file creations
            if response.files_to_create:
                for file_to_create in response.files_to_create:
                    success, msg = st.session_state.engineer.create_file(
                        file_to_create.path,
                        file_to_create.content
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
            
            # Handle file edits
            if response.files_to_edit:
                st.session_state.pending_edits = response.files_to_edit
            
            # Display assistant's reply
            st.markdown(response.assistant_reply)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.assistant_reply
            })
