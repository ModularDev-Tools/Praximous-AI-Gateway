# skills/text_manipulation_skill.py
from typing import Dict, Any
from core.skill_manager import BaseSkill
from core.logger import log

class TextManipulationSkill(BaseSkill):
    name: str = "text_manipulation"

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "none").lower()
        log.info(f"TextManipulationSkill executing with prompt: '{prompt}', operation: '{operation}'")

        original_text = prompt
        modified_text = original_text

        if operation == "uppercase":
            modified_text = original_text.upper()
        elif operation == "lowercase":
            modified_text = original_text.lower()
        elif operation == "reverse":
            modified_text = original_text[::-1]
        else:
            return self._build_response(
                success=False,
                data={"original_text": original_text},
                error=f"Unsupported operation: {operation}",
                details="Supported operations are: uppercase, lowercase, reverse."
            )

        response_data = {
            "original_text": original_text,
            "operation_performed": operation,
            "modified_text": modified_text
        }
        return self._build_response(success=True, data=response_data)

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Performs various text manipulation operations like uppercase, lowercase, or reverse.",
            "operations": {
                "manipulate": { # Generic operation name for this skill
                    "description": "Applies a specified manipulation to the input text.",
                    "parameters_schema": {
                        "prompt": {"type": "string", "description": "The text to be manipulated."},
                        "operation": {"type": "string", "enum": ["uppercase", "lowercase", "reverse"], "description": "The manipulation to perform."}
                    },
                    "example_request_payload": {
                        "task_type": "text_manipulation",
                        "prompt": "Sample Text",
                        "operation": "uppercase"
                    }
                }
            }
        }