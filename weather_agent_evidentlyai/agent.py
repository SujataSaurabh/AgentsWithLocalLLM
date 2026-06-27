import os
import requests
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm 
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from observability import adk_evidently_logger

os.environ["OPENAI_API_KEY"] = "mock-local-key"

def get_current_weather(location: str) -> str:
    """Gets the current weather conditions for a specified city or location.

    Args:
        location: The name of the city, e.g., 'San Francisco, CA'.
    """
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(location)}&count=1&language=en&format=json"
        geo_response = requests.get(geo_url, timeout=5)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            return f"Error: Could not resolve the location '{location}' to real geographic coordinates."
            
        result = geo_data["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        resolved_name = f"{result.get('name')}, {result.get('admin1', '')} ({result.get('country', '')})"

        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation",
            "temperature_unit": "celsius", 
            "timezone": "auto"
        }
        
        weather_response = requests.get(weather_url, params=params, timeout=5)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        current = weather_data.get("current", {})
        temp = current.get("temperature_2m")
        feels_like = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        precip = current.get("precipitation")
        
        return (
            f"Current weather conditions for {resolved_name}: "
            f"The temperature is {temp}°C (Feels like {feels_like}°C). "
            f"Humidity is at {humidity}% with {precip}mm of current precipitation."
        )

    except Exception as e:
        return f"Error trying to fetch weather data: {str(e)}"

cloud_open_model = LiteLlm(
    model="openai/Qwen/Qwen2.5-7B-Instruct", 
    api_base="http://localhost:8000/v1", 
    api_key="mock-local-key",
    custom_llm_provider="openai"
)

root_agent = Agent(
    model=cloud_open_model,
    name="CloudOpenAssistant",
    description='A helpful assistant that can answer general questions and fetch weather data.',
    instruction="Analyze the user request precisely. If they ask about weather, use your tool.",
    tools=[get_current_weather],
    after_agent_callback=[adk_evidently_logger]
)

 