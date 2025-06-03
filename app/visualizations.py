import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from wordcloud import WordCloud


def normalize_list_column(df, col):
    df[col] = df[col].apply(
        lambda x: [v.strip().lower() for v in x] if isinstance(x, list) else []
    )
    return df


def plot_emotion_timeline(df, top_n=5, return_fig=False):
    if "analysis" in df.columns:
        df["emotions"] = df["analysis"].apply(lambda x: x.get("emotions", []) if isinstance(x, dict) else [])

    if "emotions" not in df.columns:
        st.warning("No 'emotions' column found in this dataset.")
        return

    df["emotions"] = df["emotions"].apply(
        lambda x: [e.strip().lower() for e in x] if isinstance(x, list) else []
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df_exploded = df[["timestamp", "emotions"]].explode("emotions")

    # Group by month
    df_exploded["month"] = df_exploded["timestamp"].dt.to_period("M").dt.to_timestamp()

    # Filter top N emotions
    top_emotions = df_exploded["emotions"].value_counts().nlargest(top_n).index
    df_exploded = df_exploded[df_exploded["emotions"].isin(top_emotions)]

    emotion_counts = df_exploded.groupby(["month", "emotions"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 6))
    emotion_counts.plot(ax=ax)
    ax.set_title(f"Emotion Timeline (Top {top_n}, Monthly)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Count")
    ax.legend(title="Emotions", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    return fig if return_fig else plt.show()




def plot_theme_frequency(df, top_n=None, return_fig=False):
    if "analysis" in df.columns:
        df["themes"] = df["analysis"].apply(lambda x: x.get("themes", []) if isinstance(x, dict) else [])

    if "themes" not in df.columns:
        st.warning("No 'themes' column found in this dataset.")
        return

    df = normalize_list_column(df, "themes")
    df_exploded = df[["themes"]].explode("themes")
    theme_counts = df_exploded["themes"].value_counts()

    if top_n:
        theme_counts = theme_counts.nlargest(top_n)

    fig, ax = plt.subplots(figsize=(10, 5))
    theme_counts.plot(kind="bar", ax=ax)
    ax.set_title("Theme Frequency")
    ax.set_ylabel("Count")
    ax.set_xlabel("Theme")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
    plt.tight_layout()

    return fig if return_fig else plt.show()


def plot_theme_wordcloud(df, return_fig=False):
    if "analysis" in df.columns:
        df["themes"] = df["analysis"].apply(lambda x: x.get("themes", []) if isinstance(x, dict) else [])

    if "themes" not in df.columns:
        st.warning("No 'themes' column found in this dataset.")
        return

    df = normalize_list_column(df, "themes")
    all_themes = df["themes"].explode().dropna()
    text = " ".join(all_themes)

    wc = WordCloud(width=800, height=400, background_color="white", colormap="Dark2").generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout()

    return fig if return_fig else plt.show()
