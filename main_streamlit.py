import streamlit as st
import json
import os
import asyncio
from datetime import datetime

from classify import classify_request
from retrieve import retrieve_chunks
from escalate import check_escalation
from respond import generate_response  # async function
from logs.logger_utils import log_interaction

st.set_page_config(page_title="IT Helpdesk Chatbot", layout="centered")

# ✅ Inject custom CSS styling
st.markdown("""
    <style>
        .chat-box {
            height: 320px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 12px;
            background: #ffffff;  /* Pure white background */
            margin-bottom: 10px;
            border-radius: 6px;
        }
        .user {
            text-align: right;
            background: #d0f0fd;
            padding: 6px 10px;
            margin: 5px 0;
            border-radius: 10px;
            color: #000000;
            font-weight: bold;  /* Thick black user text */
        }
        .bot {
            text-align: left;
            background: #f0f8da;
            padding: 6px 10px;
            margin: 5px 0;
            border-radius: 10px;
            color: #000000;
        }
        .status-bubble {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        input, textarea, select {
            color: #000 !important;
            background-color: #fff !important;
            font-weight: bold !important;  /* Bold black text in input fields */
        }
        label {
            font-weight: bold;
            color: #fff;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 IT Helpdesk Chatbot")

# Session setup
if "stage" not in st.session_state:
    st.session_state.stage = "username"
if "chat" not in st.session_state:
    st.session_state.chat = []
if "username" not in st.session_state:
    st.session_state.username = ""
if "contact" not in st.session_state:
    st.session_state.contact = ""
if "category" not in st.session_state:
    st.session_state.category = ""
if "escalated" not in st.session_state:
    st.session_state.escalated = None

# Status display
def render_status():
    color = "gray"
    text = "Status: Waiting for message..."
    if st.session_state.escalated is True:
        color = "red"
        text = "Status: CRITICAL – Escalation needed"
    elif st.session_state.escalated is False:
        color = "green"
        text = "Status: OK – No escalation"
    st.markdown(f'<div class="status-indicator"><span class="status-bubble" style="background-color:{color};"></span>{text}</div>', unsafe_allow_html=True)

render_status()

# Chat box rendering
with st.container():
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for entry in st.session_state.chat:
        role = "user" if "user" in entry else "bot"
        text = entry.get(role)
        st.markdown(f'<div class="{role}">{text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Step-by-step chat logic
if st.session_state.stage == "username":
    name = st.text_input("Enter your name")
    if st.button("Next"):
        if name.strip():
            st.session_state.username = name.strip()
            st.session_state.chat.append({"user": name})
            st.session_state.stage = "contact"
            st.rerun()

elif st.session_state.stage == "contact":
    contact = st.text_input("Enter your contact (email/phone)")
    if st.button("Next"):
        if contact.strip():
            st.session_state.contact = contact.strip()
            st.session_state.chat.append({"user": contact})
            st.session_state.stage = "category"
            st.rerun()

elif st.session_state.stage == "category":
    category = st.selectbox("Choose a category", options=[
        "", "password_reset", "software_installation", "network_connectivity",
        "email_configuration", "hardware_failure", "security_incident", "policy_question", "general_inquiry"
    ])
    if st.button("Next"):
        if category:
            st.session_state.category = category
            st.session_state.chat.append({"user": category})
            st.session_state.chat.append({"bot": f"Hi {st.session_state.username}, how can I assist you today?"})
            st.session_state.stage = "chat"
            st.rerun()

elif st.session_state.stage == "chat":
    message = st.text_input("Type your message")
    if st.button("Send"):
        if message.strip():
            user_msg = message.strip()
            st.session_state.chat.append({"user": user_msg})

            actual_category = (
                classify_request(user_msg)
                if st.session_state.category.lower() == "auto"
                else st.session_state.category
            )

            chunks = retrieve_chunks(user_msg, actual_category)
            escalate, reason = check_escalation(user_msg, actual_category)
            st.session_state.escalated = escalate

            full_context = "\n\n".join([msg.get("user", msg.get("bot", "")) for msg in st.session_state.chat])
            with st.spinner("Generating response..."):
                response = asyncio.run(generate_response(
                    full_context, chunks, actual_category, st.session_state.username
                ))

            st.session_state.chat.append({"bot": response})

            os.makedirs("logs/chat_sessions", exist_ok=True)
            chat_path = f"logs/chat_sessions/{st.session_state.username}.json"
            with open(chat_path, "w", encoding="utf-8") as f:
                json.dump(st.session_state.chat, f, indent=2)

            log_interaction({
                "timestamp": datetime.now().isoformat(),
                "username": st.session_state.username,
                "contact": st.session_state.contact,
                "query": user_msg,
                "category": actual_category,
                "escalate": escalate,
                "escalation_reason": reason,
                "response": response
            })

            st.session_state.chat.append({"bot": "✅ Is your query resolved? You can submit feedback or end the session."})
            st.session_state.stage = "feedback"
            st.rerun()

elif st.session_state.stage == "feedback":
    feedback = st.text_area("Optional: Share feedback")
    if st.button("Submit Feedback"):
        if feedback.strip():
            os.makedirs("logs/feedback", exist_ok=True)
            fname = f"logs/feedback/{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(feedback.strip())
            st.session_state.chat.append({"bot": "🙏 Thanks for your feedback."})
        else:
            st.session_state.chat.append({"bot": "Feedback skipped."})
        st.session_state.stage = "end"
        st.rerun()

if st.session_state.stage == "end":
    if st.button("Start New Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
