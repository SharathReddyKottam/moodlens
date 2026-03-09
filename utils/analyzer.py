import requests
import os
from dotenv import load_dotenv

# load token from .env file
load_dotenv()

# --- API SETTINGS ---
EMOTION_API_URL = "https://router.huggingface.co/hf-inference/models/j-hartmann/emotion-english-distilroberta-base"
WHISPER_API_URL = "https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3"

# --- EMOTION COLORS ---
EMOTION_COLORS = {
    "joy":      "#FFD700",
    "sadness":  "#6495ED",
    "anger":    "#FF4500",
    "fear":     "#9370DB",
    "surprise": "#FF8C00",
    "disgust":  "#228B22",
    "neutral":  "#A9A9A9"
}

# --- EMOTION EMOJIS ---
EMOTION_EMOJIS = {
    "joy":      "😊",
    "sadness":  "😢",
    "anger":    "😠",
    "fear":     "😨",
    "surprise": "😲",
    "disgust":  "🤢",
    "neutral":  "😐"
}


def get_token():
    """Gets HuggingFace token from .env file or Streamlit secrets."""
    token = os.getenv("HF_TOKEN")
    if not token:
        try:
            import streamlit as st
            token = st.secrets["HF_TOKEN"]
        except Exception:
            pass
    return token


def analyze_emotion(text):
    """
    Sends text to HuggingFace API and returns emotion scores.
    """
    token = get_token()

    if not token:
        return {"error": "No HuggingFace token found!"}

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(
            EMOTION_API_URL,
            headers=headers,
            json={"inputs": text},
            timeout=30
        )

        if response.status_code != 200:
            return {"error": f"API error: {response.status_code}"}

        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            return result[0]

        return {"error": "Unexpected response format"}

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Try again!"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Check your internet!"}
    except Exception as e:
        return {"error": f"Something went wrong: {str(e)}"}


def transcribe_audio(audio_bytes):
    """
    Sends audio bytes to HuggingFace Whisper API.
    Returns transcribed text.
    """
    token = get_token()

    if not token:
        return {"error": "No HuggingFace token found!"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "audio/wav"
    }

    try:
        response = requests.post(
            WHISPER_API_URL,
            headers=headers,
            data=audio_bytes,
            timeout=60
        )

        if response.status_code != 200:
            return {"error": f"Whisper API error: {response.status_code} — {response.text}"}

        result = response.json()

        # Whisper returns {"text": "transcribed text here"}
        if "text" in result:
            return {"text": result["text"]}

        return {"error": "Unexpected response from Whisper"}

    except requests.exceptions.Timeout:
        return {"error": "Whisper timed out. Try a shorter recording!"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Check your internet!"}
    except Exception as e:
        return {"error": f"Something went wrong: {str(e)}"}


def get_dominant_emotion(emotions):
    """Returns the emotion with the highest score."""
    if isinstance(emotions, dict) and "error" in emotions:
        return None
    return max(emotions, key=lambda x: x["score"])


def format_emotions(emotions):
    """
    Adds color and emoji to each emotion.
    Returns enriched list ready for display.
    """
    if isinstance(emotions, dict) and "error" in emotions:
        return []

    enriched = []
    for item in emotions:
        label = item["label"]
        enriched.append({
            "label": label,
            "score": item["score"],
            "percentage": round(item["score"] * 100, 1),
            "color": EMOTION_COLORS.get(label, "#888888"),
            "emoji": EMOTION_EMOJIS.get(label, "❓")
        })

    return enriched