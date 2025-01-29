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
            'show_image_upload': False  # New state for image upload visibility
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
            /* Animation keyframes */
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

            /* Main app styling */
            .stApp {{
                background: linear-gradient(-45deg, {gradient_colors});
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
            }}

            /* Chat message styling */
            .stChatMessage {{
                background-color: rgba({colors["message_bg"]}, 0.95) !important;
                border-radius: 15px;
                margin: 10px 0;
                padding: 15px;
            }}

            .stChatMessage p, .stChatMessage span {{
                color: {colors["text"]} !important;
            }}

            /* Image upload controls */
            .image-controls {{
                position: fixed;
                bottom: 80px;
                right: 20px;
                z-index: 1000;
                display: flex;
                gap: 10px;
                background: rgba({colors["message_bg"]}, 0.95);
                padding: 10px;
                border-radius: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}

            .image-button {{
                background-color: rgba({colors["chat_bg"]}, 0.8);
                color: {colors["text"]};
                border: none;
                padding: 8px 15px;
                border-radius: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 5px;
            }}

            .image-button:hover {{
                background-color: rgba({colors["chat_bg"]}, 1);
                transform: translateY(-2px);
            }}

            /* Image upload zone */
            .upload-container {{
                position: fixed;
                bottom: 140px;
                right: 20px;
                width: 300px;
                background: rgba({colors["message_bg"]}, 0.95);
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                z-index: 1000;
                display: none;
            }}

            .upload-container.visible {{
                display: block;
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

            /* Theme toggle */
            .theme-toggle {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba({colors["message_bg"]}, 0.95);
                padding: 8px 15px;
                border-radius: 20px;
                cursor: pointer;
                z-index: 1000;
                color: {colors["text"]};
            }}
        </style>

        <script>
        // Toggle image upload container
        function toggleImageUpload() {{
            const container = document.querySelector('.upload-container');
            container.classList.toggle('visible');
        }}

        // Handle clipboard paste
        document.addEventListener('paste', function(e) {{
            const items = e.clipboardData.items;
            for (let i = 0; i < items.length; i++) {{
                if (items[i].type.indexOf('image') !== -1) {{
                    const blob = items[i].getAsFile();
                    const reader = new FileReader();
                    reader.onload = function(e) {{
                        window.parent.postMessage({{
                            type: 'image-upload',
                            data: e.target.result
                        }}, '*');
                    }};
                    reader.readAsDataURL(blob);
                }}
            }}
        }});
        </script>
        """

    def handle_image_upload(self):
        if not st.session_state.show_image_upload:
            return None

        # Create the image upload container
        st.markdown("""
        <div class="upload-container visible">
            <div class="drop-zone" id="paste-zone">
                📸 Drag & drop an image here or paste from clipboard (Ctrl+V)
            </div>
        </div>
        """, unsafe_allow_html=True)

        return st.file_uploader(
            "",
            type=["jpg", "jpeg", "png"],
            key="file_uploader",
            label_visibility="collapsed"
        )

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
        
        # Theme toggle
        st.markdown(f"""
        <div class="theme-toggle" onclick="document.querySelector('button[kind=secondary]').click()">
            {'🌓' if st.session_state.dark_mode else '🌞'}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Toggle Theme", key="theme_toggle", visible=False):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        
        # Image controls
        st.markdown("""
        <div class="image-controls">
            <button class="image-button" onclick="document.querySelector('button[kind=primary]').click()">
                📸 Share Image
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Toggle Image Upload", key="image_toggle", visible=False):
            st.session_state.show_image_upload = not st.session_state.show_image_upload
            st.rerun()
        
        # Sidebar
        with st.sidebar:
            st.title("Chat History")
            if st.button("New Chat"):
                self.create_new_chat()
                st.rerun()
            
            for chat in reversed(st.session_state.chat_history):
                if st.button(f"Chat {chat['id']} - {chat['timestamp']}", key=f"chat_{chat['id']}"):
                    self.load_chat(chat['id'])
                    st.rerun()
        
        st.title("💬 InspireX AI")
        
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
