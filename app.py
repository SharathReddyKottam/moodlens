import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from audio_recorder_streamlit import audio_recorder
from utils.analyzer import (
    analyze_emotion, transcribe_audio,
    get_dominant_emotion, format_emotions,
    EMOTION_COLORS, EMOTION_EMOJIS
)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MoodLens",
    page_icon="🔍",
    layout="centered"
)

# --- SESSION STATE ---
if "history" not in st.session_state:
    st.session_state.history = []

if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""

# --- HEADER ---
st.title("🔍 MoodLens")
st.write("Analyze the emotions behind any text using AI.")

st.divider()

# --- INPUT TABS ---
st.subheader("📝 Enter Your Text")

input_tab1, input_tab2 = st.tabs(["⌨️ Type Text", "🎤 Voice Input"])

# =====================
# TAB 1 — TYPE TEXT
# =====================
with input_tab1:
    text_input = st.text_area(
        "Type or paste any text below:",
        placeholder="e.g. I had the most amazing day today!",
        height=150,
        value=st.session_state.transcribed_text
    )

# =====================
# TAB 2 — VOICE INPUT
# =====================
with input_tab2:
    st.write("🎤 Click the microphone button and speak:")
    st.caption("Speak clearly for best results. Recording stops automatically after a pause.")

    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#FF4500",
        neutral_color="#6495ED",
        icon_name="microphone",
        icon_size="2x"
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        with st.spinner("🤖 Transcribing your speech..."):
            transcript = transcribe_audio(audio_bytes)

        if "error" in transcript:
            st.error(f"❌ {transcript['error']}")
        else:
            transcribed = transcript["text"].strip()
            st.success(f"✅ Transcribed: **{transcribed}**")

            # store in session state so it appears in text tab
            st.session_state.transcribed_text = transcribed
            text_input = transcribed

            st.info("💡 Text has been copied to the Type Text tab — click Analyze below!")

st.divider()

# --- ANALYZE BUTTON ---
col1, col2 = st.columns([2, 1])

with col1:
    analyze_btn = st.button(
        "🔍 Analyze Emotions",
        type="primary",
        use_container_width=True
    )

with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.transcribed_text = ""
        st.rerun()

st.divider()

# --- ANALYZE ---
if analyze_btn:

    if not text_input or text_input.strip() == "":
        st.error("❌ Please enter or speak some text first!")

    else:
        with st.spinner("🤖 AI is analyzing your text..."):
            emotions = analyze_emotion(text_input)

        if isinstance(emotions, dict) and "error" in emotions:
            st.error(f"❌ {emotions['error']}")

        else:
            formatted = format_emotions(emotions)
            dominant = get_dominant_emotion(emotions)

            st.divider()

            # --- DOMINANT EMOTION ---
            st.subheader("🎭 Overall Emotion")

            dom_label = dominant["label"]
            dom_score = round(dominant["score"] * 100, 1)
            dom_emoji = EMOTION_EMOJIS.get(dom_label, "❓")
            dom_color = EMOTION_COLORS.get(dom_label, "#888")

            st.markdown(
                f"""
                <div style="
                    background-color: {dom_color}22;
                    border-left: 5px solid {dom_color};
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                ">
                    <h1 style="font-size: 60px; margin: 0">{dom_emoji}</h1>
                    <h2 style="color: {dom_color}; margin: 5px 0">{dom_label.upper()}</h2>
                    <h3 style="margin: 0">{dom_score}% confidence</h3>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.divider()

            # --- EMOTION BREAKDOWN ---
            st.subheader("📊 Emotion Breakdown")

            for emotion in formatted:
                col1, col2, col3 = st.columns([2, 5, 1])
                with col1:
                    st.write(f"{emotion['emoji']} **{emotion['label'].capitalize()}**")
                with col2:
                    st.progress(emotion["score"])
                with col3:
                    st.write(f"{emotion['percentage']}%")

            st.divider()

            # --- BAR CHART ---
            st.subheader("📈 Emotion Chart")

            chart_df = pd.DataFrame(formatted)

            fig = px.bar(
                chart_df,
                x="label",
                y="percentage",
                color="label",
                color_discrete_map=EMOTION_COLORS,
                title="Emotion Distribution",
                text="percentage",
                labels={"label": "Emotion", "percentage": "Confidence (%)"}
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(
                showlegend=False,
                yaxis_range=[0, 110],
                xaxis_title="Emotion",
                yaxis_title="Confidence (%)"
            )
            st.plotly_chart(fig, use_container_width=True)

            st.divider()

            # --- SAVE TO HISTORY ---
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            history_entry = {
                "timestamp": timestamp,
                "text": text_input[:100] + "..." if len(text_input) > 100 else text_input,
                "input_type": "voice" if audio_bytes else "text",
                "dominant_emotion": dom_label,
                "dominant_score": dom_score,
                "joy": next((e["percentage"] for e in formatted if e["label"] == "joy"), 0),
                "sadness": next((e["percentage"] for e in formatted if e["label"] == "sadness"), 0),
                "anger": next((e["percentage"] for e in formatted if e["label"] == "anger"), 0),
                "fear": next((e["percentage"] for e in formatted if e["label"] == "fear"), 0),
                "surprise": next((e["percentage"] for e in formatted if e["label"] == "surprise"), 0),
                "disgust": next((e["percentage"] for e in formatted if e["label"] == "disgust"), 0),
                "neutral": next((e["percentage"] for e in formatted if e["label"] == "neutral"), 0),
            }

            st.session_state.history.append(history_entry)

            os.makedirs("data", exist_ok=True)
            history_df = pd.DataFrame(st.session_state.history)
            history_df.to_csv("data/history.csv", index=False)

            st.success(f"✅ Analysis saved to history!")