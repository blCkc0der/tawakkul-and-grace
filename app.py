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


def get_next_christian_prayer(prayer_slots):
    # prayer_slots is a list of (name, time) tuples
    now = datetime.now().strftime("%H:%M")

    # Sort by time
    sorted_slots = sorted(prayer_slots, key=lambda x: x[1])

    for name, time in sorted_slots:
        if now < time:
            return name, time

    # Past all prayers — return first one (tomorrow)
    return sorted_slots[0][0], sorted_slots[0][1]


def christian_tab(city, p1_name, p1_time, p2_name, p2_time,
                  p3_name, p3_time, context):
    if not city.strip():
        return "Please enter a city name.", ""

    # Build list of prayer slots, filter out empty ones
    prayer_slots = []
    for name, time in [(p1_name, p1_time), (p2_name, p2_time),
                       (p3_name, p3_time)]:
        if name.strip() and time:
            prayer_slots.append((name.strip(), time))

    if not prayer_slots:
        return "Please add at least one prayer.", ""

    next_prayer_name, next_prayer_time = get_next_christian_prayer(prayer_slots)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=f"""
            Generate a warm, encouraging reminder for a Christian student 
            in {city} that their {next_prayer_name} is coming up at {next_prayer_time}.
            It's a {context}. Keep it to 2-3 sentences, 
            respectful and faith-affirming.
            """
        )
        reminder = response.text
    except Exception:
        reminder = "Could not generate reminder right now. Please try again shortly."

    schedule_lines = "\n".join([f"{name}: {time}"
                                for name, time in prayer_slots])
    schedule = (
        f"Your prayer schedule:\n{schedule_lines}\n\n"
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
            with gr.Tab("✝️ Christian Prayer Schedule"):
                city_input_c = gr.Textbox(label="Your City", value="Dubai")

                gr.Markdown("### Your Prayer Schedule")
                gr.Markdown("Add your prayer times below. Click + to add more.")

                # Generate time options 00:00 to 23:45 in 15 min intervals
                time_options = []
                for hour in range(24):
                    for minute in [0, 15, 30, 45]:
                        time_options.append(f"{hour:02d}:{minute:02d}")

                # Three default prayer slots
                with gr.Row():
                    prayer1_name = gr.Textbox(
                        label="Prayer 1",
                        value="Morning Prayer",
                        scale=2
                    )
                    prayer1_time = gr.Dropdown(
                        choices=time_options,
                        label="Time",
                        value="07:00",
                        scale=1
                    )

                with gr.Row():
                    prayer2_name = gr.Textbox(
                        label="Prayer 2",
                        value="Midday Prayer",
                        scale=2
                    )
                    prayer2_time = gr.Dropdown(
                        choices=time_options,
                        label="Time",
                        value="12:00",
                        scale=1
                    )

                with gr.Row():
                    prayer3_name = gr.Textbox(
                        label="Prayer 3",
                        value="Evening Prayer",
                        scale=2
                    )
                    prayer3_time = gr.Dropdown(
                        choices=time_options,
                        value="19:00",
                        label="Time",
                        scale=1
                    )

                context_input_c = gr.Dropdown(
                    choices=["normal day", "exam week", "weekend"],
                    label="How's your day?",
                    value="normal day"
                )
                submit_christian = gr.Button("Get Reflection Reminder", variant="primary")
                schedule_output = gr.Textbox(label="Your Prayer Schedule")
                reminder_output_c = gr.Textbox(label="Your AI Reminder")

                submit_christian.click(
                    fn=christian_tab,
                    inputs=[
                        city_input_c,
                        prayer1_name, prayer1_time,
                        prayer2_name, prayer2_time,
                        prayer3_name, prayer3_time,
                        context_input_c
                    ],
                    outputs=[schedule_output, reminder_output_c]
                )

app.launch()