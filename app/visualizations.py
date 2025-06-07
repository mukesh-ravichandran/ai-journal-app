from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
from PIL import Image, ImageFilter
import numpy as np
import os

# ---------- MASK HELPERS ----------
def soften_mask_edges(mask_path, blur_radius=10):
    if os.path.exists(mask_path):
        mask = Image.open(mask_path).convert("L")
        blurred = mask.filter(ImageFilter.GaussianBlur(blur_radius))
        return np.array(blurred)
    return None


# ---------- STACKED AREA CHART ----------
def plot_emotion_area(df, emotion_col="analysis", top_n=5, selected=None):
    df["month"] = pd.to_datetime(df["timestamp"]).dt.to_period("M").dt.to_timestamp()

    emotion_counts = {}
    for _, row in df.iterrows():
        if isinstance(row[emotion_col], dict) and "emotions" in row[emotion_col]:
            for emotion in row[emotion_col]["emotions"]:
                month = row["month"]
                emotion_counts[(month, emotion)] = emotion_counts.get((month, emotion), 0) + 1

    data = [
        {"month": month, "emotion": emotion, "count": count}
        for (month, emotion), count in emotion_counts.items()
    ]
    timeline_df = pd.DataFrame(data)

    if selected:
        top_emotions = selected
    else:
        top_emotions = Counter(timeline_df["emotion"]).most_common(top_n)
        top_emotions = [e[0] for e in top_emotions]

    timeline_df = timeline_df[timeline_df["emotion"].isin(top_emotions)]
    pivot_df = timeline_df.pivot(index="month", columns="emotion", values="count").sort_index().fillna(0)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor='none')
    ax.set_facecolor('none')

    colors = plt.cm.tab10.colors[:len(pivot_df.columns)]
    pivot_df.plot.area(ax=ax, color=colors, linewidth=0, legend=True)

 

    ax.set_title("Emotion Trends – Stacked Area", color='white', fontsize=16, pad=15)
    ax.set_xlabel("Month", color='white')
    ax.set_ylabel("Frequency", color='white')
    ax.tick_params(colors='white')

    for spine in ax.spines.values():
        spine.set_color('white')

    ax.set_xticks(pivot_df.index)
    ax.set_xticklabels([d.strftime("%b %Y") for d in pivot_df.index], rotation=45, ha='right', color='white')
    fig.tight_layout()
    return fig


# ---------- EMOTION HEATMAP ----------
def plot_emotion_heatmap(df, emotion_col="analysis", top_n=5, selected=None):
    df["month"] = pd.to_datetime(df["timestamp"]).dt.to_period("M").dt.to_timestamp()

    emotion_counts = {}
    for _, row in df.iterrows():
        if isinstance(row[emotion_col], dict) and "emotions" in row[emotion_col]:
            for emotion in row[emotion_col]["emotions"]:
                month = row["month"]
                emotion_counts[(month, emotion)] = emotion_counts.get((month, emotion), 0) + 1

    data = [
        {"month": month, "emotion": emotion, "count": count}
        for (month, emotion), count in emotion_counts.items()
    ]
    timeline_df = pd.DataFrame(data)

    if selected:
        top_emotions = selected
    else:
        top_emotions = Counter(timeline_df["emotion"]).most_common(top_n)
        top_emotions = [e[0] for e in top_emotions]

    timeline_df = timeline_df[timeline_df["emotion"].isin(top_emotions)]
    pivot_df = timeline_df.pivot(index="emotion", columns="month", values="count").fillna(0)

    fig, ax = plt.subplots(figsize=(10, 4), facecolor='none')
    ax.set_facecolor('none')

    sns.heatmap(
        pivot_df,
        ax=ax,
        cmap="coolwarm",
        linewidths=0.5,
        linecolor="#444",
        cbar=True,
        xticklabels=[d.strftime("%b %Y") for d in pivot_df.columns],
        yticklabels=True
    )

    ax.tick_params(colors='white')
    ax.set_title("Emotion Frequency Heatmap", color='white', fontsize=14, pad=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


# ---------- THEME WORD CLOUD ----------
def plot_theme_wordcloud(df, theme_col="analysis", key="themes", wc=20):
    bg_color = None

    all_themes = []
    for row in df[theme_col]:
        if isinstance(row, dict) and key in row:
            all_themes.extend(row[key])
    if not all_themes:
        all_themes = ["no themes"]
    text = " ".join(all_themes)

    def soften_mask_edges(mask_path, blur_radius=4):
        mask = Image.open(mask_path).convert("L")
        blurred = mask.filter(ImageFilter.GaussianBlur(blur_radius))
        return np.array(blurred)

    mask_path = os.path.join("data", "Heart_Mask.png")
    mask = soften_mask_edges(mask_path) if os.path.exists(mask_path) else None

    wordcloud = WordCloud(
        background_color=bg_color,
        mode="RGBA",
        max_words=wc,
        stopwords=set(STOPWORDS),
        mask=mask,
        contour_color=None,
        contour_width=0,
        width=800,
        height=800,
        colormap="coolwarm"
    ).generate(text)

    fig = plt.figure(figsize=(6, 6), facecolor=bg_color)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    return fig