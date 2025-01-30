class ChatApp:
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
                    st.info("Due to browser security restrictions, please use the file uploader to share images from your clipboard. Copy your image, then click 'Browse files' and paste with Ctrl+V in the file picker dialog.")
            
            st.markdown("""
            <div class="drop-zone">
                📸 Drag & drop an image here<br>or<br>click 'Browse files' and paste in the file dialog
            </div>
            """, unsafe_allow_html=True)
            
        return uploaded_file
