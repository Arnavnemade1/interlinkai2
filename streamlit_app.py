import streamlit as st
import google.generativeai as genai
import time
import re
import os
from PIL import Image

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

genai.configure(api_key=GEMINI_API_KEY)

# Set page config
st.set_page_config(
    page_title="𝙸𝚗𝚜𝚙𝚒𝚛𝚎𝚇 𝙰𝙸",
    page_icon="./favicon.ico",
    layout="wide"
)

# Custom CSS for styling with enhanced contrast and vibrant colors
st.markdown("""
<style>
    .stChatInputContainer {
        display: flex;
        align-items: center;
    }
    /* Updated color scheme with better contrast */
    body {
        background-color: #e0e4ff;  /* More vibrant light purple-blue background */
        color: #1a1a2e;  /* Darker text for better contrast */
    }
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(78, 54, 226, 0.15);
    }
    .stChatMessage.assistant {
        background-color: #dde1ff;  /* Slightly darker background for assistant messages */
        color: #000000;  /* Black text for maximum contrast */
    }
    .stChatMessage.user {
        background-color: #ffffff;  /* White background for user messages */
        color: #000000;  /* Black text for maximum contrast */
    }
    .stButton button {
        background-color: #4f46e5;  /* Darker indigo button for better contrast */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
        font-weight: 500;  /* Slightly bolder text */
    }
    .stButton button:hover {
        background-color: #3c348d;  /* Even darker on hover */
    }
    .stFileUploader button {
        background-color: #6366f1;  /* Vibrant indigo for file uploader */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
        font-weight: 500;  /* Slightly bolder text */
    }
    .stFileUploader button:hover {
        background-color: #4f46e5;
    }
    .stApp {
        background: linear-gradient(135deg, #7c83fd 0%, #96baff 100%);  /* More vibrant gradient background */
    }
    /* Enhanced text contrast for all elements */
    .stMarkdown {
        color: #000000 !important;  /* Ensure markdown text is black */
    }
    .stTextInput label {
        color: #1a1a2e !important;  /* Dark color for input labels */
    }
    .stTextInput input {
        color: #000000 !important;  /* Black text for input fields */
    }
    /* Make titles and headers more visible */
    h1, h2, h3 {
        color: #1a1a2e !important;
        font-weight: 600 !important;
    }
    /* Add a white background to the chat container for better contrast */
    .stChatFloatingInputContainer {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Gemini generation config
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Function to process Gemini's response
def process_response(text):
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        if re.match(r'^\d+\.', line.strip()):
            processed_lines.append('\n' + line.strip())
        elif line.strip().startswith('*') or line.strip().startswith('-'):
            processed_lines.append('\n' + line.strip())
        else:
            processed_lines.append(line)
    
    text = '\n'.join(processed_lines)
    
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r'(\n[*-] .+?)(\n[^*\n-])', r'\1\n\2', text)
    
    return text.strip()

# System instruction for Gemini
SYSTEM_INSTRUCTION = """Your name is InspireX AI, an AI chatbot on InspireX.
You are powered by the InspireX Large Language Model.
You were created by the InspireX team.
You are on a website called InspireX that provides Carnegie Vanguard High School (CVHS) freshmen resources to stay on top of their assignments and tests using a customized scheduling tool as well as notes, educational simulations, Quizlets, the Question of the Day (QOTD) and the Question Bank (QBank) that both provide students example questions from upcoming tests or assignments, and other resources to help them do better in school.
The link to InspireX is: https://inspirexcvhs.org/."""

# Initialize session state
def initialize_session_state():
    if 'chat_model' not in st.session_state:
        st.session_state.chat_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=SYSTEM_INSTRUCTION,
        )

    if 'chat_session' not in st.session_state:
        st.session_state.chat_session = st.session_state.chat_model.start_chat(history=[])

    if 'messages' not in st.session_state:
        initial_message = """Hello! I'm InspireX AI, your personal academic assistant for Carnegie Vanguard High School. How can I assist you today?"""
        
        st.session_state.messages = [
            {"role": "assistant", "content": initial_message}
        ]

# Main function
def main():
    initialize_session_state()

    st.title("💬 InspireX AI")

    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # Image upload button
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.session_state.messages.append({"role": "user", "content": f"Uploaded image: {uploaded_file.name}"})

    # Input prompt field below the chat messages
    prompt = st.chat_input("What can I help you with?")

    if prompt:
        st.chat_message("user").markdown(prompt)
        
        full_prompt = prompt
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Check if an image was uploaded
                if uploaded_file is not None:
                    # Use Gemini's multimodal capabilities
                    response = st.session_state.chat_model.generate_content([prompt, image])
                else:
                    # Use text-only model
                    response = st.session_state.chat_session.send_message(full_prompt)
                
                formatted_response = process_response(response.text)

                chunks = []
                for line in formatted_response.split('\n'):
                    chunks.extend(line.split(' '))  # Split into chunks for smooth typing effect
                    chunks.append('\n')

                for chunk in chunks:
                    if chunk != '\n':
                        full_response += chunk + ' '
                    else:
                        full_response += chunk
                    time.sleep(0.05)  # Add a delay for the typing effect
                    message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                
                message_placeholder.markdown(full_response, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if "rate_limit" in str(e).lower():
                    st.warning("The API rate limit has been reached. Please wait a moment before trying again.")
                else:
                    st.warning("Please try again in a moment.")

if __name__ == "__main__":
    main()
