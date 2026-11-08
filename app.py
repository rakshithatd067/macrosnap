from google import genai
from google.genai import types
import streamlit as st

from prompts import SYSTEM_PROMPT,WELCOME_MESSAGE_TEMPLATE
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

gemini_client = get_gemini_client()
MODEL_NAME = "gemini-3.0-flash"

def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])




def add_message(role, kind, content):
    st.session_state.messages.append({ "role": role, "kind": kind,
        "content": content
    })

if 'onboarded' not in st.session_state:
    st.title("MacroSnap")
    st.caption("Snap it. Track it. Text yourself the result.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name:")
        whatsapp_number = st.text_input(
            "WhatsApp number (with country code)",
            placeholder="+91XXXXXXXXXX",
            help="This is the number MacroSnap will text you."
        )
        submitted = st.form_submit_button("Let's go 🚀")

if submitted:
    if not name.strip() or not whatsapp_number.strip():
        st.warning("Please fill in both your name and WhatsApp number.")
    else:
        st.session_state.name = name.strip()
        st.session_state.whatsapp_number = whatsapp_number.strip()
#activate my ai
        st.session_state.chat = gemini_client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        )
        st.session_state.messages = []
        st.session_state.onboarded = True   
        st.rerun()
st.stop()
#chat 
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title(" MacroSnap")

with button_col:
    send_disabled = len(st.session_state.messages) <= 1

    if st.button("📤 Send to WhatsApp", disabled=send_disabled):
        with st.spinner("Summarizing your day..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
        success, info = send_whatsapp(st.session_state.whatsapp, summary)

        if success:
            st.success("Sent! Check your WhatsApp 📲")
        else:
            st.error(f"Couldn't send that: {info}")

st.caption(f"Logged in as {st.session_state.name} - Updates go to [{st.session_state.whatsapp_number}]")
if not st.session_state.messages:
    add_message("assistant", text=WELCOME_MESSAGE_TEMPLATE)
else:
    for message in st.session_state.messages:
        render_message(message)