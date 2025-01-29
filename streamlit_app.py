import streamlit as st
import google.generativeai as genai
import time
import os
from PIL import Image

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
                
    def get_color_scheme(self):
        colors = {
            "light": {
                "gradient": ["#9333EA", "#7C3AED", "#6D28D9", "#5B21B6", "#4C1D95", "#2E1065"],
                "text": "#1a1a1a",
                "background": "255, 255, 255",
                "chat_bg": "147, 51, 234",
                "message_bg": "248, 249, 250"
            },
            "dark": {
                "gradient": ["#C084FC", "#A855F7", "#9333EA", "#7C3AED", "#6D28D9", "#5B21B6"],
                "text": "#ffffff",
                "background": "18, 18, 18",
                "chat_bg": "147, 51, 234",
                "message_bg": "32, 33, 35"
            }
        }
        return colors["dark"] if st.session_state.dark_mode else colors["light"]
    
    def get_styles(self):
        colors = self.get_color_scheme()
        gradient_colors = ", ".join(colors["gradient"])
        
        return f"""
        <style>
            @keyframes gradient {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}

            @keyframes float {{
                0% {{ transform: translateY(0px); }}
                50% {{ transform: translateY(-10px); }}
                100% {{ transform: translateY(0px); }}
            }}

            .stApp {{
                background: linear-gradient(-45deg, {gradient_colors});
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
            }}

            .header-container {{
                text-align: center;
                padding: 2rem 0;
                margin-bottom: 2rem;
            }}

            .main-title {{
                font-size: 4rem;
                font-weight: bold;
                background: linear-gradient(to right, {colors["gradient"][0]}, {colors["gradient"][2]}, {colors["gradient"][4]});
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
                padding: 0;
                font-family: 'Helvetica Neue', sans-serif;
                letter-spacing: 2px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }}

            .title-emoji {{
                font-size: 3.5rem;
                margin-right: 0.5rem;
                vertical-align: middle;
                display: inline-block;
                animation: float 3s ease-in-out infinite;
            }}

            .stChatMessage {{
                background-color: rgba({colors["message_bg"]}, 0.95) !important;
                border-radius: 15px;
                margin: 10px 0;
                padding: 15px;
            }}

            .stChatMessage p, .stChatMessage span {{
                color: {colors["text"]} !important;
            }}

            .upload-container {{
                background: rgba({colors["message_bg"]}, 0.95);
                padding: 20px;
                border-radius: 15px;
                margin-top: 1rem;
            }}

            .drop-zone {{
                border: 2px dashed rgba({colors["chat_bg"]}, 0.5);
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 10px 0;
                background-color: rgba({colors["background"]}, 0.1);
                transition: all 0.3s ease;
                color: {colors["text"]};
            }}

            .drop-zone:hover {{
                border-color: rgba({colors["chat_bg"]}, 0.8);
                background-color: rgba({colors["background"]}, 0.2);
            }}

            .custom-button {{
                background-color: rgba({colors["chat_bg"]}, 0.8);
                color: {colors["text"]};
                border: none;
                padding: 8px 15px;
                border-radius: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 5px;
                font-size: 16px;
            }}

            .custom-button:hover {{
                background-color: rgba({colors["chat_bg"]}, 1);
                transform: translateY(-2px);
            }}
            
            .st-emotion-cache-1r4qj8v {{
                color: {colors["text"]} !important;
            }}

            .chat-input {{
                margin-top: 2rem;
            }}
        </style>
        """

    def handle_image_upload(self):
        uploaded_file = None
        
        if st.session_state.show_image_upload:
            with st.container():
                st.markdown('<div class="upload-container">', unsafe_allow_html=True)
                uploaded_file = st.file_uploader(
                    "Choose an image",
                    type=["jpg", "jpeg", "png"],
                    label_visibility="collapsed"
                )
                
                st.markdown("""
                <div class="drop-zone">
                    📸 Drag & drop an image here or paste from clipboard (Ctrl+V)
                </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
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
        
    def run(self):
        st.markdown(self.get_styles(), unsafe_allow_html=True)
        
        # Custom buttons in header
        col1, col2, col3 = st.columns([8, 2, 2])
        with col2:
            if st.button("📸 Share Image", key="image_toggle", type="primary"):
                st.session_state.show_image_upload = not st.session_state.show_image_upload
                st.rerun()
        with col3:
            if st.button("🌓 Toggle Theme" if st.session_state.dark_mode else "🌞 Toggle Theme", 
                        key="theme_toggle", type="primary"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        # Centered header with enhanced styling
        st.markdown("""
            <div class="header-container">
                <h1 class="main-title">
                    <span class="title-emoji">💬</span>
                    InspireX AI
                </h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        with st.sidebar:
            st.title("Chat History")
            if st.button("New Chat", type="primary"):
                self.create_new_chat()
                st.rerun()
            
            for chat in reversed(st.session_state.chat_history):
                if st.button(f"Chat {chat['id']} - {chat['timestamp']}", 
                           key=f"chat_{chat['id']}", type="secondary"):
                    self.load_chat(chat['id'])
                    st.rerun()
        
        # Display messages
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
