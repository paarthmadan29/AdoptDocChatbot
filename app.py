import json
import streamlit as st

from llm import GeminiBot

# Set page configuration
st.set_page_config(
    page_title="TrueFoundry Documentation Assistant",
    page_icon="🤖",
    layout="wide"
)

# Apply custom CSS
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #f0f2f6;
    }
    .chat-message.bot {
        background-color: #e6f7ff;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-message .message {
        flex-grow: 1;
    }
    .stTextInput {
        margin-bottom: 0.5rem;
    }
    .main-header {
        text-align: center;
        padding-bottom: 1rem;
        border-bottom: 1px solid #eee;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'bot' not in st.session_state:
    st.session_state.bot = None


def display_messages():
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.container():
                st.markdown(f"""
                <div class="chat-message user">
                    <img class="avatar" src="https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y">
                    <div class="message">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.container():
                st.markdown(f"""
                <div class="chat-message bot">
                    <img class="avatar" src="https://api.dicebear.com/7.x/bottts/svg?seed=gemini">
                    <div class="message">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>TrueFoundry Documentation Assistant</h1>", unsafe_allow_html=True)

with st.sidebar:
    data_path = "data/data.json"
    
    model_choice = st.selectbox(
        "Gemini Model",
        ["gemini-2.5-flash-preview-04-17", "gemini-2.5-pro-preview-03-25", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=1
    )
    
    if st.button("Initialize Bot"):
        try:
            with open(data_path, "r") as f:
                data = json.load(f)
            context = json.dumps(data)
            
            # Initialize bot with the context
            st.session_state.bot = GeminiBot(context=context, model=model_choice)
            st.success("Bot initialized successfully with JSON data!")
            st.session_state.messages = []
        except FileNotFoundError:
            st.error(f"File not found: {data_path}")
        except json.JSONDecodeError:
            st.error("Invalid JSON data")
        except Exception as e:
            st.error(f"Error initializing bot: {str(e)}")

if st.session_state.bot is None:
    st.info("Please initialize the bot with context information in the sidebar.")
else:
    display_messages()
    
    with st.container():
        user_input = st.text_input("Ask a question:", key="user_input")
        col1, col2 = st.columns([1, 5])
        with col1:
            send_button = st.button("Send")
        with col2:
            clear_button = st.button("Clear Chat")
    
    if send_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.bot.query(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.rerun()
    
    if clear_button:
        st.session_state.messages = []
        st.rerun()
