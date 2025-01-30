import streamlit as st
import google.generativeai as genai
import time
import os
from PIL import Image
from io import BytesIO
import streamlit.components.v1 as components

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
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
            
            @keyframes gradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            @keyframes glow {
                0% { text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF, 0 0 30px #9333EA; }
                50% { text-shadow: 0 0 20px #00FFFF, 0 0 30px #00FFFF, 0 0 40px #9333EA; }
                100% { text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF, 0 0 30px #9333EA; }
            }

            .stApp {
                background: linear-gradient(-45deg, #9333EA, #7C3AED, #6D28D9, #5B21B6, #4C1D95, #2E1065, #0891B2);
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
            }

            .title-container {
                text-align: center;
                margin: 20px 0;
                padding: 20px;
                background: rgba(0, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(5px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
            }

            .glowing-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 3em;
                color: white;
                animation: glow 2s ease-in-out infinite;
                text-transform: uppercase;
                letter-spacing: 3px;
                margin: 0;
            }

            .stChatMessage {
                background-color: rgba(32, 33, 35, 0.9) !important;
                border-radius: 15px;
                margin: 10px 0;
                padding: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.1);
            }

            .stChatMessage p, .stChatMessage span {
                color: white !important;
            }

            /* Sidebar styling */
            section[data-testid="stSidebar"] {
                background-color: rgba(32, 33, 35, 0.9);
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 5px 0 15px rgba(0, 255, 255, 0.1);
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
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
            }

            .drop-zone {
                border: 2px dashed rgba(0, 255, 255, 0.5);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 10px 0;
                background-color: rgba(32, 33, 35, 0.9);
                transition: all 0.3s ease;
                color: white;
            }

            .drop-zone:hover {
                border-color: rgba(0, 255, 255, 0.8);
                background-color: rgba(55, 56, 58, 0.9);
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
            }

            /* Button styling */
            .stButton button {
                background-color: rgba(8, 145, 178, 0.8) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 8px 16px !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
            }

            .stButton button:hover {
                background-color: rgba(8, 145, 178, 1) !important;
                transform: translateY(-2px);
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
            }

            /* Chat input styling */
            .stTextInput input {
                background-color: rgba(32, 33, 35, 0.9) !important;
                color: white !important;
                border: 1px solid rgba(0, 255, 255, 0.3) !important;
                border-radius: 8px !important;
                padding: 10px 15px !important;
            }

            .stTextInput input:focus {
                border-color: rgba(0, 255, 255, 0.6) !important;
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.2) !important;
            }

            /* Markdown text color */
            .st-emotion-cache-1v0mbdj.e115fcil1, 
            .st-emotion-cache-1v0mbdj p,
            .st-emotion-cache-1v0mbdj span,
            h1, h2, h3, p {
                color: white !important;
            }

            /* File uploader styling */
            .stFileUploader {
                background-color: rgba(32, 33, 35, 0.9) !important;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid rgba(0, 255, 255, 0.3);
            }

            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }

            ::-webkit-scrollbar-track {
                background: rgba(32, 33, 35, 0.9);
            }

            ::-webkit-scrollbar-thumb {
                background: rgba(0, 255, 255, 0.5);
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: rgba(0, 255, 255, 0.8);
            }
        </style>

        <script>
        // Function to handle clipboard paste
        function setupClipboardPaste() {
            document.addEventListener('paste', async (e) => {
                const items = e.clipboardData.items;
                for (let i = 0; i < items.length; i++) {
                    if (items[i].type.indexOf('image') !== -1) {
                        const blob = items[i].getAsFile();
                        const reader = new FileReader();
                        reader.onload = function(event) {
                            const fileInput = document.querySelector('input[type="file"]');
                            if (fileInput) {
                                // Create a new file from the blob
                                const file = new File([blob], "pasted-image.png", { type: "image/png" });
                                
                                // Create a new DataTransfer object and add the file
                                const dataTransfer = new DataTransfer();
                                dataTransfer.items.add(file);
                                
                                // Set the file input's files
                                fileInput.files = dataTransfer.files;
                                
                                // Dispatch change event
                                const event = new Event('change', { bubbles: true });
                                fileInput.dispatchEvent(event);
                            }
                        };
                        reader.readAsDataURL(blob);
                    }
                }
            });
        }

        // Set up the clipboard paste handler when the document is ready
        if (document.readyState === 'complete') {
            setupClipboardPaste();
        } else {
            window.addEventListener('load', setupClipboardPaste);
        }
        </script>
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
                if st.button("📋 Paste (Ctrl+V)", type="primary"):
                    st.info("Just press Ctrl+V anywhere on the page!")
            
            st.markdown("""
            <div class="drop-zone">
                📸 Drag & drop an image here<br>or<br>paste from clipboard (Ctrl+V)
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
        st.sidebar.markdown("""
            <div class='title-container' style='text-align: center; margin-bottom: 20px;'>
                <h2 style='color: white; font-family: Orbitron, sans-serif;'>Chat History</h2>
            </div>
        """, unsafe_allow_html=True)
        
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
        
        # Centered title with glow effect
        st.markdown("""
            <div class='title-container'>
                <h1 class='glowing-title'>💬 InspireX AI</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Image upload button
        col1, col2, col3 = st.columns([4, 4, 4])
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
        st.chat_message("user
