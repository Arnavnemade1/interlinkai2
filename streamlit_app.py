# Add these imports at the top
import streamlit.components.v1 as components

# In the ChatApp class, update the get_styles method:
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
            }

            .glowing-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 3em;
                color: white;
                animation: glow 2s ease-in-out infinite;
                text-transform: uppercase;
                letter-spacing: 3px;
                margin: 0;
                padding: 20px;
                background: rgba(0, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(5px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .stChatMessage {
                background-color: rgba(32, 33, 35, 0.9
