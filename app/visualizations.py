# app/visualizations.py
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_emotion_timeline(df, top_n=10):
    df = df.copy()
    if "emotions" not in df.columns:
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["month"] = df["timestamp"].dt.to_period("M").dt.to_timestamp()
    df_exploded = df.explode("emotions").dropna(subset=["emotions"])
    df_exploded["emotions"] = df_exploded["emotions"].str.strip().str.title()

    emotion_counts = df_exploded["emotions"].value_counts().nlargest(top_n).index
    df_filtered = df_exploded[df_exploded["emotions"].isin(emotion_counts)]

    emotion_monthly = (
        df_filtered
        .groupby(["month", "emotions"])
        .size()
        .reset_index(name="count")
    )

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=emotion_monthly, x="month", y="count", hue="emotions", marker="o")
    plt.title("Monthly Emotion Trends")
    plt.xlabel("Month")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt.gcf()


def plot_theme_frequency(df, top_n=10):
    df = df.copy()
    if "themes" not in df.columns:
        return

    df_exploded = df.explode("themes").dropna(subset=["themes"])
    df_exploded["themes"] = df_exploded["themes"].str.strip().str.title()

    theme_counts = (
        df_exploded["themes"]
        .value_counts()
        .nlargest(top_n)
        .reset_index()
        .rename(columns={"index": "Theme", "themes": "Count"})
    )

    plt.figure(figsize=(8, 4))
    sns.barplot(data=theme_counts, x="Count", y="Theme", palette="coolwarm")
    plt.title("Top Themes")
    plt.xlabel("Count")
    plt.ylabel("")
    plt.tight_layout()
    return plt.gcf()
