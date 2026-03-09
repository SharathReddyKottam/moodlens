import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import date, timedelta
from utils.analyzer import EMOTION_COLORS, EMOTION_EMOJIS

# --- PAGE CONFIG ---
st.set_page_config(page_title="Streaks", page_icon="🔥", layout="wide")

st.title("🔥 Streaks & Consistency")
st.write("Track your journaling habit and consistency over time.")

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
all_dates = sorted(journal_df["date"].dt.date.unique().tolist())

# --- STREAK CALCULATIONS ---
def calculate_current_streak(dates):
    """Current consecutive days streak."""
    if not dates:
        return 0
    dates = sorted(set(dates), reverse=True)
    streak = 0
    check = date.today()
    for d in dates:
        if d == check:
            streak += 1
            check = check - timedelta(days=1)
        else:
            break
    return streak

def calculate_longest_streak(dates):
    """Longest streak ever achieved."""
    if not dates:
        return 0
    dates = sorted(set(dates))
    longest = 1
    current = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest

def calculate_weekly_consistency(dates, weeks=8):
    """Returns consistency % for last N weeks."""
    weekly = []
    today = date.today()
    for w in range(weeks - 1, -1, -1):
        week_start = today - timedelta(days=today.weekday() + 7 * w)
        week_end = week_start + timedelta(days=6)
        days_in_week = sum(
            1 for d in dates
            if week_start <= d <= week_end
        )
        consistency = round((days_in_week / 7) * 100, 1)
        weekly.append({
            "Week": week_start.strftime("%b %d"),
            "Days": days_in_week,
            "Consistency (%)": consistency
        })
    return pd.DataFrame(weekly)

current_streak = calculate_current_streak(all_dates)
longest_streak = calculate_longest_streak(all_dates)
total_days = len(all_dates)
total_possible = (date.today() - all_dates[0]).days + 1 if all_dates else 1
overall_consistency = round((total_days / total_possible) * 100, 1)

st.divider()

# --- STREAK HERO SECTION ---
st.subheader("🏆 Your Streaks")

col1, col2, col3, col4 = st.columns(4)

