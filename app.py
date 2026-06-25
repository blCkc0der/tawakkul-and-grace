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


def christian_tab(city, p1n, p2n, p3n, p4n, p5n, p6n, p7n,
                  p1t, p2t, p3t, p4t, p5t, p6t, p7t, context):
    if not city.strip():
        return "Please enter a city name.", ""

    all_slots = [
        (p1n, p1t), (p2n, p2t), (p3n, p3t),
        (p4n, p4t), (p5n, p5t), (p6n, p6t), (p7n, p7t)
    ]

    prayer_slots = [
        (name.strip(), time)
        for name, time in all_slots
        if name.strip()
    ]

    if not prayer_slots:
        return "Please add at least one prayer.", ""

    next_prayer_name, next_prayer_time = get_next_christian_prayer(prayer_slots)

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
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

    schedule_lines = "\n".join([
        f"{name}: {time}" for name, time in prayer_slots
    ])
    schedule = (
        f"Your prayer schedule:\n{schedule_lines}\n\n"
        f"Next up: {next_prayer_name} at {next_prayer_time}"
    )
    return schedule, reminder
    if not city.strip():
        return "Please enter a city name.", ""

    all_slots = [
        (p1n, p1t), (p2n, p2t), (p3n, p3t),
        (p4n, p4t), (p5n, p5t), (p6n, p6t), (p7n, p7t)
    ]

    # Only include slots with a real name
    prayer_slots = [
        (name.strip(), time)
        for name, time in all_slots
        if name.strip()
    ]

    if not prayer_slots:
        return "Please add at least one prayer.", ""

    next_prayer_name, next_prayer_time = get_next_christian_prayer(prayer_slots)

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
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

    schedule_lines = "\n".join([
        f"{name}: {time}" for name, time in prayer_slots
    ])
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
            city_input_c = gr.Textbox(label="Your City", value="Dubai")

            gr.Markdown("### Your Prayer Schedule")
            gr.Markdown("Add your prayer times below. Click **+ Add Prayer** to add more slots (up to 7).")

            # Generate time options
            time_options = []
            for hour in range(24):
                for minute in [0, 15, 30, 45]:
                    time_options.append(f"{hour:02d}:{minute:02d}")

            # Store all prayer rows and their visibility state
            prayer_rows = []
            prayer_names = []
            prayer_times = []

            # Default values for each slot
            defaults = [
                ("Morning Prayer", "07:00"),
                ("Midday Prayer", "12:00"),
                ("Evening Prayer", "19:00"),
                ("", "08:00"),
                ("", "10:00"),
                ("", "14:00"),
                ("", "21:00"),
            ]

            # Create 7 slots, first 3 visible, rest hidden
            for i, (default_name, default_time) in enumerate(defaults):
                visible = i < 3
                with gr.Row(visible=visible) as row:
                    name_input = gr.Textbox(
                        label=f"Prayer {i + 1}",
                        value=default_name,
                        scale=2
                    )
                    time_input = gr.Dropdown(
                        choices=time_options,
                        label="Time",
                        value=default_time,
                        scale=1
                    )
                prayer_rows.append(row)
                prayer_names.append(name_input)
                prayer_times.append(time_input)

            # Track how many slots are visible
            slot_count = gr.State(value=3)

            add_btn = gr.Button("+ Add Prayer", size="sm", variant="secondary")

            context_input_c = gr.Dropdown(
                choices=["normal day", "exam week", "weekend"],
                label="How's your day?",
                value="normal day"
            )

            submit_christian = gr.Button(
                "Get Reflection Reminder",
                variant="primary"
            )
            schedule_output = gr.Textbox(label="Your Prayer Schedule")
            reminder_output_c = gr.Textbox(label="Your AI Reminder")


            # + button logic — reveals next hidden row
            def add_prayer_slot(current_count):
                if current_count >= 7:
                    return [gr.Row(visible=True)] * 7 + [current_count]
                new_count = current_count + 1
                updates = []
                for i in range(7):
                    updates.append(gr.Row(visible=i < new_count))
                updates.append(new_count)
                return updates


            add_btn.click(
                fn=add_prayer_slot,
                inputs=[slot_count],
                outputs=prayer_rows + [slot_count]
            )

            submit_christian.click(
                fn=christian_tab,
                inputs=[city_input_c] + prayer_names + prayer_times + [context_input_c],
                outputs=[schedule_output, reminder_output_c]
            )

app.launch()