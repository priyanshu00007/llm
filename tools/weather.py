"""Weather tool — OpenWeather API with mock fallback."""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

_MOCK = {
    "london": "15°C, Partly cloudy, Humidity 72%, Wind 5 m/s",
    "new york": "18°C, Clear sky, Humidity 55%, Wind 4 m/s",
    "tokyo": "22°C, Sunny, Humidity 60%, Wind 3 m/s",
    "paris": "14°C, Overcast, Humidity 80%, Wind 6 m/s",
    "sydney": "25°C, Sunny, Humidity 50%, Wind 7 m/s",
}


def get_weather(city: str) -> str:
    """
    Get current weather for a city via OpenWeather API.

    Falls back to mock data when OPENWEATHER_API_KEY is not set.

    Args:
        city: City name, e.g. "London".

    Returns:
        Weather summary string.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not api_key or api_key == "your_openweather_api_key_here":
        mock = _MOCK.get(city.lower())
        if mock:
            return f"Weather in {city}: {mock}  (mock data — add OPENWEATHER_API_KEY for live data)"
        return (
            f"Weather in {city}: 20°C, Clear sky, Humidity 60%, Wind 4 m/s  "
            "(mock data — add OPENWEATHER_API_KEY for live data)"
        )

    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        data = resp.json()
        if resp.status_code != 200:
            return f"Error: {data.get('message', 'city not found')}"

        m = data["main"]
        w = data["weather"][0]
        return (
            f"Weather in {city}:\n"
            f"  Temperature : {m['temp']}°C (feels like {m['feels_like']}°C)\n"
            f"  Condition   : {w['description'].capitalize()}\n"
            f"  Humidity    : {m['humidity']}%\n"
            f"  Wind        : {data['wind']['speed']} m/s"
        )
    except requests.Timeout:
        return "Error: request timed out."
    except Exception as exc:
        return f"Error getting weather: {exc}"
