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

# Custom CSS for styling with enhanced contrast and vibrant colors
st.markdown("""
<style>
    .stChatInputContainer {
        display: flex;
        align-items: center;
    }
    /* Updated color scheme with better contrast */
    body {
        background-color: #e0e4ff;  /* More vibrant light purple-blue background */
        color: #1a1a2e;  /* Darker text for better contrast */
    }
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(78, 54, 226, 0.15);
    }
    .stChatMessage.assistant {
        background-color: #dde1ff;  /* Slightly darker background for assistant messages */
        color: #000000;  /* Black text for maximum contrast */
    }
    .stChatMessage.user {
        background-color: #ffffff;  /* White background for user messages */
        color: #000000;  /* Black text for maximum contrast */
    }
    .stButton button {
        background-color: #4f46e5;  /* Darker indigo button for better contrast */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
        font-weight: 500;  /* Slightly bolder text */
    }
    .stButton button:hover {
        background-color: #3c348d;  /* Even darker on hover */
    }
    .stFileUploader button {
        background-color: #6366f1;  /* Vibrant indigo for file uploader */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
        font-weight: 500;  /* Slightly bolder text */
    }
    .stFileUploader button:hover {
        background-color: #4f46e5;
    }
    .stApp {
        background: linear-gradient(135deg, #7c83fd 0%, #96baff 100%);  /* More vibrant gradient background */
    }
    /* Enhanced text contrast for all elements */
    .stMarkdown {
        color: #000000 !important;  /* Ensure markdown text is black */
    }
    .stTextInput label {
        color: #1a1a2e !important;  /* Dark color for input labels */
    }
    .stTextInput input {
        color: #000000 !important;  /* Black text for input fields */
    }
    /* Make titles and headers more visible */
    h1, h2, h3 {
        color: #1a1a2e !important;
        font-weight: 600 !important;
    }
    /* Add a white background to the chat container for better contrast */
    .stChatFloatingInputContainer {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Rest of the code remains the same
[... rest of the code remains unchanged ...]
