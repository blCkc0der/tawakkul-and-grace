import requests

def get_prayer_times(city, country="AE"):
    url = "https://api.aladhan.com/v1/timingsByCity"
    params = {
        "city": city,
        "country": country,
        "method": 2  # Islamic Society of North America method
    }
    response = requests.get(url, params=params)
    data = response.json()
    timings = data["data"]["timings"]
    return timings

# Test it
times = get_prayer_times("Dubai")
print(times)