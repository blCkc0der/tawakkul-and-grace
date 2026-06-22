from google import genai
from dotenv import load_dotenv
import os
import requests
from datetime import datetime

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_prayer_times(city):
    url = "https://api.aladhan.com/v1/timingsByCity"
    params = {"city": city, "country": "AE", "method": 2}
    response = requests.get(url, params=params)
    data = response.json()
    return data["data"]["timings"]

def generate_reminder(prayer_name, city, context="normal day"):
    prompt = f"""
    Generate a warm, encouraging reminder for a Muslim student 
    that it's almost time for {prayer_name} prayer in {city}. 
    It's a {context}. Keep it to 2-3 sentences, 
    respectful and motivating.
    """
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )
    return response.text

# Test the combination
times = get_prayer_times("Dubai")
reminder = generate_reminder("Dhuhr", "Dubai", "exam week")

import gradio as gr


def muslim_reminder(city, context):
    times = get_prayer_times(city)
    reminder = generate_reminder("Dhuhr", city, context)

    times_display = (
        f"Fajr: {times['Fajr']}\n"
        f"Dhuhr: {times['Dhuhr']}\n"
        f"Asr: {times['Asr']}\n"
        f"Maghrib: {times['Maghrib']}\n"
        f"Isha: {times['Isha']}"
    )
    return times_display, reminder


interface = gr.Interface(
    fn=muslim_reminder,
    inputs=[
        gr.Textbox(label="Your City", value="Dubai"),
        gr.Dropdown(
            choices=["normal day", "exam week", "weekend"],
            label="How's your day?",
            value="normal day"
        )
    ],
    outputs=[
        gr.Textbox(label="Today's Prayer Times"),
        gr.Textbox(label="Your AI Reminder")
    ],
    title="Tawakkul & Grace 🌙✝️",
    description="A multi-faith prayer and reflection companion for Dubai's students"
)

interface.launch()