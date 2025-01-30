import streamlit as st
import google.generativeai as genai
import time
import os
from PIL import Image
import base64
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
            'show_image_upload': False,
            'clipboard_image': None
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
                "message_bg": "248, 249, 250",
                "sidebar_bg": "255, 255, 255",
                "chat_item_hover": "243, 244, 246"
            },
            "dark": {
                "gradient": ["#C084FC", "#A855F7", "#9333EA", "#7C3AED", "#6D28D9", "#5B21B6"],
                "text": "#ffffff",
                "background": "18, 18, 18",
                "chat_bg": "147, 51, 234",
                "message_bg": "32, 33, 35",
                "sidebar_bg": "24, 24, 24",
                "chat_item_hover": "39, 39, 39"
            }
        }
        return colors["dark"] if st.session_state.dark_mode else colors["light"]
    
    def get_styles(self):
        colors = self.get_color_scheme()
        gradient_colors = ", ".join(colors["gradient"])
        
        return f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
            
            * {{
                font-family: 'Inter', sans-serif;
            }}
            
            @keyframes gradient {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}

            .stApp {{
                background: linear-gradient(-45deg, {gradient_colors});
                background-size: 400% 400%;
                animation: gradient 15s ease infinite;
            }}

            .stChatMessage {{
                background-color: rgba({colors["message_bg"]}, 0.95) !important;
                border-radius: 15px;
                margin: 10px 0;
                padding: 15px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}

            .stChatMessage p, .stChatMessage span {{
                color: {colors["text"]} !important;
            }}

            /* Sidebar styling */
            .st-emotion-cache-1r4qj8v {{
                color: {colors["text"]} !important;
                background-color: rgba({colors["sidebar_bg"]}, 0.95) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }}

            .chat-history-item {{
                padding: 12px 15px;
                margin: 8px 0;
                border-radius: 10px;
                background-color: rgba({colors["message_bg"]}, 0.95);
                cursor: pointer;
                transition: all 0.2s ease;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            .chat-history-item:hover {{
                background-color: rgba({colors["chat_item_hover"]}, 0.95);
                transform: translateX(5px);
            }}

            .chat-timestamp {{
                font-size: 12px;
                opacity: 0.7;
            }}

            /* Upload container styling */
            .upload-container {{
                position: fixed;
                bottom: 140px;
                right: 20px;
                width: 300px;
                background: rgba({colors["message_bg"]}, 0.95);
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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

            .drop-zone.dragover {{
                border-color: rgba({colors["chat_bg"]}, 1);
                background-color: rgba({colors["background"]}, 0.2);
                transform: scale(1.02);
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
                display: flex;
                align-items: center;
                gap: 8px;
            }}

            .custom-button:hover {{
                background-color: rgba({colors["chat_bg"]}, 1);
                transform: translateY(-2px);
            }}

            /* Header styling */
            .chat-header {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 24px;
            }}

            .chat-header h1 {{
                margin: 0;
                color: {colors["text"]};
            }}
        </style>

        <script>
            // Enable clipboard paste
            document.addEventListener('paste', function(e) {{
                if (e.clipboardData.files.length > 0) {{
                    const file = e.clipboardData.files[0];
                    if (file.type.startsWith('image/')) {{
                        const reader = new FileReader();
                        reader.onload = function(event) {{
                            const base64Data = event.target.result.split(',')[1];
                            window.clipboardData = base64Data;
                        }};
                        reader.readAsDataURL(file);
                    }}
                }}
            }});

            // Enable drag and drop highlighting
            document.addEventListener('dragover', function(e) {{
                const dropZone = document.querySelector('.drop-zone');
                if (dropZone) {{
                    dropZone.classList.add('dragover');
                }}
            }});

            document.addEventListener('dragleave', function(e) {{
                const dropZone = document.querySelector('.drop-zone');
                if (dropZone) {{
                    dropZone.classList.remove('dragover');
                }}
            }});
        </script>
        """

    def handle_image_upload(self):
        uploaded_file = None
        
        if st.session_state.show_image_upload:
            uploaded_file = st.file_uploader(
                "Choose an image",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed"
            )
            
            # Handle clipboard paste
            if 'clipboard_image' in st.session_state and st.session_state.clipboard_image:
                try:
                    image_data = base64.b64decode(st.session_state.clipboard_image)
                    uploaded_file = BytesIO(image_data)
                    st.session_state.clipboard_image = None
                except:
                    pass
            
            st.markdown("""
            <div class="drop-zone">
                📸 Drag & drop an image here<br>or<br>paste from clipboard (Ctrl+V)
            </div>
            """, unsafe_allow_html=True)
            
        return uploaded_file

    def display_chat_history(self):
        st.sidebar.markdown("""
            <h2 style='margin-bottom: 20px;'>Chat History</h2>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("+ New Chat", type="primary", key="new_chat"):
            self.create_new_chat()
            st.rerun()
        
        st.sidebar.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        for chat in reversed(st.session_state.chat_history):
            chat_preview = (chat['messages'][0]['content'][:50] + '...') if chat['messages'] else 'Empty chat'
            st.sidebar.markdown(f"""
                <div class='chat-history-item' onclick='handleChatClick({chat["id"]})'>
                    <div style='font-weight: 500;'>Chat {chat['id'] + 1}</div>
                    <div class='chat-timestamp'>{chat['timestamp']}</div>
                    <div style='margin-top: 5px; opacity: 0.8;'>{chat_preview}</div>
                </div>
            """, unsafe_allow_html=True)

    def run(self):
        st.markdown(self.get_styles(), unsafe_allow_html=True)
        
        # Header with controls
        col1, col2, col3 = st.columns([8, 2, 2])
        with col1:
            st.markdown("""
                <div class='chat-header'>
                    <h1>💬 InspireX AI</h1>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("📸 Share Image", key="image_toggle", type="primary"):
                st.session_state.show_image_upload = not st.session_state.show_image_upload
                st.rerun()
        with col3:
            if st.button("🌓 Toggle Theme" if st.session_state.dark_mode else "🌞 Toggle Theme", 
                        key="theme_toggle", type="primary"):
                st.session_state.dark_mode = not st.session_state.dark_mode
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
