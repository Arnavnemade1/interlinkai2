st.markdown("""
<style>
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
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
    }

    /* Make chat messages more visible and bold */
    .stChatMessage {
        background-color: white !important;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-weight: bold !important;
        color: black !important;  /* Make text black */
    }

    .stChatMessage.assistant {
        background-color: #f0f4ff !important;
        color: black !important; /* Ensure the assistant's text is also black */
    }

    .stChatMessage.user {
        background-color: white !important;
        color: black !important; /* Ensure the user's text is black */
    }

    /* Make title clearly visible */
    h1 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        font-size: 2.5rem !important;
        font-weight: bold !important;
        margin-bottom: 2rem !important;
        background-color: rgba(0, 0, 0, 0.2);
        padding: 1rem;
        border-radius: 10px;
        display: inline-block;
    }

    /* Style buttons */
    .stButton button {
        background: #4f46e5 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        background: #4338ca !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2) !important;
    }

    /* Style file uploader */
    .stFileUploader {
        background-color: white !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        margin: 1rem 0 !important;
    }

    .stFileUploader button {
        background: #6366f1 !important;
        color: white !important;
    }

    .stFileUploader button:hover {
        background: #4f46e5 !important;
    }

    /* Make input area clearly visible */
    .stChatInputContainer {
        background-color: white !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        margin-top: 1rem !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }

    /* Style chat input */
    .stChatInput {
        border-color: #6366f1 !important;
    }

    .stChatInput:focus {
        box-shadow: 0 0 0 2px #4f46e5 !important;
    }

    /* Make upload text visible */
    .stFileUploader label {
        color: black !important;
        font-weight: bold !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.5);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.7);
    }

    /* Container styling */
    .main {
        padding: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)
