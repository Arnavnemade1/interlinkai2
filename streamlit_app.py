import streamlit as st
import google.generativeai as genai
import time
import re
import os
from PIL import Image

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

genai.configure(api_key=GEMINI_API_KEY)

# Set page config
st.set_page_config(
    page_title="𝙸𝚗𝚜𝚙𝚒𝚛𝚎𝚇 𝙰𝙸",
    page_icon="./favicon.ico",
    layout="wide"
)

# Custom CSS for styling with animated gradient background
st.markdown("""
<style>
    @keyframes gradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    @keyframes sparkle {
        0% { opacity: 0; }
        50% { opacity: 1; }
        100% { opacity: 0; }
    }

    .stApp {
        background: linear-gradient(
            -45deg, 
            #7c83fd,
            #96baff,
            #4f46e5,
            #818cf8,
            #6366f1,
            #4338ca
        );
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        position: relative;
        overflow: hidden;
    }

    /* Create sparkle effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at center, rgba(255,255,255,0.2) 0%, transparent 60%);
        pointer-events: none;
        opacity: 0;
        animation: sparkle 3s infinite;
    }

    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .stChatMessage.assistant {
        background-color: rgba(221, 225, 255, 0.9) !important;
        color: #000000;
    }

    .stChatMessage.user {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #000000;
    }

    /* Glowing effect for buttons */
    .stButton button {
        background: linear-gradient(45deg, #4f46e5, #6366f1);
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.3);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(79, 70, 229, 0.5);
    }

    .stFileUploader button {
        background: linear-gradient(45deg, #6366f1, #818cf8);
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
    }

    .stFileUploader button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
    }

    /* Enhance text contrast and readability */
    .stMarkdown {
        color: #000000 !important;
    }

    .stTextInput label {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(0,0,0,0.2);
    }

    .stTextInput input {
        color: #000000 !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
    }

    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(0,0,0,0.2);
    }

    .stChatFloatingInputContainer {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 15px;
        padding: 5px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.5);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.7);
    }
</style>
""", unsafe_allow_html=True)

# Rest of your original code remains the same
[Previous Python code from initialize_session_state() to the end remains exactly the same...]
