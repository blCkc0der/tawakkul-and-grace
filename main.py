from google import genai
from dotenv import load_dotenv
import os

# load the .env file
load_dotenv()

# set up a client
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# send first request
'''generate_content_stream'''
response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="why is the sky blue?"
)

print(response.text)