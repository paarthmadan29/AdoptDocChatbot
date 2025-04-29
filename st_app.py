import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Documentation Chatbot",
    page_icon="💬",
    layout="centered"
)

st.title("TrueFoundry Doc Assistant")
st.markdown("Ask questions about the documentation!")

if "messages" not in st.session_state:
    st.session_state.messages = []

API_ENDPOINT = "http://localhost:8000/chat"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            st.markdown("**Sources:**")
            for source in message["sources"]:
                st.markdown(f"- [{source}]({source})")

if prompt := st.chat_input("Ask a question about the documentation..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "query": prompt,
                    "top_k": 4  # You can make this configurable
                }
                
                response = requests.post(
                    API_ENDPOINT,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    answer = response_data.get("answer", "")
                    sources = response_data.get("sources", [])
                    
                    message_placeholder.markdown(answer)
                    
                    if sources:
                        st.markdown("**Sources:**")
                        for source in sources:
                            st.markdown(f"- [{source}]({source})")

                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                else:
                    error_msg = f"Error: Received status code {response.status_code}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
            
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })

with st.sidebar:
    st.title("About")
    st.markdown("""
    This chatbot uses the TrueFoundry documentation to answer your questions.
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()