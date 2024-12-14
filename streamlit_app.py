def main():
    initialize_session_state()

    st.title("💬 Interlink AI")

    # Displaying the assistant's responses first
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # Display the uploaded file preview if available
    if st.session_state.uploaded_file_preview:
        with st.chat_message("assistant"):
            st.markdown(f"📎 File Uploaded: {st.session_state.uploaded_file_preview}")

    col1, col2 = st.columns([0.9, 0.1])

    with col2:
        # File uploader section
        uploaded_file = st.file_uploader(
            "Upload files", 
            type=["jpg", "png", "pdf", "txt", "csv", "xlsx", "xls"],
            label_visibility="collapsed",
            key="file_uploader"
        )

    # File handling
    if uploaded_file is not None:
        st.session_state.uploaded_file_content, st.session_state.uploaded_file_preview = handle_file_upload(uploaded_file)

    with col1:
        # Display the text box for user input only after assistant's response
        prompt = st.chat_input("What can I help you with?")

    if prompt:
        st.chat_message("user").markdown(prompt)
        
        # Creating the full prompt with uploaded file content, if any
        full_prompt = prompt
        if st.session_state.uploaded_file_content is not None:
            if isinstance(st.session_state.uploaded_file_content, pd.DataFrame):
                full_prompt += f"\n\n[Uploaded File Content: DataFrame with {len(st.session_state.uploaded_file_content)} rows and {len(st.session_state.uploaded_file_content.columns)} columns]\n"
                full_prompt += st.session_state.uploaded_file_content.to_string()
            else:
                full_prompt += f"\n\n[Uploaded File Content]:\n{st.session_state.uploaded_file_content}"
        
        # Add user message to session history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Respond from the assistant
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Send the prompt to the model
                response = st.session_state.chat_session.send_message(full_prompt)
                
                formatted_response = process_response(response.text)

                # Break response into chunks for gradual rendering
                chunks = []
                for line in formatted_response.split('\n'):
                    chunks.extend(line.split(' '))
                    chunks.append('\n')

                # Gradually display the response
                for chunk in chunks:
                    if chunk != '\n':
                        full_response += chunk + ' '
                    else:
                        full_response += chunk
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                
                message_placeholder.markdown(full_response, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if "rate_limit" in str(e).lower():
                    st.warning("The API rate limit has been reached. Please wait a moment before trying again.")
                else:
                    st.warning("Please try again in a moment.")

        # Reset file upload after processing
        st.session_state.uploaded_file_content = None
        st.session_state.uploaded_file_preview = None
