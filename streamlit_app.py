import streamlit as st
import google.generativeai as genai
import time
import re
import os
from PIL import Image
import pandas as pd
import io
from PyPDF2 import PdfReader

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
    .upload-container {
        display: flex;
        align-items: center;
    }
    .upload-icon {
        cursor: pointer;
        margin-right: 10px;
        transition: transform 0.2s;
    }
    .upload-icon:hover {
        transform: scale(1.2);
    }
    .file-upload-input {
        display: none;
    }
    .stChatInputContainer {
        display: flex;
        align-items: center;
    }
    .back-button {
        width: 300px;
        margin-top: 20px;
        padding: 10px 20px;
        font-size: 18px;
        background-color: #0b1936;
        color: #5799f7;
        border: 2px solid #4a83d4;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 0 15px rgba(74, 131, 212, 0.3);
        position: relative;
        overflow: hidden;
        display: inline-block;
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
        font-size: 18px;
        color: #5799f7;
        text-align: center;
    }
    .back-button:hover {
        background-color: #1c275c;
        color: #73abfa;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(74, 131, 212, 0.2);
    }
    .back-button:hover:before {
        transform: translateY(-100%);
        color: #73abfa;
    }
</style>
<center>
    <a href="https://interlinkcvhs.org/" class="back-button" target="_blank" rel="noopener noreferrer">
        interlinkcvhs.org
    </a>
</center>""", unsafe_allow_html=True)

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

def handle_file_upload(uploaded_file):
    if uploaded_file is None:
        return None, None

    file_type = uploaded_file.type
    content = None
    preview = None

    try:
        if file_type in ["image/jpeg", "image/png"]:
            image = Image.open(uploaded_file)
            preview = f"Uploaded Image (Type: {file_type})"
            content = image

        elif file_type == "text/plain":
            content = uploaded_file.read().decode("utf-8")
            preview = f"Text File: First 100 characters\n{content[:100]}..."

        elif file_type in ["text/csv", "application/vnd.ms-excel"]:
            df = pd.read_csv(uploaded_file)
            content = df
            preview = f"CSV File: {len(df)} rows, {len(df.columns)} columns"

        elif file_type in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            "application/vnd.ms-excel"
        ]:
            df = pd.read_excel(uploaded_file)
            content = df
            preview = f"Excel File: {len(df)} rows, {len(df.columns)} columns"

        elif file_type == "application/pdf":
            reader = PdfReader(uploaded_file)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
            preview = f"PDF File: First 100 characters\n{content[:100]}..."

        else:
            st.error(f"Unsupported file type: {file_type}")
            return None, None

        return content, preview

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None, None

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

if 'uploaded_file_content' not in st.session_state:
    st.session_state.uploaded_file_content = None
    st.session_state.uploaded_file_preview = None

st.title("💬 Interlink AI")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if st.session_state.uploaded_file_preview:
    with st.chat_message("assistant"):
        st.markdown(f"📎 File Uploaded: {st.session_state.uploaded_file_preview}")

col1, col2 = st.columns([0.9, 0.1])

with col2:
    uploaded_file = st.file_uploader(
        "Upload files", 
        type=["jpg", "png", "pdf", "txt", "csv", "xlsx", "xls"],
        label_visibility="collapsed",
        key="file_uploader"
    )

if uploaded_file is not None:
    st.session_state.uploaded_file_content, st.session_state.uploaded_file_preview = handle_file_upload(uploaded_file)
    st.experimental_rerun()

with col1:
    prompt = st.chat_input("What can I help you with?")

if prompt:
    st.chat_message("user").markdown(prompt)
    
    full_prompt = prompt
    if st.session_state.uploaded_file_content is not None:
        if isinstance(st.session_state.uploaded_file_content, pd.DataFrame):
            full_prompt += f"\n\n[Uploaded File Content: DataFrame with {len(st.session_state.uploaded_file_content)} rows and {len(st.session_state.uploaded_file_content.columns)} columns]\n"
            full_prompt += st.session_state.uploaded_file_content.to_string()
        elif isinstance(st.session_state.uploaded_file_content, Image.Image):
            full_prompt += "\n\n[Uploaded File: Image]"
        else:
            full_prompt += f"\n\n[Uploaded File Content]:\n{st.session_state.uploaded_file_content}"
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            response = st.session_state.chat_session.send_message(full_prompt)
            
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

if st.session_state.uploaded_file_content is not None:
    st.session_state.uploaded_file_content = None
    st.session_state.uploaded_file_preview = None
