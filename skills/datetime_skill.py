# skills/datetime_skill.py
from typing import Dict, Any, Optional
from core.skill_manager import BaseSkill
from core.logger import log
from datetime import datetime, timezone
import pytz # For timezone handling, ensure 'pytz' is in your requirements.txt

class DateTimeSkill(BaseSkill):
    name: str = "datetime_tool" # This must match the task_type in API requests

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "get_current_datetime").lower()
        log.info(f"DateTimeSkill executing. Operation: '{operation}', Prompt: '{prompt}', Args: {kwargs}")

        try:
            if operation == "get_current_datetime":
                tz_str = kwargs.get("timezone", "UTC")
                try:
                    tz = pytz.timezone(tz_str)
                except pytz.UnknownTimeZoneError:
                    return self._build_response(success=False, error="Invalid Timezone", details=f"Timezone '{tz_str}' is not recognized.")
                
                current_time = datetime.now(tz)
                response_data = {
                    "datetime_iso": current_time.isoformat(),
                    "timezone": tz_str,
                    "message": f"Current datetime in {tz_str}."
                }
                return self._build_response(success=True, data=response_data)

            elif operation == "format_datetime":
                datetime_str = kwargs.get("datetime_str")
                format_str = kwargs.get("format_string", "%Y-%m-%d %H:%M:%S %Z") # Default format
                input_tz_str = kwargs.get("input_timezone", "UTC") # Assume input is UTC if not specified

                if not datetime_str:
                    return self._build_response(success=False, error="Input Error", details="'datetime_str' is required for formatting.")

                try:
                    # Attempt to parse the datetime string (this might need more robust parsing)
                    # For simplicity, assuming ISO format or that it's timezone-aware if input_tz_str is not UTC
                    dt_obj = datetime.fromisoformat(datetime_str.replace("Z", "+00:00")) # Handle Z for UTC
                    
                    # If a specific input timezone is given, localize it
                    source_tz = pytz.timezone(input_tz_str)
                    if dt_obj.tzinfo is None:
                        dt_obj = source_tz.localize(dt_obj)
                    else:
                        dt_obj = dt_obj.astimezone(source_tz)

                    formatted_datetime = dt_obj.strftime(format_str)
                    response_data = {
                        "original_datetime": datetime_str,
                        "format_string": format_str,
                        "formatted_datetime": formatted_datetime,
                        "timezone_applied_for_formatting": dt_obj.tzinfo.tzname(None) if dt_obj.tzinfo else "Assumed " + input_tz_str
                    }
                    return self._build_response(success=True, data=response_data)
                except Exception as e:
                    log.error(f"DateTimeSkill format_datetime error: {e}", exc_info=True)
                    return self._build_response(success=False, error="Formatting Error", details=str(e))
            else:
                return self._build_response(success=False, error="Unsupported Operation", details=f"Operation '{operation}' is not supported.")
        except Exception as e:
            log.error(f"DateTimeSkill unexpected error: {e}", exc_info=True)
            return self._build_response(success=False, error="Internal Skill Error", details=str(e))

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Provides date and time related functionalities.",
            "operations": {
                "get_current_datetime": {
                    "description": "Gets the current date and time, optionally in a specified timezone.",
                    "parameters_schema": {"prompt": {"type": "string", "description": "Optional descriptive text."}, "timezone": {"type": "string", "default": "UTC", "description": "Timezone name (e.g., 'America/New_York', 'UTC')."}},
                    "example_request_payload": {"task_type": self.name, "operation": "get_current_datetime", "timezone": "Europe/London"}
                },
                "format_datetime": {
                    "description": "Formats a given datetime string into a specified format.",
                    "parameters_schema": {"prompt": {"type": "string", "description": "Optional descriptive text."}, "datetime_str": {"type": "string", "description": "ISO 8601 datetime string to format (e.g., '2023-10-26T10:00:00Z')."}, "format_string": {"type": "string", "default": "%Y-%m-%d %H:%M:%S %Z", "description": "Python strftime format string."}, "input_timezone": {"type": "string", "default": "UTC", "description": "Timezone of the input datetime_str if not specified in the string."}},
                    "example_request_payload": {"task_type": self.name, "operation": "format_datetime", "datetime_str": "2024-01-15T14:30:00+02:00", "format_string": "%A, %B %d, %Y %I:%M %p %Z"}
                }
            }
        }