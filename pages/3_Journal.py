import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from audio_recorder_streamlit import audio_recorder
from utils.analyzer import (
    analyze_emotion, transcribe_audio,
    get_dominant_emotion, format_emotions,
    EMOTION_COLORS, EMOTION_EMOJIS
)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Daily Journal", page_icon="🗓️", layout="centered")

st.title("🗓️ Daily Mood Journal")
st.write("Check in every day — speak or write how you feel.")

st.divider()

# --- FILE PATH ---
JOURNAL_FILE = "data/journal.csv"

# --- LOAD JOURNAL ---
def load_journal():
    if os.path.exists(JOURNAL_FILE):
        try:
            df = pd.read_csv(JOURNAL_FILE)
            if df.empty or len(df.columns) == 0:
                return pd.DataFrame()
            return df
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    return pd.DataFrame()

journal_df = load_journal()

# --- CHECK IF ALREADY CHECKED IN TODAY ---
today = date.today().strftime("%Y-%m-%d")
already_checked_in = False

if not journal_df.empty and "date" in journal_df.columns:
    already_checked_in = today in journal_df["date"].values

# --- STREAK CALCULATION ---
def calculate_streak(df):
    """Calculates current journaling streak in days."""
    if df.empty:
        return 0

    dates = pd.to_datetime(df["date"]).dt.date.tolist()
    dates = sorted(set(dates), reverse=True)

    streak = 0
    check_date = date.today()

    for d in dates:
        if d == check_date:
            streak += 1
            check_date = date.fromordinal(check_date.toordinal() - 1)
        else:
            break

    return streak

streak = calculate_streak(journal_df)

# --- HEADER STATS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔥 Current Streak", f"{streak} days")

with col2:
    total_entries = len(journal_df) if not journal_df.empty else 0
    st.metric("📝 Total Entries", total_entries)

with col3:
    if already_checked_in:
        st.success("✅ Checked in today!")
    else:
        st.warning("⏰ Not checked in yet!")

st.divider()

# --- ALREADY CHECKED IN ---
if already_checked_in:
    st.info("✅ You've already checked in today. Come back tomorrow!")

    # show today's entry
    today_entry = journal_df[journal_df["date"] == today].iloc[-1]
    emotion = today_entry["dominant_emotion"]
    emoji = EMOTION_EMOJIS.get(emotion, "❓")
    color = EMOTION_COLORS.get(emotion, "#888")

    st.markdown(
        f"""
        <div style="
            background-color: {color}22;
            border-left: 5px solid {color};
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        ">
            <h1 style="font-size: 50px; margin: 0">{emoji}</h1>
            <h2 style="color: {color}; margin: 5px 0">Today: {emotion.upper()}</h2>
            <h3 style="margin: 0">Mood Score: {today_entry['mood_score']}/10</h3>
            <p style="margin: 10px 0 0 0; font-style: italic;">"{today_entry['note']}"</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# --- DAILY CHECK IN FORM ---
st.subheader(f"📝 Today's Check-in — {today}")

# --- MOOD SCORE SLIDER ---
st.write("**How are you feeling overall?**")
mood_score = st.slider(
    "Mood Score",
    min_value=1,
    max_value=10,
    value=5,
    help="1 = terrible, 10 = amazing"
)

# mood score display
mood_labels = {
    1: "😭 Terrible",
    2: "😢 Very Bad",
    3: "😞 Bad",
    4: "😕 Not Great",
    5: "😐 Neutral",
    6: "🙂 Okay",
    7: "😊 Good",
    8: "😄 Great",
    9: "🤩 Amazing",
    10: "🥳 Perfect!"
}
st.write(f"**{mood_labels.get(mood_score, '')}**")

st.divider()

# --- INPUT TABS ---
st.write("**Tell us about your day:**")

tab1, tab2 = st.tabs(["⌨️ Type", "🎤 Speak"])

journal_text = ""

with tab1:
    journal_text = st.text_area(
        "How was your day? What happened?",
        placeholder="Today I felt... The best part was... I'm struggling with...",
        height=150
    )

with tab2:
    st.write("🎤 Speak about your day:")
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#FF4500",
        neutral_color="#6495ED",
        icon_name="microphone",
        icon_size="2x",
        key="journal_recorder"
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        with st.spinner("Transcribing..."):
            transcript = transcribe_audio(audio_bytes)

        if "error" in transcript:
            st.error(f"❌ {transcript['error']}")
        else:
            journal_text = transcript["text"].strip()
            st.success(f"✅ Transcribed: **{journal_text}**")

st.divider()

# --- PERSONAL NOTE ---
personal_note = st.text_input(
    "📌 One line summary of today (optional)",
    placeholder="e.g. Great meeting at work, feeling motivated!"
)

st.divider()

# --- SAVE BUTTON ---
if st.button("💾 Save Today's Entry", type="primary", use_container_width=True):

    if not journal_text.strip():
        st.error("❌ Please type or speak about your day first!")

    else:
        with st.spinner("🤖 Analyzing your mood..."):
            emotions = analyze_emotion(journal_text)

        if isinstance(emotions, dict) and "error" in emotions:
            st.error(f"❌ {emotions['error']}")

        else:
            formatted = format_emotions(emotions)
            dominant = get_dominant_emotion(emotions)

            dom_label = dominant["label"]
            dom_score = round(dominant["score"] * 100, 1)
            dom_emoji = EMOTION_EMOJIS.get(dom_label, "❓")
            dom_color = EMOTION_COLORS.get(dom_label, "#888")

            # --- SHOW RESULT ---
            st.markdown(
                f"""
                <div style="
                    background-color: {dom_color}22;
                    border-left: 5px solid {dom_color};
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                ">
                    <h1 style="font-size: 50px; margin: 0">{dom_emoji}</h1>
                    <h2 style="color: {dom_color}; margin: 5px 0">{dom_label.upper()}</h2>
                    <h3 style="margin: 0">{dom_score}% confidence</h3>
                </div>
                """,
                unsafe_allow_html=True
            )

            # emotion breakdown
            st.write("")
            for emotion in formatted:
                col1, col2, col3 = st.columns([2, 5, 1])
                with col1:
                    st.write(f"{emotion['emoji']} **{emotion['label'].capitalize()}**")
                with col2:
                    st.progress(emotion["score"])
                with col3:
                    st.write(f"{emotion['percentage']}%")

            # --- SAVE TO CSV ---
            new_entry = {
                "date": today,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "mood_score": mood_score,
                "text": journal_text[:200],
                "note": personal_note if personal_note else "No note added",
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

            os.makedirs("data", exist_ok=True)

            if os.path.exists(JOURNAL_FILE):
                existing = pd.read_csv(JOURNAL_FILE)
                updated = pd.concat(
                    [existing, pd.DataFrame([new_entry])],
                    ignore_index=True
                )
            else:
                updated = pd.DataFrame([new_entry])

            updated.to_csv(JOURNAL_FILE, index=False)
            st.success("✅ Journal entry saved!")
            st.balloons()