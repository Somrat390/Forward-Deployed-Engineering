import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

WEATHER_API_URL = "https://api.weatherapi.com/v1/current.json"


def current_weather(city: str) -> dict:
    """
    Get the current weather information for a city.

    Args:
        city: Name of the city.

    Returns:
        Dictionary containing current weather information.
    """

    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        return {"error": "WEATHER_API_KEY is not configured."}

    if not city or not city.strip():
        return {"error": "Please provide a city name."}

    params = {
        "key": api_key,
        "q": city.strip(),
        "aqi": "no"
    }

    try:
        response = requests.get(
            WEATHER_API_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return {
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "temperature_c": data["current"]["temp_c"],
            "temperature_f": data["current"]["temp_f"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "wind_kph": data["current"]["wind_kph"],
            "feels_like_c": data["current"]["feelslike_c"],
            "last_updated": data["current"]["last_updated"]
        }

    except requests.exceptions.HTTPError:
        try:
            error_data = response.json()
            return {"error": error_data.get("error", {}).get(
                "message", "Weather API request failed."
            )}
        except ValueError:
            return {"error": "Weather API returned an HTTP error."}

    except requests.exceptions.Timeout:
        return {"error": "Weather API request timed out."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}

    except (KeyError, TypeError):
        return {"error": "Unexpected response format from WeatherAPI."}