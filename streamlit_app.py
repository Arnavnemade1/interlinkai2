import streamlit as st
import google.generativeai as genai
import time
import os
from PIL import Image
from io import BytesIO

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

genai.configure(api_key=GEMINI_API_KEY)

# Configuration settings
GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048,
}

SYSTEM_INSTRUCTION = """You are InspireX AI, a helpful and creative assistant.
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
            .stApp {
                background-color: #ffffff;
            }

            .main {
                background-color: #ffffff;
            }

            .stChatMessage {
                background-color: #f8f9fa !important;
                border-radius: 15px;
                margin: 10px 0;
                padding: 15px;
                border: 1px solid #e9ecef;
            }

            /* Make sidebar look better */
            .css-1d391kg {
                background-color: #f8f9fa;
            }

            .chat-history-item {
                padding: 12px 15px;
                margin: 8px 0;
                border-radius: 10px;
                background-color: #ffffff;
                cursor: pointer;
                transition: all 0.2s ease;
                border: 1px solid #e9ecef;
            }

            .chat-history-item:hover {
                background-color: #f1f3f5;
                transform: translateX(5px);
            }

            .drop-zone {
                border: 2px dashed #6c757d;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 10px 0;
                background-color: #ffffff;
                transition: all 0.3s ease;
            }

            .drop-zone:hover {
                border-color: #343a40;
                background-color: #f8f9fa;
            }

            /* Header styling */
            .chat-header {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 24px;
                background-color: #ffffff;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }

            /* Button styling */
            .stButton button {
                border-radius: 8px;
                padding: 4px 12px;
                border: 1px solid #e9ecef;
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
        
        # Header with controls
        col1, col2, col3 = st.columns([8, 2, 2])
        with col1:
            st.title("💬 InspireX AI")
        with col2:
            if st.button("📸 Share Image", key="image_toggle", type="primary"):
                st.session_state.show_image_upload = not st.session_state.show_image_upload
                st.rerun()
        
        # Sidebar with chat history
        self.display_chat_history()
        
        # Chat interface
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "image" in message:
                    st.image(message["image"], caption="Shared Image", use_column_width=True)
        
        # Handle image upload
        uploaded_file = self.handle_image_upload()
        image = None
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Chat input
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
