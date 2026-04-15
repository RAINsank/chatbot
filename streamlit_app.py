import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Chatbot Plus", page_icon="💬", layout="wide")

# Show title and description.
st.title("💬 Chatbot Plus")
st.write(
    "A richer chatbot demo with model tuning, system prompt control, and chat history export."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Settings")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    api_base_url = st.text_input("API Base URL", value="https://sg.uiuiapi.com/v1")
    model_name = st.selectbox(
        "Model",
        options=["gpt-4o-mini", "gpt-4.1-mini", "gpt-3.5-turbo"],
        index=0,
    )
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
    max_tokens = st.slider("Max Tokens", min_value=64, max_value=4096, value=1024, step=64)
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful assistant. Answer clearly and concisely.",
        height=100,
    )
    show_debug = st.checkbox("Show debug info", value=False)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        chat_text = "\n\n".join(
            f'{m["role"].upper()}: {m["content"]}' for m in st.session_state.messages
        )
        st.download_button(
            "Export .txt",
            data=chat_text or "No messages yet.",
            file_name="chat_history.txt",
            mime="text/plain",
            use_container_width=True,
        )

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    st.stop()

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key, base_url=api_base_url)

if show_debug:
    st.caption(
        f"Current model: `{model_name}` | Temperature: `{temperature}` | Max tokens: `{max_tokens}`"
    )

if system_prompt.strip():
    with st.expander("Current system prompt"):
        st.code(system_prompt.strip())

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message.
if prompt := st.chat_input("Ask me anything..."):
    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build request messages with an optional system prompt.
    request_messages = []
    if system_prompt.strip():
        request_messages.append({"role": "system", "content": system_prompt.strip()})
    request_messages.extend(
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    )

    try:
        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model=model_name,
            messages=request_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        # Stream the response to the chat and store it in session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as exc:
        st.error(f"Request failed: {exc}")
