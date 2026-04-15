import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="聊天助手增强版", page_icon="💬", layout="wide")

# Show title and description.
st.title("💬 聊天助手增强版")
st.write(
    "一个更丰富的聊天应用，支持模型调参、系统提示词控制和聊天记录导出。"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("参数设置")
    openai_api_key = st.text_input("OpenAI API 密钥", type="password")
    api_base_url = st.text_input("API 基础地址", value="https://sg.uiuiapi.com/v1")
    model_name = st.selectbox(
        "模型",
        options=["gpt-4o-mini", "gpt-4.1-mini", "gpt-3.5-turbo"],
        index=0,
    )
    temperature = st.slider("温度系数", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
    max_tokens = st.slider("最大 Token 数", min_value=64, max_value=4096, value=1024, step=64)
    system_prompt = st.text_area(
        "系统提示词",
        value="你是一个有帮助的助手，请清晰、简洁地回答问题。",
        height=100,
    )
    show_debug = st.checkbox("显示调试信息", value=False)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("清空聊天", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        chat_text = "\n\n".join(
            f'{m["role"].upper()}: {m["content"]}' for m in st.session_state.messages
        )
        st.download_button(
            "导出 .txt",
            data=chat_text or "暂无聊天记录。",
            file_name="chat_history.txt",
            mime="text/plain",
            use_container_width=True,
        )

if not openai_api_key:
    st.info("请先输入 OpenAI API 密钥后再继续。", icon="🗝️")
    st.stop()

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key, base_url=api_base_url)

if show_debug:
    st.caption(
        f"当前模型: `{model_name}` | 温度系数: `{temperature}` | 最大 Token: `{max_tokens}`"
    )

if system_prompt.strip():
    with st.expander("当前系统提示词"):
        st.code(system_prompt.strip())

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message.
if prompt := st.chat_input("请输入你的问题..."):
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
        st.error(f"请求失败: {exc}")
