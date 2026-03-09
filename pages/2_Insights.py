import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from utils.analyzer import EMOTION_COLORS, EMOTION_EMOJIS

# --- PAGE CONFIG ---
st.set_page_config(page_title="Insights", page_icon="📊", layout="wide")

st.title("📊 Emotion Insights")
st.write("Patterns and trends across all your analyses.")

st.divider()

# --- LOAD HISTORY ---
HISTORY_FILE = "data/history.csv"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            if df.empty or len(df.columns) == 0:
                return pd.DataFrame()
            return df
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    return pd.DataFrame()

history_df = load_history()

if history_df.empty:
    st.info("No analyses yet. Go to the home page and analyze some text!")
    st.stop()

# prepare dates
history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
history_df["date"] = history_df["timestamp"].dt.date
history_df["hour"] = history_df["timestamp"].dt.hour

emotion_cols = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"]

st.divider()

# --- OVERVIEW METRICS ---
st.subheader("📈 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔍 Total Analyses", len(history_df))

with col2:
    most_common = history_df["dominant_emotion"].value_counts().idxmax()
    emoji = EMOTION_EMOJIS.get(most_common, "❓")
    st.metric("🎭 Most Common", f"{emoji} {most_common.capitalize()}")

with col3:
    avg_joy = history_df["joy"].mean()
    st.metric("😊 Avg Joy Score", f"{avg_joy:.1f}%")

with col4:
    avg_confidence = history_df["dominant_score"].mean()
    st.metric("📊 Avg Confidence", f"{avg_confidence:.1f}%")

st.divider()

# --- ROW 1: EMOTION DISTRIBUTION + DOMINANT EMOTIONS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🥧 Emotion Distribution")

    # average score per emotion across all analyses
    avg_emotions = history_df[emotion_cols].mean().reset_index()
    avg_emotions.columns = ["Emotion", "Average Score (%)"]
    avg_emotions = avg_emotions.sort_values("Average Score (%)", ascending=False)

    fig1 = px.pie(
        avg_emotions,
        names="Emotion",
        values="Average Score (%)",
        color="Emotion",
        color_discrete_map=EMOTION_COLORS,
        title="Average Emotion Mix",
        hole=0.4
    )
    fig1.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🏆 Dominant Emotion Counts")

    dominant_counts = history_df["dominant_emotion"].value_counts().reset_index()
    dominant_counts.columns = ["Emotion", "Count"]

    fig2 = px.bar(
        dominant_counts,
        x="Emotion",
        y="Count",
        color="Emotion",
        color_discrete_map=EMOTION_COLORS,
        title="How often each emotion dominates",
        text="Count"
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        showlegend=False,
        yaxis_range=[0, dominant_counts["Count"].max() * 1.3]
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- ROW 2: EMOTIONS OVER TIME ---
st.subheader("📅 Emotions Over Time")

# group by date
time_df = history_df.groupby("date")[emotion_cols].mean().reset_index()
time_df["date"] = pd.to_datetime(time_df["date"])

# let user pick which emotions to show
selected_emotions = st.multiselect(
    "Select emotions to display:",
    emotion_cols,
    default=["joy", "sadness", "anger"]
)

if selected_emotions:
    fig3 = go.Figure()

    for emotion in selected_emotions:
        color = EMOTION_COLORS.get(emotion, "#888")
        emoji = EMOTION_EMOJIS.get(emotion, "")
        fig3.add_trace(go.Scatter(
            x=time_df["date"],
            y=time_df[emotion],
            name=f"{emoji} {emotion.capitalize()}",
            line=dict(color=color, width=2),
            mode="lines+markers"
        ))

    fig3.update_layout(
        title="Emotion Scores Over Time",
        xaxis_title="Date",
        yaxis_title="Average Score (%)",
        yaxis_range=[0, 100],
        hovermode="x unified"
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --- ROW 3: EMOTION HEATMAP + RADAR CHART ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Emotion Heatmap")

    if len(history_df) >= 2:
        heatmap_df = history_df[emotion_cols].copy()
        heatmap_df.index = history_df["timestamp"].dt.strftime("%m/%d %H:%M")

        fig4 = px.imshow(
            heatmap_df.T,
            color_continuous_scale="RdYlGn",
            title="Emotion Intensity per Analysis",
            labels=dict(x="Analysis", y="Emotion", color="Score (%)"),
            aspect="auto"
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Need at least 2 analyses to show heatmap.")

with col2:
    st.subheader("🕸️ Emotion Radar Chart")

    # average scores for radar
    avg_scores = history_df[emotion_cols].mean()

    fig5 = go.Figure()

    fig5.add_trace(go.Scatterpolar(
        r=avg_scores.values.tolist() + [avg_scores.values[0]],
        theta=emotion_cols + [emotion_cols[0]],
        fill="toself",
        fillcolor="rgba(100, 149, 237, 0.3)",
        line=dict(color="cornflowerblue", width=2),
        name="Avg Emotions"
    ))

    fig5.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        title="Average Emotion Radar",
        showlegend=False
    )
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

# --- ROW 4: CONFIDENCE TREND + HOUR ANALYSIS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Emotion Heatmap")

    if len(history_df) >= 2:
        heatmap_df = history_df[emotion_cols].copy()
        heatmap_df.index = history_df["timestamp"].dt.strftime("%m/%d %H:%M")

        fig4 = px.imshow(
            heatmap_df.T,
            color_continuous_scale="RdYlGn",
            title="Emotion Intensity per Analysis",
            labels=dict(x="Analysis", y="Emotion", color="Score (%)"),
            aspect="auto"
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Need at least 2 analyses to show heatmap.")
with col2:
    st.subheader("🕐 Analysis by Hour of Day")

    hour_df = history_df.groupby("hour").size().reset_index()
    hour_df.columns = ["Hour", "Count"]

    fig7 = px.bar(
        hour_df,
        x="Hour",
        y="Count",
        title="When do you analyze most?",
        color="Count",
        color_continuous_scale="Blues",
        text="Count"
    )
    fig7.update_traces(textposition="outside")
    fig7.update_layout(
        showlegend=False,
        xaxis=dict(tickmode="linear", tick0=0, dtick=1)
    )
    st.plotly_chart(fig7, use_container_width=True)

st.divider()

# --- FULL DATA TABLE ---
st.subheader("📋 Full Emotion Data")

display_df = history_df[["timestamp", "dominant_emotion", "dominant_score"] + emotion_cols].copy()
display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
display_df = display_df.sort_values("timestamp", ascending=False)

st.dataframe(display_df.reset_index(drop=True), use_container_width=True)