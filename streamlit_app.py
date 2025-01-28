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

# Set page config - removed icon
st.set_page_config(
    page_title="𝙸𝚗𝚜𝚙𝚒𝚛𝚎𝚇 𝙰𝙸",
    layout="wide"
)

# Enhanced CSS with improved visibility and effects
st.markdown("""
<style>
    /* Enhanced gradient animation */
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Typing animation */
    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }

    /* Glow animation */
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.5); }
        50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.8); }
        100% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.5); }
    }

    .stApp {
        background: linear-gradient(
            -45deg, 
            #7c83fd,
            #96baff,
            #4f46e5,
            #818cf8,
            #6366f1,
            #4338ca
        );
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    /* Enhanced chat messages with better visibility */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    }

    .stChatMessage.assistant {
        background-color: rgba(240, 244, 255, 0.95) !important;
    }

    .stChatMessage.user {
        background-color: rgba(255, 255, 255, 0.95) !important;
    }

    /* Message text styling */
    .stChatMessage p {
        color: #1a1a1a !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }

    /* Enhanced title with animation */
    h1 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        font-size: 3rem !important;
        font-weight: bold !important;
        margin-bottom: 2rem !important;
        background-color: rgba(0, 0, 0, 0.2);
        padding: 1.5rem;
        border-radius: 15px;
        display: inline-block;
        animation: glow 3s ease-in-out infinite;
        backdrop-filter: blur(5px);
    }

    /* Enhanced buttons with hover effect */
    .stButton button {
        background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(5px);
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #4338ca, #4f46e5) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2) !important;
    }

    /* Enhanced file uploader */
    .stFileUploader {
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Enhanced chat input container */
    .stChatInputContainer {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin-top: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(10px);
        animation: glow 3s ease-in-out infinite;
    }

    /* Enhanced chat input */
    .stChatInput input {
        border-color: #6366f1 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 1.1rem !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #1a1a1a !important;
    }

    .stChatInput input:focus {
        box-shadow: 0 0 0 2px #4f46e5 !important;
        transform: translateY(-1px);
    }

    /* Enhanced scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.7);
        border-radius: 5px;
        transition: background 0.3s ease;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.9);
    }

    /* Container styling */
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }

    /* Code block styling */
    pre {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        color: #f8f8f2 !important;
    }

    code {
        font-family: 'Monaco', 'Consolas', monospace !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
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

    # Input prompt field
    prompt = st.chat_input("What can I help you with?")

    if prompt:
        st.chat_message("user").markdown(prompt)
        full_prompt = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                if uploaded_file is not None:
                    response = st.session_state.chat_model.generate_content([prompt, image])
                else:
                    response = st.session_state.chat_session.send_message(full_prompt)
                
                formatted_response = process_response(response.text)
                chunks = []
                for line in formatted_response.split('\n'):
                    chunks.append(line.strip())
                
                full_response = "\n".join(chunks)
                message_placeholder.markdown(full_response, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            except Exception as e:
                message_placeholder.markdown(f"Error: {e}")
            
            time.sleep(1)

if __name__ == "__main__":
    main()
