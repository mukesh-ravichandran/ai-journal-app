import sys
import os

# Add root directory to path so app.* modules can be imported from ui/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import streamlit as st
from datetime import datetime
import pandas as pd
from app.analyzer import analyze_entry
from app.storage import save_entry
from app.visualizations import plot_emotion_timeline, plot_theme_frequency, plot_theme_wordcloud


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

tabs = st.tabs(["✍️ Add Entry", "📖 Browse Entries", "📊 Visual Insights"])

# -------------------- ✍️ ADD ENTRY --------------------
with tabs[0]:
    st.header("New Journal Entry")

    date = st.date_input("Date", value=datetime.now().date())
    time = st.time_input("Time", value=datetime.now().time())
    text = st.text_area("What’s on your mind?", height=180)

    if st.button("Analyze & Save"):
        if not text.strip():
            st.warning("Please write something before submitting.")
        else:
            with st.spinner("Analyzing with AI..."):
                result = analyze_entry(text)
                result["timestamp"] = datetime.combine(date, time).isoformat()
                result["text"] = text
                save_entry(text, result)
            st.success("✅ Entry saved and analyzed!")

# -------------------- 📖 BROWSE ENTRIES --------------------
with tabs[1]:
    st.header("Your Journal History")

    files = [f for f in os.listdir("data") if f.endswith(".jsonl")]
    file_choice = st.selectbox("Select a database:", files) if files else None

    if file_choice:
        path = os.path.join("data", file_choice)
        with open(path, "r") as f:
            entries = [json.loads(line.strip()) for line in f.readlines()]

        if entries:
            entries.sort(key=lambda x: x["timestamp"], reverse=True)

            available_dates = sorted(list(set([e["timestamp"].split("T")[0] for e in entries])))
            available_dates_dt = [datetime.strptime(d, "%Y-%m-%d").date() for d in available_dates]
            selected_date = st.selectbox("Choose a date with an entry:", available_dates_dt)

            matching_entries = [e for e in entries if e["timestamp"].startswith(selected_date.isoformat())]
            time_options = []
            for e in matching_entries:
                try:
                    dt = datetime.strptime(e["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    dt = datetime.strptime(e["timestamp"], "%Y-%m-%dT%H:%M:%S")
                time_options.append(dt.strftime("%H:%M"))

            selected_time = st.selectbox("Select time:", time_options) if time_options else None

            if selected_time:
                selected = next(
                    e for e in matching_entries
                    if selected_time in e["timestamp"]
                )
                analysis = selected.get("analysis", {})

                col_left, col_right = st.columns([1, 1])

                with col_left:
                    st.markdown(f"""
                        <div class='outerbox'>
                            <div class='readbox-container'>
                                <div class='readbox-title'>Journal Text</div>
                                <div class='readbox'>{selected.get("text", "—")}</div>
                            </div>
                            <div class='readbox-container'>
                                <div class='readbox-title'>Summary</div>
                                <div class='readbox'><ul style="list-style:none;padding-left:0;"><li>{analysis.get("summary", "—")}</li></ul></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                with col_right:
                    st.markdown("""
                        <div class='outerbox'>
                            <div class='readbox-container'>
                                <div class='readbox-title'>Emotions</div>
                                <div class='readbox'><ul>{}</ul></div>
                            </div>
                            <div class='readbox-container'>
                                <div class='readbox-title'>Themes</div>
                                <div class='readbox'><ul>{}</ul></div>
                            </div>
                        </div>
                    """.format(
                        ''.join(f"<li>{x}</li>" for x in analysis.get("emotions", [])),
                        ''.join(f"<li>{x}</li>" for x in analysis.get("themes", []))
                    ), unsafe_allow_html=True)
            else:
                st.info("No entries found for selected date.")
        else:
            st.info("No entries in selected file.")
    else:
        st.info("No database files found in /data.")

# -------------------- 📊 VISUAL INSIGHTS --------------------
with tabs[2]:
    st.header("Visual Insights")
    files = [f for f in os.listdir("data") if f.endswith(".jsonl")]
    file_choice = st.selectbox("Select a database for visualization:", files, key="viz") if files else None

    if file_choice:
        path = os.path.join("data", file_choice)
        with open(path, "r") as f:
            entries = [json.loads(line.strip()) for line in f.readlines()]

        if entries:
            df = pd.DataFrame(entries)
            if "timestamp" in df.columns:
                df["date"] = pd.to_datetime(df["timestamp"]).dt.date

            st.subheader("📈 Emotion Timeline (Top 5)")
            fig = plot_emotion_timeline(df, top_n=5, return_fig=True)
            st.pyplot(fig)

            #st.subheader("📊 Theme Frequency (Top 25)")
            #fig = plot_theme_frequency(df, top_n=25, return_fig=True)
            #st.pyplot(fig)

            st.subheader("🎨 Theme Word Cloud")
            fig = plot_theme_wordcloud(df, return_fig=True)
            st.pyplot(fig)

        else:
            st.info("No data to visualize.")
    else:
        st.info("No database files found.")
