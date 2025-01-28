import streamlit as st
import google.generativeai as genai
import time
import re
import os
from PIL import Image
import io
import base64

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

genai.configure(api_key=GEMINI_API_KEY)

# Set page config
st.set_page_config(
    page_title="𝙸𝚗𝚜𝚙𝚒𝚛𝚎𝚇 𝙰𝙸",
    layout="wide"
)

def get_color_scheme():
    colors = {
        "light": {
            "gradient": ["#9333EA", "#7C3AED", "#6D28D9", "#5B21B6", "#4C1D95", "#2E1065"],
            "text": "#1a1a1a",
            "background": "255, 255, 255",
            "chat_bg": "147, 51, 234"
        },
        "dark": {
            "gradient": ["#C084FC", "#A855F7", "#9333EA", "#7C3AED", "#6D28D9", "#5B21B6"],
            "text": "#ffffff",
            "background": "18, 18, 18",
            "chat_bg": "147, 51, 234"
        }
    }
    return colors["dark"] if st.session_state.get('dark_mode', False) else colors["light"]

def get_dynamic_styles():
    colors = get_color_scheme()
    gradient_colors = ", ".join(colors["gradient"])
    
    return f"""
<style>
    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    @keyframes glow {{
        0% {{ box-shadow: 0 0 5px rgba({colors["chat_bg"]}, 0.5); }}
        50% {{ box-shadow: 0 0 20px rgba({colors["chat_bg"]}, 0.8); }}
        100% {{ box-shadow: 0 0 5px rgba({colors["chat_bg"]}, 0.5); }}
    }}

    .stApp {{
        background: linear-gradient(-45deg, {gradient_colors});
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: {colors["text"]} !important;
    }}

    .stChatMessage {{
        background-color: rgba({colors["background"]}, 0.95) !important;
        color: {colors["text"]} !important;
    }}

    .stChatMessage p {{
        color: {colors["text"]} !important;
    }}

    .drop-zone {{
        border: 2px dashed rgba({colors["chat_bg"]}, 0.5);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
        background-color: rgba({colors["background"]}, 0.1);
        transition: all 0.3s ease;
    }}

    .drop-zone:hover {{
        border-color: rgba({colors["chat_bg"]}, 0.8);
        background-color: rgba({colors["background"]}, 0.2);
    }}

    .chat-history {{
        background-color: rgba({colors["background"]}, 0.95);
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
    }}

    .chat-history-item {{
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }}

    .chat-history-item:hover {{
        background-color: rgba({colors["chat_bg"]}, 0.1);
    }}

    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
    }}
</style>
"""

def handle_image_upload():
    uploaded_file = st.file_uploader("Drop an image here or paste from clipboard", type=["jpg", "jpeg", "png"], key="file_uploader")
    
    st.markdown("""
    <div class="drop-zone" id="paste-zone" ondrop="handleDrop(event)" ondragover="handleDragOver(event)">
        Drag & drop an image here or paste from clipboard (Ctrl+V)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <script>
    document.addEventListener('paste', function(e) {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                const reader = new FileReader();
                reader.onload = function(e) {
                    window.parent.postMessage({
                        type: 'image-upload',
                        data: e.target.result
                    }, '*');
                };
                reader.readAsDataURL(blob);
            }
        }
    });

    function handleDrop(e) {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                window.parent.postMessage({
                    type: 'image-upload',
                    data: e.target.result
                }, '*');
            };
            reader.readAsDataURL(files[0]);
        }
    }

    function handleDragOver(e) {
        e.preventDefault();
    }
    </script>
    """, unsafe_allow_html=True)
    
    return uploaded_file

def initialize_session_state():
    if 'chat_model' not in st.session_state:
        st.session_state.chat_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
        )

    if 'chat_session' not in st.session_state:
        st.session_state.chat_session = st.session_state.chat_model.start_chat(history=[])

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = None

    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def create_new_chat():
    chat_id = len(st.session_state.chat_history)
    st.session_state.chat_history.append({
        'id': chat_id,
        'messages': [],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    st.session_state.chat_session = st.session_state.chat_model.start_chat(history=[])

def load_chat(chat_id):
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = st.session_state.chat_history[chat_id]['messages']
    st.session_state.chat_session = st.session_state.chat_model.start_chat(history=[])

def main():
    initialize_session_state()
    st.markdown(get_dynamic_styles(), unsafe_allow_html=True)

    col1, col2 = st.columns([1, 11])
    with col1:
        if st.button("🌓" if st.session_state.dark_mode else "🌞"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    with st.sidebar:
        st.title("Chat History")
        if st.button("New Chat"):
            create_new_chat()
            st.rerun()
        
        for chat in reversed(st.session_state.chat_history):
            if st.button(f"Chat {chat['id']} - {chat['timestamp']}", key=f"chat_{chat['id']}"):
                load_chat(chat['id'])
                st.rerun()

    st.title("💬 InspireX AI")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            if "image" in message:
                st.image(message["image"], caption="Shared Image", use_column_width=True)

    uploaded_file = handle_image_upload()
    image = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    prompt = st.chat_input("What can I help you with?")

    if prompt:
        st.chat_message("user").markdown(prompt)
        if image:
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt,
                "image": image
            })
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.current_chat_id is None:
            create_new_chat()
        st.session_state.chat_history[st.session_state.current_chat_id]['messages'] = st.session_state.messages

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                response = st.session_state.chat_model.generate_content([prompt])
                response_text = response.result.candidates[0].content.parts[0].text
                
                message_placeholder.markdown(response_text, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.session_state.chat_history[st.session_state.current_chat_id]['messages
