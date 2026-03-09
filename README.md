# 🔍 MoodLens

🌐 **Live Demo:** [moodlens.streamlit.app](https://sharathreddykottam-moodlens.streamlit.app/)
> Analyze emotions, track your daily mood and build journaling streaks — built with Python, Streamlit & HuggingFace AI

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red?style=flat-square)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Latest-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Live-green?style=flat-square)

---

## 📖 About

**MoodLens** is an AI-powered mood tracking and daily journal web app.
Speak or type how you feel — AI analyzes your emotions, tracks patterns
over time, and helps you build a consistent journaling habit with streak tracking.

---

## ✨ Features

### 🤖 AI Emotion Analysis
- Detects 7 emotions — joy, sadness, anger, fear, surprise, disgust, neutral
- Voice input — speak and AI transcribes + analyzes instantly
- Powered by HuggingFace Whisper + emotion detection models

### 🗓️ Daily Journal
- One check-in per day — speak or type
- Mood score 1-10 with emoji labels
- Personal notes for context

### 📅 Mood Calendar
- Visual calendar showing emotion per day
- Monthly overview with consistency metrics
- Mood score trend with color zones

### 🔥 Streaks & Consistency
- Current and longest streak tracking
- Dynamic badges — Bronze to Legendary
- Weekly consistency charts
- Last 30 days activity grid

### 📊 Insights & History
- Emotion trends over time
- Radar chart of emotion balance
- Hour of day analysis
- Full history with search and export

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web app framework |
| HuggingFace Whisper | Speech to text |
| HuggingFace RoBERTa | Emotion detection |
| Pandas | Data handling |
| Plotly | Interactive charts |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/SharathReddyKottam/moodlens.git
cd moodlens
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your HuggingFace token
Create a `.env` file:
```
HF_TOKEN=your_token_here
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 📁 Project Structure
```
moodlens/
│
├── app.py                    # Home — emotion analyzer
│
├── pages/
│   ├── 1_History.py          # Analysis history
│   ├── 2_Insights.py         # Charts & patterns
│   ├── 3_Journal.py          # Daily check-in
│   ├── 4_Calendar.py         # Mood calendar
│   └── 5_Streaks.py          # Streaks & consistency
│
├── utils/
│   └── analyzer.py           # HuggingFace API functions
│
├── data/                     # CSV storage (auto created)
│   ├── history.csv
│   └── journal.csv
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 👨‍💻 Author

**SharathReddy**
- GitHub: [@SharathReddyKottam](https://github.com/SharathReddyKottam)
- LinkedIn: [SharathReddy](https://www.linkedin.com/in/sharathreddyk/)

---

## 📄 License
MIT License

---

*Built with ❤️ using Python, Streamlit & HuggingFace*
