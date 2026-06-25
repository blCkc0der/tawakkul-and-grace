# Tawakkul & Grace

An AI-powered, multi-faith prayer and reflection companion built for Dubai's diverse student community.

## About

As a Christian studying in Dubai, I've come to appreciate the different faiths and beliefs of the people around me. Tawakkul & Grace is my attempt to build something that reflects that shared experience rather than serving just one community.

The app supports both Muslim and Christian users:
- **Muslim users** get accurate, location-based prayer times pulled from real prayer time data, paired with AI-generated reminders.
- **Christian users** can set up a personalised prayer schedule — choosing how many times a day they want to pray and at what times — also paired with AI-generated reflection prompts.

Both paths include smart, snoozable reminders that adapt their tone based on context (e.g. exam week vs. a normal day).

## Status

Work in progress. built as part of the Decoding Data Science Building AI Application Challenge (June 2026).

Currently on Day 2: setting up the development environment and beginning API integration.

## Tech Stack

- **Python**
- **Aladhan API** — for Islamic prayer times
- **OpenAI API** — for AI-generated reminders and reflections
- **Gradio** — for the user interface
- Deployment planned via **Hugging Face Spaces**

## How to Run

1. Clone the repo
2. Create a `.env` file with your Gemini API key:
   `GEMINI_API_KEY=your-key-here`
3. Install dependencies:
   `pip install google-genai gradio requests python-dotenv`
4. Run the app:
   `python app.py`
5. Open `http://127.0.0.1:7860` in your browser

## Architecture

- **Aladhan API** — fetches real Islamic prayer times by city
- **Google Gemini API** — generates personalised AI reminders
- **Gradio** — provides the web interface
- **python-dotenv** — manages API key securely via `.env`

## Project Goal

To build a working, deployed AI application that reflects Dubai's multi-faith student community, demonstrating real API and LLM integration, and to grow it into a genuine portfolio project.

## Author

Daniella Nwambu — BSc Data Science student, Heriot-Watt University Dubai
