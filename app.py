from google import genai
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import gradio as gr

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_prayer_times(city):
    try:
        url = "https://api.aladhan.com/v1/timingsByCity"
        params = {"city": city, "country": "AE", "method": 2}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data["code"] != 200:
            return None
        return data["data"]["timings"]
    except Exception:
        return None


def get_next_prayer(timings):
    prayer_order = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    now = datetime.now().strftime("%H:%M")
    for prayer in prayer_order:
        if now < timings[prayer]:
            return prayer, timings[prayer]
    return 'Fajr', timings['Fajr']


def generate_reminder(prayer_name, city, context, faith="Muslim"):
    if faith == "Muslim":
        prompt = f"""
        Generate a warm, encouraging reminder for a Muslim student 
        that it's almost time for {prayer_name} prayer in {city}. 
        It's a {context}. Keep it to 2-3 sentences, 
        respectful and motivating.
        """
    else:
        prompt = f"""
        Generate a warm, encouraging reminder for a Christian student 
        that it's time for their personal prayer/reflection in {city}. 
        It's a {context}. Keep it to 2-3 sentences, 
        respectful and faith-affirming.
        """
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Could not generate reminder right now. Please try again shortly."


def muslim_tab(city, context):
    if not city.strip():
        return "Please enter a city name.", "", ""

    times = get_prayer_times(city)
    if not times:
        return "Could not find prayer times for that city. Please check the city name and try again.", "", ""

    next_prayer, next_time = get_next_prayer(times)
    reminder = generate_reminder(next_prayer, city, context, "Muslim")

    times_display = (
        f"Fajr:    {times['Fajr']}\n"
        f"Dhuhr:   {times['Dhuhr']}\n"
        f"Asr:     {times['Asr']}\n"
        f"Maghrib: {times['Maghrib']}\n"
        f"Isha:    {times['Isha']}"
    )

    next_info = f"Next prayer: {next_prayer} at {next_time}"
    return times_display, next_info, reminder


def get_next_christian_prayer(prayer_times_input):
    now = datetime.now().strftime("%H:%M")
    lines = prayer_times_input.strip().split("\n")

    next_prayer_name = None
    next_prayer_time = None

    for line in lines:
        if ":" in line:
            # Split on last colon to get time
            parts = line.rsplit(":", 1)
            if len(parts) == 2:
                prayer_name = parts[0].strip()
                prayer_time = parts[1].strip()
                # Make sure it looks like a time
                if len(prayer_time) <= 5 and prayer_time.replace(":", "").isdigit():
                    if now < prayer_time:
                        next_prayer_name = prayer_name
                        next_prayer_time = prayer_time
                        break

    # If no upcoming prayer found today, return the first one
    if not next_prayer_name and lines:
        first_line = lines[0].rsplit(":", 1)
        if len(first_line) == 2:
            next_prayer_name = first_line[0].strip()
            next_prayer_time = first_line[1].strip()

    return next_prayer_name, next_prayer_time


def christian_tab(city, prayer_times_input, context):
    if not city.strip():
        return "Please enter a city name.", ""
    if not prayer_times_input.strip():
        return "Please enter at least one prayer time.", ""

    next_prayer_name, next_prayer_time = get_next_christian_prayer(prayer_times_input)

    if not next_prayer_name:
        return "Could not read your prayer times. Please use the format shown in the placeholder.", ""

    prompt = f"""
    Generate a warm, encouraging reminder for a Christian student 
    in {city} that their {next_prayer_name} is coming up at {next_prayer_time}.
    It's a {context}. Keep it to 2-3 sentences, 
    respectful and faith-affirming.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )
        reminder = response.text
    except Exception:
        reminder = "Could not generate reminder right now. Please try again shortly."

    schedule = (
        f"Your prayer schedule:\n{prayer_times_input}\n\n"
        f"Next up: {next_prayer_name} at {next_prayer_time}"
    )
    return schedule, reminder


with gr.Blocks(title="Tawakkul & Grace") as app:
    gr.Markdown("# Tawakkul & Grace 🌙✝️")
    gr.Markdown("### A multi-faith prayer and reflection companion for Dubai's students")

    with gr.Tabs():
        with gr.Tab("🌙 Muslim Prayer Times"):
            city_input = gr.Textbox(label="Your City", value="Dubai")
            context_input = gr.Dropdown(
                choices=["normal day", "exam week", "weekend"],
                label="How's your day?",
                value="normal day"
            )
            submit_muslim = gr.Button("Get Prayer Times & Reminder")
            times_output = gr.Textbox(label="Today's Prayer Times")
            next_output = gr.Textbox(label="Next Prayer")
            reminder_output = gr.Textbox(label="Your AI Reminder")

            submit_muslim.click(
                fn=muslim_tab,
                inputs=[city_input, context_input],
                outputs=[times_output, next_output, reminder_output]
            )

        with gr.Tab("✝️ Christian Prayer Schedule"):
            city_input_c = gr.Textbox(label="Your City", value="Dubai")
            prayer_times_input = gr.Textbox(
                label="Your Prayer Times",
                placeholder="e.g.\nMorning prayer: 07:00\nMidday reflection: 12:30\nEvening prayer: 18:00",
                lines=4
            )
            context_input_c = gr.Dropdown(
                choices=["normal day", "exam week", "weekend"],
                label="How's your day?",
                value="normal day"
            )
            submit_christian = gr.Button("Get Reflection Reminder")
            schedule_output = gr.Textbox(label="Your Prayer Schedule")
            reminder_output_c = gr.Textbox(label="Your AI Reminder")

            submit_christian.click(
                fn=christian_tab,
                inputs=[city_input_c, prayer_times_input, context_input_c],
                outputs=[schedule_output, reminder_output_c]
            )

app.launch()