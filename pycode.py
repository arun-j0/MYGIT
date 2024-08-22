import streamlit as st
from streamlit_ace import st_ace
import io
import contextlib

# Define available themes
THEMES = [
    "textmate",
    "monokai",
    "github",
    "solarized_light",
    "solarized_dark",
    "terminal",
    "eclipse",
    "xcode",
    
    "kuroir",
    "dracula"
]

st.title("Python Code Interpreter with Dynamic Theme")

# Dropdown for selecting the theme
selected_theme = st.selectbox("Select Editor Theme:", THEMES)

# Code editor with syntax highlighting and selected theme
code = st_ace(
    value="print('Hello, World!')",
    language="python",
    theme=selected_theme,  # Use the selected theme
)

if st.button("Run Code"):
    output = io.StringIO()  # Create an in-memory file-like object to capture output
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(code)  # Execute the code
        result = output.getvalue()  # Get the output as a string
    except Exception as e:
        result = f"Error: {e}"  # Capture any exceptions as errors

    st.subheader("Output")
    st.code(result)  # Display the result
