import streamlit as st
import pandas as pd
import os
from utils.analyzer import EMOTION_COLORS, EMOTION_EMOJIS

# --- PAGE CONFIG ---
st.set_page_config(page_title="History", page_icon="📜", layout="wide")

st.title("📜 Analysis History")
st.write("All your past emotion analyses in one place.")

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

st.divider()

# --- QUICK STATS ---
st.subheader("📊 Quick Stats")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔍 Total Analyses", len(history_df))

with col2:
    most_common = history_df["dominant_emotion"].value_counts().idxmax()
    emoji = EMOTION_EMOJIS.get(most_common, "❓")
    st.metric("🎭 Most Common Emotion", f"{emoji} {most_common.capitalize()}")

with col3:
    avg_confidence = history_df["dominant_score"].mean()
    st.metric("📈 Avg Confidence", f"{avg_confidence:.1f}%")

with col4:
    unique_emotions = history_df["dominant_emotion"].nunique()
    st.metric("🌈 Unique Emotions", unique_emotions)

st.divider()

# --- FILTERS ---
st.subheader("🔍 Filter History")

col1, col2 = st.columns(2)

with col1:
    emotion_options = ["All Emotions"] + history_df["dominant_emotion"].unique().tolist()
    selected_emotion = st.selectbox("Filter by emotion", emotion_options)

with col2:
    sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Highest Confidence", "Lowest Confidence"])

# apply filters
filtered_df = history_df.copy()

if selected_emotion != "All Emotions":
    filtered_df = filtered_df[filtered_df["dominant_emotion"] == selected_emotion]

if sort_by == "Newest First":
    filtered_df = filtered_df.sort_values("timestamp", ascending=False)
elif sort_by == "Oldest First":
    filtered_df = filtered_df.sort_values("timestamp", ascending=True)
elif sort_by == "Highest Confidence":
    filtered_df = filtered_df.sort_values("dominant_score", ascending=False)
elif sort_by == "Lowest Confidence":
    filtered_df = filtered_df.sort_values("dominant_score", ascending=True)

st.divider()

# --- HISTORY CARDS ---
st.subheader(f"📋 Results ({len(filtered_df)} entries)")

if filtered_df.empty:
    st.info("No entries match your filters.")
    st.stop()

# show each entry as a card
for _, row in filtered_df.iterrows():
    emotion = row["dominant_emotion"]
    emoji = EMOTION_EMOJIS.get(emotion, "❓")
    color = EMOTION_COLORS.get(emotion, "#888")

    with st.container():
        st.markdown(
            f"""
            <div style="
                background-color: {color}15;
                border-left: 4px solid {color};
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            ">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 14px; color: gray;">{row['timestamp']}</span>
                    <span style="font-size: 14px; color: {color}; font-weight: bold;">
                        {emoji} {emotion.upper()} — {row['dominant_score']:.1f}%
                    </span>
                </div>
                <p style="margin: 8px 0 0 0; font-size: 15px;">"{row['text']}"</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

# --- FULL TABLE ---
st.subheader("📋 Full Data Table")

display_cols = ["timestamp", "text", "dominant_emotion", "dominant_score"]
st.dataframe(
    filtered_df[display_cols].reset_index(drop=True),
    use_container_width=True
)

st.divider()

# --- DOWNLOAD ---
st.subheader("⬇️ Download History")

col1, col2 = st.columns(2)

with col1:
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name="moodlens_history.csv",
        mime="text/csv"
    )

with col2:
    # clear history button
    if st.button("🗑️ Clear All History", type="primary"):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.session_state.history = []
        st.success("✅ History cleared!")
        st.rerun()