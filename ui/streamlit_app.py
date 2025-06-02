import sys
import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil import parser

from app.analyzer import analyze_entry
from app.storage import save_entry
from app.visualizations import plot_emotion_timeline, plot_theme_frequency

sys.path.append("/Users/Additional Storage/ML Projects/Journal app")

st.set_page_config(page_title="AI Journal", layout="centered")
st.title("📝 AI-Powered Journal")

# --------- STYLING ---------
st.markdown("""
    <style>
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
        color: white;
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

            available_dates = sorted(list(set(e["timestamp"].split("T")[0] for e in entries)))
            date_options = [datetime.strptime(d, "%Y-%m-%d").strftime("%d-%b-%Y") for d in available_dates]

            col_date, col_time = st.columns([1, 1])
            with col_date:
                selected_date_str = st.selectbox("Filter by date:", date_options)
                selected_date = datetime.strptime(selected_date_str, "%d-%b-%Y").date()

            with col_time:
                matching_entries = [e for e in entries if e["timestamp"].startswith(selected_date.isoformat())]
                time_options = [
                    parser.parse(e["timestamp"]).strftime("%H:%M")

                    for e in matching_entries
                ]
                selected_time = st.selectbox("Select time:", time_options) if time_options else None

            if selected_time:
                selected = next(e for e in matching_entries if selected_time in e["timestamp"])
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
                    st.markdown(f"""
                        <div class='outerbox'>
                            <div class='readbox-container'>
                                <div class='readbox-title'>Emotions</div>
                                <div class='readbox'><ul>{''.join(f"<li>{e}</li>" for e in analysis.get("emotions", []))}</ul></div>
                            </div>
                            <div class='readbox-container'>
                                <div class='readbox-title'>Themes</div>
                                <div class='readbox'><ul>{''.join(f"<li>{t}</li>" for t in analysis.get("themes", []))}</ul></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No entries found for selected date.")
        else:
            st.info("No entries in selected file.")
    else:
        st.info("No database files found in /data.")

# -------------------- 📊 VISUAL INSIGHTS --------------------
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

            # Flatten 'analysis' dictionary into columns
            if "analysis" in df.columns:
                analysis_df = pd.json_normalize(df["analysis"])
                df = pd.concat([df.drop(columns=["analysis"]), analysis_df], axis=1)

            # Check for required column
            if "emotions" not in df.columns:
                st.error("❌ 'emotions' column missing. Your data might not be analyzed yet.")
                st.stop()

            # Format and parse dates
            df["date"] = pd.to_datetime(df["timestamp"]).dt.date
            df["month"] = pd.to_datetime(df["timestamp"]).dt.to_period("M").dt.to_timestamp()
            df["date_str"] = df["date"].apply(lambda d: d.strftime("%d-%b-%Y"))

            st.subheader("📈 Emotion Timeline (Monthly Frequency)")
            st.pyplot(plot_emotion_timeline(df))

            st.subheader("📊 Theme Frequency")
            st.pyplot(plot_theme_frequency(df))

        else:
            st.info("No data to visualize.")
    else:
        st.info("No database files found.")
