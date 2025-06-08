import streamlit as st
import google.generativeai as genai
import time
import os
from PIL import Image
from io import BytesIO

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

genai.configure(api_key=GEMINI_API_KEY)

GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048,
}

SYSTEM_INSTRUCTION = """You are InspireX AI, a helpful and creative assistant meant to help people answer problems relating to public health and safety.
Provide clear, concise, and accurate responses while maintaining a friendly tone.
Format responses using Markdown for better readability when appropriate."""

class ChatApp:
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        
    def setup_page_config(self):
        st.set_page_config(
            page_title="InspireX AI",
            layout="wide"
        )
        
    def initialize_session_state(self):
        if 'chat_model' not in st.session_state:
            st.session_state.chat_model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=GENERATION_CONFIG,
                system_instruction=SYSTEM_INSTRUCTION,
            )
            
        defaults = {
            'chat_session': st.session_state.chat_model.start_chat(history=[]),
            'messages': [],
            'chat_history': [],
            'current_chat_id': None,
            'dark_mode': False,
            'show_image_upload': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def get_styles(self):
        return """
        <style>
            @keyframes gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .stApp {
                background: linear-gradient(-45deg, #9333EA, #7C3AED, #6D28D9, #5B21B6, #4C1D95, #2E1065);
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
            }

            .stChatMessage {
                background-color: rgba(32, 33, 35, 0.9) !important;
                border-radius: 15px;
                margin: 10px 0;
                padding: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: white !important;
            }

            .stChatMessage p, .stChatMessage span {
                color: white !important;
            }

            section[data-testid="stSidebar"] {
                background-color: rgba(32, 33, 35, 0.9);
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }

            .chat-history-item {
                padding: 12px 15px;
                margin: 8px 0;
                border-radius: 10px;
                background-color: rgba(55, 56, 58, 0.9);
                cursor: pointer;
                transition: all 0.2s ease;
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: white;
            }

            .chat-history-item:hover {
                background-color: rgba(75, 76, 78, 0.9);
                transform: translateX(5px);
            }

            .drop-zone {
                border: 2px dashed rgba(147, 51, 234, 0.5);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 10px 0;
                background-color: rgba(32, 33, 35, 0.9);
                transition: all 0.3s ease;
                color: white;
            }

            .drop-zone:hover {
                border-color: rgba(147, 51, 234, 0.8);
                background-color: rgba(55, 56, 58, 0.9);
            }

            .chat-header {
                margin-bottom: 24px;
                color: white;
            }

            .stButton button {
                background-color: rgba(147, 51, 234, 0.8) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 4px 12px !important;
            }

            .stButton button:hover {
                background-color: rgba(147, 51, 234, 1) !important;
                transform: translateY(-2px);
            }

            .stTextInput input {
                background-color: rgba(32, 33, 35, 0.9) !important;
                color: white !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
            }

            .st-emotion-cache-1v0mbdj.e115fcil1, 
            .st-emotion-cache-1v0mbdj p,
            .st-emotion-cache-1v0mbdj span,
            h1, h2, h3, p {
                color: white !important;
            }

            .stFileUploader {
                background-color: rgba(32, 33, 35, 0.9) !important;
                border-radius: 10px;
                padding: 10px;
            }
        </style>
        """

    def handle_image_upload(self):
        uploaded_file = None
        
        if st.session_state.show_image_upload:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                uploaded_file = st.file_uploader(
                    "Choose an image",
                    type=["jpg", "jpeg", "png"],
                    label_visibility="collapsed"
                )
            
            with col2:
                if st.button("📋 Paste from Clipboard"):
                    st.info("To paste an image: Click 'Browse files' and paste with Ctrl+V in the file picker dialog")
            
            st.markdown("""
            <div class="drop-zone">
                📸 Drag & drop an image here<br>or<br>click 'Browse files' to upload
            </div>
            """, unsafe_allow_html=True)
            
        return uploaded_file
        
    def create_new_chat(self):
        chat_id = len(st.session_state.chat_history)
        st.session_state.chat_history.append({
            'id': chat_id,
            'messages': [],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = []
        st.session_state.chat_session = st.session_state.chat_model.start_chat(history=[])
        
    def load_chat(self, chat_id):
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = st.session_state.chat_history[chat_id]['messages']
        st.session_state.chat_session = st.session_state.chat_model.start_chat(history=[])
        
    def process_response(self, response_text):
        return response_text

    def display_chat_history(self):
        st.sidebar.title("Chat History")
        
        if st.sidebar.button("+ New Chat", type="primary", key="new_chat"):
            self.create_new_chat()
            st.rerun()
        
        st.sidebar.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        for chat in reversed(st.session_state.chat_history):
            chat_preview = (chat['messages'][0]['content'][:50] + '...') if chat['messages'] else 'Empty chat'
            if st.sidebar.button(
                f"Chat {chat['id'] + 1}\n{chat['timestamp']}\n{chat_preview}",
                key=f"chat_{chat['id']}",
                use_container_width=True
            ):
                self.load_chat(chat['id'])
                st.rerun()

    def run(self):
        st.markdown(self.get_styles(), unsafe_allow_html=True)
        
        col1, col2 = st.columns([10, 2])
        with col1:
            st.title("💬 InspireX AI")
        with col2:
            if st.button("📸 Share Image", key="image_toggle", type="primary"):
                st.session_state.show_image_upload = not st.session_state.show_image_upload
                st.rerun()
        
        self.display_chat_history()
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "image" in message:
                    st.image(message["image"], caption="Shared Image", use_column_width=True)
        
        uploaded_file = self.handle_image_upload()
        image = None
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        prompt = st.chat_input("What can I help you with?")
        
        if prompt:
            self._handle_chat_input(prompt, image)
    
    def _handle_chat_input(self, prompt, image=None):
        st.chat_message("user").markdown(prompt)
        message = {"role": "user", "content": prompt}
        if image:
            message["image"] = image
        st.session_state.messages.append(message)
        
        if st.session_state.current_chat_id is None:
            self.create_new_chat()
            
        st.session_state.chat_history[st.session_state.current_chat_id]['messages'] = \
            st.session_state.messages
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                response = (st.session_state.chat_model.generate_content([prompt, image]) 
                          if image else st.session_state.chat_session.send_message(prompt))
                
                formatted_response = self.process_response(response.text)
                message_placeholder.markdown(formatted_response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": formatted_response
                })
                st.session_state.chat_history[st.session_state.current_chat_id]['messages'] = \
                    st.session_state.messages
                    
            except Exception as e:
                message_placeholder.markdown(f"Error: {str(e)}")

if __name__ == "__main__":
    app = ChatApp()
    app.run()
