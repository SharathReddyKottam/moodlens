import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
import os
from datetime import date, datetime
from utils.analyzer import EMOTION_COLORS, EMOTION_EMOJIS

# --- PAGE CONFIG ---
st.set_page_config(page_title="Mood Calendar", page_icon="📅", layout="wide")

st.title("📅 Mood Calendar")
st.write("See your emotional journey day by day.")

st.divider()

# --- LOAD JOURNAL ---
JOURNAL_FILE = "data/journal.csv"

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

if journal_df.empty:
    st.info("No journal entries yet. Start your daily check-in first!")
    st.stop()

# --- PREPARE DATA ---
journal_df["date"] = pd.to_datetime(journal_df["date"])
journal_df["year"] = journal_df["date"].dt.year
journal_df["month"] = journal_df["date"].dt.month
journal_df["day"] = journal_df["date"].dt.day
journal_df["weekday"] = journal_df["date"].dt.weekday

st.divider()

# --- MONTH SELECTOR ---
st.subheader("📅 Select Month")

col1, col2 = st.columns(2)

with col1:
    available_years = sorted(journal_df["year"].unique().tolist(), reverse=True)
    selected_year = st.selectbox("Year", available_years)

with col2:
    month_names = {
        1: "January", 2: "February", 3: "March",
        4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September",
        10: "October", 11: "November", 12: "December"
    }
    available_months = sorted(
        journal_df[journal_df["year"] == selected_year]["month"].unique().tolist()
    )
    selected_month = st.selectbox(
        "Month",
        available_months,
        format_func=lambda x: month_names[x]
    )

# filter to selected month
month_df = journal_df[
    (journal_df["year"] == selected_year) &
    (journal_df["month"] == selected_month)
    ]

st.divider()

# --- MONTH OVERVIEW METRICS ---
st.subheader(f"📊 {month_names[selected_month]} {selected_year} Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    days_in_month = calendar.monthrange(selected_year, selected_month)[1]
    entries = len(month_df)
    st.metric("📝 Days Journaled", f"{entries}/{days_in_month}")

with col2:
    consistency = round((entries / days_in_month) * 100, 1)
    st.metric("📈 Consistency", f"{consistency}%")

with col3:
    if not month_df.empty:
        avg_mood = month_df["mood_score"].mean()
        st.metric("😊 Avg Mood Score", f"{avg_mood:.1f}/10")
    else:
        st.metric("😊 Avg Mood Score", "N/A")

with col4:
    if not month_df.empty:
        most_common = month_df["dominant_emotion"].value_counts().idxmax()
        emoji = EMOTION_EMOJIS.get(most_common, "❓")
        st.metric("🎭 Most Common Mood", f"{emoji} {most_common.capitalize()}")
    else:
        st.metric("🎭 Most Common Mood", "N/A")

st.divider()

# --- CALENDAR GRID ---
st.subheader("🗓️ Monthly Calendar")

# build calendar grid
cal = calendar.monthcalendar(selected_year, selected_month)
day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# header row
header_cols = st.columns(7)
for i, day_name in enumerate(day_names):
    with header_cols[i]:
        st.markdown(f"<p style='text-align:center; font-weight:bold; color:gray'>{day_name}</p>", unsafe_allow_html=True)

# calendar rows
for week in cal:
    week_cols = st.columns(7)
    for i, day in enumerate(week):
        with week_cols[i]:
            if day == 0:
                # empty cell
                st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
            else:
                # check if this day has an entry
                day_entry = month_df[month_df["day"] == day]

                if not day_entry.empty:
                    entry = day_entry.iloc[0]
                    emotion = entry["dominant_emotion"]
                    emoji = EMOTION_EMOJIS.get(emotion, "❓")
                    color = EMOTION_COLORS.get(emotion, "#888")
                    mood = entry["mood_score"]

                    # today highlight
                    today = date.today()
                    is_today = (
                            day == today.day and
                            selected_month == today.month and
                            selected_year == today.year
                    )

                    border = "3px solid white" if is_today else "none"

                    st.markdown(
                        f"""
                        <div style="
                            background-color: {color}33;
                            border: {border};
                            border-radius: 10px;
                            padding: 8px;
                            text-align: center;
                            height: 80px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        ">
                            <p style="margin:0; font-size:11px; color:gray">{day}</p>
                            <p style="margin:0; font-size:22px">{emoji}</p>
                            <p style="margin:0; font-size:10px; color:{color}">
                                {mood}/10
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    # no entry for this day
                    today = date.today()
                    is_today = (
                            day == today.day and
                            selected_month == today.month and
                            selected_year == today.year
                    )
                    bg = "#ffffff22" if is_today else "transparent"
                    border = "1px dashed gray"

                    st.markdown(
                        f"""
                        <div style="
                            background-color: {bg};
                            border: {border};
                            border-radius: 10px;
                            padding: 8px;
                            text-align: center;
                            height: 80px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        ">
                            <p style="margin:0; font-size:11px; color:gray">{day}</p>
                            <p style="margin:0; font-size:18px">—</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

st.divider()

# --- MOOD SCORE TREND ---
st.subheader("📈 Mood Score Trend")

if not month_df.empty:
    mood_trend = month_df.sort_values("date")

    fig1 = px.line(
        mood_trend,
        x="date",
        y="mood_score",
        title=f"Mood Score — {month_names[selected_month]} {selected_year}",
        markers=True,
        color_discrete_sequence=["cornflowerblue"]
    )

    # add zones
    fig1.add_hrect(y0=1, y1=4, fillcolor="red", opacity=0.05, line_width=0)
    fig1.add_hrect(y0=4, y1=7, fillcolor="yellow", opacity=0.05, line_width=0)
    fig1.add_hrect(y0=7, y1=10, fillcolor="green", opacity=0.05, line_width=0)

    fig1.update_layout(
        yaxis_range=[0, 11],
        yaxis_title="Mood Score (1-10)",
        xaxis_title="Date"
    )
    st.plotly_chart(fig1, use_container_width=True)

st.divider()

# --- EMOTION BREAKDOWN FOR MONTH ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎭 Emotion Distribution")

    if not month_df.empty:
        emotion_counts = month_df["dominant_emotion"].value_counts().reset_index()
        emotion_counts.columns = ["Emotion", "Count"]

        fig2 = px.pie(
            emotion_counts,
            names="Emotion",
            values="Count",
            color="Emotion",
            color_discrete_map=EMOTION_COLORS,
            title=f"Emotions in {month_names[selected_month]}",
            hole=0.4
        )
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("📋 Daily Entries")

    if not month_df.empty:
        display = month_df[["date", "mood_score", "dominant_emotion", "note"]].copy()
        display["date"] = display["date"].dt.strftime("%b %d")
        display = display.sort_values("date", ascending=False)
        display.columns = ["Date", "Mood", "Emotion", "Note"]
        st.dataframe(display.reset_index(drop=True), use_container_width=True)