import streamlit as st
import google.generativeai as genai
import time
import re
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(
    page_title="𝙸𝚗𝚝𝚎𝚛𝚕𝚒𝚗𝚔 𝙰𝙸",
    page_icon="./favicon.ico",
    layout="wide"
)

st.markdown("""
    <style>
        /* Apply Orbitron font */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');
        
        .back-button {
            width: 300px;  /* Increased width for a longer button */
            margin-top: 20px;
            padding: 20px 40px;  /* Increased padding for a more prominent button */
            font-size: 22px;  /* Increased font size for better readability */
            background-color: #0b1936;
            color: #5799f7;
            border: 2px solid #4a83d4;
            border-radius: 12px;  /* Slightly more rounded corners */
            font-family: 'Orbitron', sans-serif;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 0 15px rgba(74, 131, 212, 0.3);
            position: relative;
            cursor: pointer;
            overflow: hidden;
            transition: all 0.3s ease;
            text-align: center;
            display: inline-block; /* Ensures the button is rendered properly */
            text-decoration: none; /* Prevents underlines from appearing */
            text-align: center; /* Ensures text is centered */
            line-height: 1.5; /* Ensures text is vertically centered */
        }
        
        .back-button:before {
            content: 'BACK TO INTERLINK';
            display: flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #0b1936;
            transition: transform 0.3s ease;
            padding: 0 15px; /* Ensures padding for text inside */
        }
        
        .back-button:hover {
            background-color: #1c275c;
            color: #73abfa;
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(74, 131, 212, 0.2);
        }
        
        .back-button:hover:before {
            transform: translateY(-100%);
        }
        
        .back-button:active {
            transform: translateY(0px);
            box-shadow: 0 0 15px rgba(74, 131, 212, 0.3);
        }
        
        /* Centering the button in the page */
        .back-button-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;  /* Make sure the container takes full height */
        }
    </style>
""", unsafe_allow_html=True)

# Wrap the button in a div to center it
st.markdown("""
    <div class="back-button-container">
        <a href="https://interlinkcvhs.org/" class="back-button" target="_blank" rel="noopener noreferrer">
            interlinkcvhs.org
        </a>
    </div>
""", unsafe_allow_html=True)

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

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

SYSTEM_INSTRUCTION = """Your name is Interlink AI, an AI chatbot on Interlink.
You are powered by the Interlink Large Language Model.
You were created by the Interlink team.
You are on a website called Interlink that provides Carnegie Vanguard High School (CVHS) freshmen resources to stay on top of their assignments and tests using a customized scheduling tool as well as notes, educational simulations, Quizlets, the Question of the Day (QOTD) and the Question Bank (QBank) that both provide students example questions from upcoming tests or assignments, and other resources to help them do better in school.
The link to Interlink is: https://interlinkcvhs.org/."""

if 'chat_model' not in st.session_state:
    st.session_state.chat_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=SYSTEM_INSTRUCTION,
    )

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = st.session_state.chat_model.start_chat(history=[])

if 'messages' not in st.session_state:
    initial_message = """Hello! I'm Interlink AI, your personal academic assistant for Carnegie Vanguard High School. How can I assist you today?"""
    
    st.session_state.messages = [
        {"role": "assistant", "content": initial_message}
    ]

st.title("💬 Interlink AI")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("What can I help you with?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            response = st.session_state.chat_session.send_message(prompt)
            
            formatted_response = process_response(response.text)

            chunks = []
            for line in formatted_response.split('\n'):
                chunks.extend(line.split(' '))
                chunks.append('\n')

            for chunk in chunks:
                if chunk != '\n':
                    full_response += chunk + ' '
                else:
                    full_response += chunk
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            
            message_placeholder.markdown(full_response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if "rate_limit" in str(e).lower():
                st.warning("The API rate limit has been reached. Please wait a moment before trying again.")
            else:
                st.warning("Please try again in a moment.")
