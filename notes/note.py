import os
import streamlit as st
from streamlit_quill import st_quill

# Constants
NOTES_DIR = "notes"

# Ensure the notes directory exists
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)

@st.cache_data
def load_note_titles():
    """Load all note titles from the notes directory."""
    return [f.replace(".txt", "") for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]

@st.cache_data
def load_note_content(title):
    """Load the content of a note by title."""
    file_path = os.path.join(NOTES_DIR, f"{title}.txt")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_note(title, content):
    """Save the note content to a file."""
    file_path = os.path.join(NOTES_DIR, f"{title}.txt")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def delete_note(title):
    """Delete a note file by title."""
    file_path = os.path.join(NOTES_DIR, f"{title}.txt")
    if os.path.exists(file_path):
        os.remove(file_path)

# Streamlit Interface
st.title("Notepad")

# CSS to make the editor full-size
st.markdown(
    """
    <style>
    .full-size-editor .ql-container {
        min-height: calc(100vh - 150px);
        height: calc(100vh - 150px);
    }
    .full-size-editor .ql-editor {
        min-height: calc(100vh - 150px);
        height: calc(100vh - 150px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Option to create a new note - placed at the top and collapsed by default
with st.expander("Create a New Note", expanded=False):
    note_title = st.text_input("New Note Title")
    note_content = st_quill(placeholder="Start typing...", key="new_note")

    if st.button("Save New Note"):
        if note_title and note_content:
            save_note(note_title, note_content)
            st.cache_data.clear()  # Clear cache to force reload
            st.success(f"Note '{note_title}' saved successfully!")
        else:
            st.warning("Please enter a title and content to save the note.")

# Display all notes
note_titles = load_note_titles()
if note_titles:
    for note_title in note_titles:
        with st.expander(note_title, expanded=False):  # All expanders are closed by default
            note_content = load_note_content(note_title)
            edited_content = st_quill(value=note_content, key=f"edit_{note_title}")

            col1, col2 = st.columns([1, 3])
            with col1:
                new_title = st.text_input("Update Title", value=note_title, key=f"title_{note_title}")
            with col2:
                if st.button("Update Note", key=f"update_{note_title}"):
                    if new_title and edited_content:
                        save_note(new_title, edited_content)
                        if new_title != note_title:
                            delete_note(note_title)  # Delete old note file if title changes
                        st.cache_data.clear()  # Clear cache to force reload
                        st.success(f"Note '{new_title}' updated successfully!")

                if st.button("Delete Note", key=f"delete_{note_title}"):
                    delete_note(note_title)
                    st.cache_data.clear()  # Clear cache to force reload
                    st.success(f"Note '{note_title}' deleted successfully!")

else:
    st.write("No notes available.")