with col1:
    streak_color = "#FF4500" if current_streak >= 7 else "#FFD700" if current_streak >= 3 else "#A9A9A9"
    st.markdown(
        f"""
        <div style="
            background-color: {streak_color}22;
            border: 2px solid {streak_color};
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        ">
            <h1 style="font-size: 50px; margin: 0">🔥</h1>
            <h2 style="color: {streak_color}; margin: 5px 0">{current_streak}</h2>
            <p style="margin: 0; color: gray">Current Streak</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="
            background-color: #FFD70022;
            border: 2px solid #FFD700;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        ">
            <h1 style="font-size: 50px; margin: 0">⭐</h1>
            <h2 style="color: #FFD700; margin: 5px 0">{longest_streak}</h2>
            <p style="margin: 0; color: gray">Longest Streak</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="
            background-color: #6495ED22;
            border: 2px solid #6495ED;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        ">
            <h1 style="font-size: 50px; margin: 0">📝</h1>
            <h2 style="color: #6495ED; margin: 5px 0">{total_days}</h2>
            <p style="margin: 0; color: gray">Total Days</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    consistency_color = "#228B22" if overall_consistency >= 70 else "#FFD700" if overall_consistency >= 40 else "#FF4500"
    st.markdown(
        f"""
        <div style="
            background-color: {consistency_color}22;
            border: 2px solid {consistency_color};
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        ">
            <h1 style="font-size: 50px; margin: 0">📊</h1>
            <h2 style="color: {consistency_color}; margin: 5px 0">{overall_consistency}%</h2>
            <p style="margin: 0; color: gray">Overall Consistency</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# --- STREAK BADGE ---
st.subheader("🎖️ Your Badge")

if current_streak >= 30:
    badge = "🏆 Legendary — 30+ day streak!"
    badge_color = "#FFD700"
elif current_streak >= 14:
    badge = "💎 Diamond — 14+ day streak!"
    badge_color = "#00CED1"
elif current_streak >= 7:
    badge = "🥇 Gold — 7+ day streak!"
    badge_color = "#FFD700"
elif current_streak >= 3:
    badge = "🥈 Silver — 3+ day streak!"
    badge_color = "#C0C0C0"
elif current_streak >= 1:
    badge = "🥉 Bronze — Keep going!"
    badge_color = "#CD7F32"
else:
    badge = "🌱 Beginner — Start your streak today!"
    badge_color = "#228B22"

st.markdown(
    f"""
    <div style="
        background-color: {badge_color}22;
        border-left: 5px solid {badge_color};
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
    ">
        {badge}
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# --- WEEKLY CONSISTENCY CHART ---
st.subheader("📅 Weekly Consistency")

weekly_df = calculate_weekly_consistency(all_dates)

fig1 = px.bar(
    weekly_df,
    x="Week",
    y="Consistency (%)",
    color="Consistency (%)",
    color_continuous_scale=["red", "yellow", "green"],
    title="Journaling Consistency — Last 8 Weeks",
    text="Consistency (%)"
)
fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig1.update_layout(
    showlegend=False,
    yaxis_range=[0, 120]
)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# --- MOOD SCORE OVER ALL TIME ---
st.subheader("😊 Mood Score — All Time")

mood_df = journal_df.sort_values("date")

fig2 = px.line(
    mood_df,
    x="date",
    y="mood_score",
    title="Your Mood Journey",
    markers=True,
    color_discrete_sequence=["cornflowerblue"]
)

# add trend line
fig2.add_trace(go.Scatter(
    x=mood_df["date"],
    y=mood_df["mood_score"].rolling(window=3, min_periods=1).mean(),
    name="3-day average",
    line=dict(color="orange", dash="dash", width=2)
))

fig2.add_hrect(y0=1, y1=4, fillcolor="red", opacity=0.05, line_width=0)
fig2.add_hrect(y0=4, y1=7, fillcolor="yellow", opacity=0.05, line_width=0)
fig2.add_hrect(y0=7, y1=10, fillcolor="green", opacity=0.05, line_width=0)

fig2.update_layout(yaxis_range=[0, 11])
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- ACTIVITY GRID ---
st.subheader("🟩 Activity Grid — Last 30 Days")

today = date.today()
last_30 = [today - timedelta(days=i) for i in range(29, -1, -1)]
journaled_dates = set(all_dates)

# build grid data
grid_data = []
for d in last_30:
    journaled = d in journaled_dates
    if journaled:
        entry = journal_df[journal_df["date"].dt.date == d]
        mood = entry["mood_score"].values[0] if not entry.empty else 5
    else:
        mood = 0
    grid_data.append({
        "date": d,
        "journaled": journaled,
        "mood": mood,
        "label": d.strftime("%b %d")
    })

grid_df = pd.DataFrame(grid_data)

fig3 = px.bar(
    grid_df,
    x="label",
    y=[1] * len(grid_df),
    color="mood",
    color_continuous_scale=["#333333", "red", "yellow", "green"],
    title="Last 30 Days — Green = journaled & happy, Dark = missed",
    range_color=[0, 10]
)
fig3.update_traces(marker_line_width=0)
fig3.update_layout(
    showlegend=False,
    yaxis=dict(visible=False),
    xaxis_title="",
    bargap=0.1
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --- TIPS ---
st.subheader("💡 Tips to Keep Your Streak")

if current_streak == 0:
    st.info("🌱 Start today! Even one sentence counts. The hardest part is beginning.")
elif current_streak < 3:
    st.info("🥉 Good start! Try to journal at the same time every day to build the habit.")
elif current_streak < 7:
    st.warning("🥈 You're building momentum! You're just a few days away from a week streak!")
elif current_streak < 14:
    st.success("🥇 Amazing! You've built a solid habit. Keep it going — 14 days is next!")
else:
    st.success(f"🏆 Incredible! {current_streak} days straight. You're unstoppable!")