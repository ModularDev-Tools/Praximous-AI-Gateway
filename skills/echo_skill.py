# skills/echo_skill.py
from typing import Dict, Any
from core.skill_manager import BaseSkill
from core.logger import log

class EchoSkill(BaseSkill):
    name: str = "echo" # This must match the task_type in API requests

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        log.info(f"EchoSkill executing with prompt: '{prompt}'")
        # kwargs could be used for additional parameters if the ProcessRequest model is extended
        
        response_data = {
            "echoed_prompt": prompt,
            "message": "Prompt was successfully echoed."
        }
        return self._build_response(success=True, data=response_data)

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "A simple skill that echoes back the provided prompt.",
            "operations": {
                "echo_operation": { # Generic operation name for this simple skill
                    "description": "Returns the input prompt verbatim.",
                    "parameters_schema": {"prompt": {"type": "string", "description": "The text to be echoed."}},
                    "example_request_payload": {"task_type": "echo", "prompt": "Hello Praximous!"}
                }
            }
        }