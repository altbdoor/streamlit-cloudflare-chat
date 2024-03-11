import streamlit as st
import streamlit.components.v1 as components
import requests
import json


# ========================================
# settings
# ========================================
setting_keys = (
    "model",
    "api_token",
    "account_id",
    "max_tokens",
    "temperature",
)
for key in setting_keys:
    if key not in st.session_state:
        st.session_state[key] = ""

with st.sidebar:
    st.write(
        "Please refer to the [Cloudflare docs]"
        "(https://developers.cloudflare.com/workers-ai/)"
        " on how to fill these in."
    )

    with st.form("settings", border=False):
        model = st.text_input(
            "Model",
            placeholder="Model",
            value="@hf/thebloke/mistral-7b-instruct-v0.1-awq",
        )
        api_token = st.text_input("Cloudflare API token")
        account_id = st.text_input("Cloudflare account ID")
        max_tokens = st.number_input("Max tokens", value=256)
        temperature = st.number_input("Temperature", value=1.0)
        submitted = st.form_submit_button("Save settings")

        if submitted:
            st.session_state["model"] = model
            st.session_state["api_token"] = api_token
            st.session_state["account_id"] = account_id
            st.session_state["max_tokens"] = max_tokens
            st.session_state["temperature"] = temperature

            st.toast("Saved settings")

# ========================================
# messages
# ========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

stop_sequence = ("[DONE]", "</s>")


def response_generator():
    session = requests.Session()
    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{st.session_state.account_id}/ai/run/{st.session_state.model}"
    )

    with session.post(
        url,
        headers={
            "Authorization": f"Bearer {st.session_state.api_token}",
            "Accept": "text/event-stream",
        },
        json={
            "messages": st.session_state.messages,
            "max_tokens": st.session_state.max_tokens,
            "temperature": st.session_state.temperature,
            "stream": True,
        },
    ) as res:
        for line in res.iter_lines():
            decode_line: str = line.decode("utf-8")
            sse_line = decode_line.split(":", 1)

            if len(sse_line) != 2:
                continue

            json_line = sse_line[1].strip()
            if json_line == "" or json_line == "[DONE]":
                break

            sse_line = json.loads(json_line)
            if sse_line["response"] in stop_sequence:
                break

            yield sse_line["response"]


for message in st.session_state.messages:
    avatar = None
    if message["role"] == "system":
        avatar = "⚡️"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Type in your message"):
    role = "user"
    if len(st.session_state.messages) == 0:
        role = "system"

    with st.chat_message(role):
        st.markdown(prompt)

    st.session_state.messages.append({"role": role, "content": prompt})

if (
    len(st.session_state.messages) > 0
    and st.session_state.messages[-1]["role"] == "user"
):
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())

    st.session_state.messages.append({"role": "assistant", "content": response})


with open("./custom.js", "r") as fp:
    content = fp.read()
    components.html("<!-- custom -->" f"<script>{content}</script>")
