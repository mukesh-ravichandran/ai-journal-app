import sys
import os

# Add root directory to path so app.* modules can be imported from ui/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import random

import streamlit as st
from datetime import datetime
import pandas as pd
from app.llm import get_deepseek_response
from app.analyzer import analyze_entry
from app.storage import save_entry
from app.visualizations import (
    plot_emotion_area,
    plot_theme_wordcloud
)

st.set_page_config(page_title="AI Journal", layout="centered")
st.title("📝 AI-Powered Journal")

# --------- DARK THEME STYLING ---------
st.markdown("""
    <style>
    html, body, [class*="css"] {
        background-color: #1e1f23;
        color: #f5f5f5;
        font-family: 'Segoe UI', sans-serif;
    }
    .outerbox {
        background-color: #2c2f35;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #444;
        height: 720px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
    }
    .readbox-container {
        background-color: #2c2f35;
        padding: 2rem 1rem 1rem;
        border-radius: 8px;
        border: 1px solid #444;
        position: relative;
        margin-bottom: 1.5rem;
        height: 320px;
    }
    .readbox-title {
        position: absolute;
        top: -0.8rem;
        left: 1rem;
        background-color: #2c2f35;
        padding: 0 0.6rem;
        font-weight: 600;
        font-size: 0.93rem;
        color: #f5f5f5;
        z-index: 10;
        border-left: 1px solid #444;
        border-right: 1px solid #444;
        border-top: 1px solid #444;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        text-transform: uppercase;
    }
    .readbox {
        background-color: #3a3d44;
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        font-size: 0.93rem;
        line-height: 1.6;
        height: 190px;
        overflow-y: auto;
        border: 1px solid #444;
        margin-top: 1rem;
    }
    ul {
        padding-left: 1.25rem;
        margin: 0.25rem 0;
    }
    li {
        margin-bottom: 0.2rem;
        text-transform: capitalize;
    }
    label, .stTextInput label, .stTextArea label, .stDateInput label, .stTimeInput label {
        color: #f5f5f5 !important;
    }
    .stDateInput input {
        position: relative;
    }
    .stDateInput input[data-highlight='true'] {
        border: 2px solid red !important;
    }
    </style>
""", unsafe_allow_html=True)

tabs = st.tabs(["✍️ Add Entry", "📖 Browse Entries", "📊 Visual Insights", "💬 Journal Assistant"])

# -------------------- 💬 JOURNAL ASSISTANT --------------------
from app.llm import get_deepseek_response  # Make sure you added this earlier

with tabs[3]:
    st.markdown("""
        <style>
        .chat-box {
            height: 70vh;
            overflow-y: auto;
            padding: 1rem;
            background-color: #1e1e1e;
            border-radius: 8px;
            border: 1px solid #444;
            margin-bottom: 80px;
        }
        .chat-message {
            padding: 0.5rem;
            margin-bottom: 0.75rem;
            border-radius: 10px;
            max-width: 80%;
        }
        .chat-message.user {
            background-color: #333;
            color: #f5f5f5;
            align-self: flex-end;
            text-align: right;
        }
        .chat-message.bot {
            background-color: #2c2f35;
            color: #f5f5f5;
            align-self: flex-start;
        }
        .chat-row {
            display: flex;
            flex-direction: column;
        }
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100vw;
            background-color: #181825;
            padding: 0.75rem 1rem;
            border-top: 1px solid #333;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            z-index: 100;
        }
        .chat-input {
            flex-grow: 1;
            padding: 0.6rem 1rem;
            font-size: 1rem;
            border-radius: 20px;
            border: none;
            background-color: #2c2f35;
            color: white;
        }
        .send-btn {
            background-color: transparent;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🧠 Journal Chatbot")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # --- INPUT FORM FIRST ---
    user_input = ""
    with st.form("chat_form", clear_on_submit=True):
        cols = st.columns([10, 1])
        user_input = cols[0].text_input(
            "Your message",
            key="new_chat_input",
            label_visibility="collapsed",
            placeholder="Type a message..."
        )
        submitted = cols[1].form_submit_button("➤")

    # --- PROCESS INPUT using LLM ---
    if submitted and user_input.strip():
        st.session_state.chat_messages.append({"role": "user", "content": user_input.strip()})
        llm_reply = get_deepseek_response(user_input.strip())
        st.session_state.chat_messages.append({"role": "bot", "content": llm_reply})

    # --- CHAT DISPLAY ---
    chat_html = '<div class="chat-box chat-row">'
    for m in st.session_state.chat_messages:
        role_class = "user" if m["role"] == "user" else "bot"
        chat_html += f'<div class="chat-message {role_class}">{m["content"]}</div>'
    chat_html += '<div id="chat-end"></div></div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # --- AUTO-SCROLL TO BOTTOM ---
    st.markdown("""
        <script>
        var chatContainer = document.querySelector(".chat-box");
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        </script>
    """, unsafe_allow_html=True)

    # --- Fixed input container dummy tag ---
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)