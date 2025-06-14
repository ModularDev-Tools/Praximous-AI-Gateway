# skills/weather_skill.py
from typing import Dict, Any, Optional
from core.skill_manager import BaseSkill
from core.logger import log
import httpx
import os # For API Key

# It's good practice to load API keys from environment variables
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5" # Example for OpenWeatherMap

class WeatherSkill(BaseSkill):
    name: str = "weather_tool"

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "get_current_weather").lower()
        location = kwargs.get("location")
        units = kwargs.get("units", "metric") # metric, imperial, standard

        log.info(f"WeatherSkill executing. Operation: '{operation}', Location: '{location}', Units: '{units}', Prompt: '{prompt}'")

        if not WEATHER_API_KEY:
            return self._build_response(success=False, error="Configuration Error", details="WEATHER_API_KEY is not set.")
        if not location:
            return self._build_response(success=False, error="Input Error", details="'location' parameter is required.")

        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
            "units": units
        }

        endpoint = ""
        if operation == "get_current_weather":
            endpoint = f"{WEATHER_API_BASE_URL}/weather"
        elif operation == "get_forecast": # This is a simplified example; forecast APIs are often more complex
            endpoint = f"{WEATHER_API_BASE_URL}/forecast" # OpenWeatherMap forecast needs count or other params
            # params["cnt"] = kwargs.get("days", 5) * 8 # Example: 5 days, 3-hour intervals
        else:
            return self._build_response(success=False, error="Unsupported Operation", details=f"Operation '{operation}' is not supported.")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status() # Raises an exception for 4XX/5XX responses
                weather_data = response.json()
                
                # You might want to parse and simplify the weather_data before returning
                return self._build_response(success=True, data={"location": location, "weather_info": weather_data, "units": units})
        except httpx.HTTPStatusError as e:
            log.error(f"WeatherSkill HTTP error: {e.response.status_code} - {e.response.text}", exc_info=True)
            error_details = f"API request failed with status {e.response.status_code}."
            try: # Try to get more specific error from API response
                error_details += f" Message: {e.response.json().get('message', 'No specific message.')}"
            except:
                pass
            return self._build_response(success=False, error="API Error", details=error_details)
        except Exception as e:
            log.error(f"WeatherSkill unexpected error: {e}", exc_info=True)
            return self._build_response(success=False, error="Internal Skill Error", details=str(e))

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Fetches current weather or a forecast for a specified location. Requires WEATHER_API_KEY environment variable.",
            "operations": {
                "get_current_weather": {
                    "description": "Gets the current weather conditions for a location.",
                    "parameters_schema": {
                        "prompt": {"type": "string", "description": "Optional descriptive text."},
                        "location": {"type": "string", "description": "City name or zip code (e.g., 'London,UK', '94040,US')."},
                        "units": {"type": "string", "enum": ["metric", "imperial", "standard"], "default": "metric", "description": "Units for temperature and other measurements."}
                    },
                    "example_request_payload": {"task_type": self.name, "operation": "get_current_weather", "location": "Paris,FR", "units": "metric"}
                },
                "get_forecast": {
                    "description": "Gets a weather forecast for a location (API specific, may require more params).",
                    "parameters_schema": {
                        "prompt": {"type": "string", "description": "Optional descriptive text."},
                        "location": {"type": "string", "description": "City name or zip code."},
                        "units": {"type": "string", "enum": ["metric", "imperial", "standard"], "default": "metric", "description": "Units for temperature."}
                        # "days": {"type": "integer", "default": 5, "description": "Number of days for forecast (API dependent)."}
                    },
                    "example_request_payload": {"task_type": self.name, "operation": "get_forecast", "location": "Tokyo,JP"}
                }
            }
        }