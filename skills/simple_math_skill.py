# skills/simple_math_skill.py
from typing import Dict, Any, Union
from core.skill_manager import BaseSkill
from core.logger import log

class SimpleMathSkill(BaseSkill):
    name: str = "simple_math"

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        # The 'prompt' for this skill could be a general instruction,
        # but the core data comes from kwargs.
        log.info(f"SimpleMathSkill executing. Prompt: '{prompt}', Args: {kwargs}")

        num1 = kwargs.get("num1")
        num2 = kwargs.get("num2")
        operation = kwargs.get("operation", "add").lower() # Default to 'add'

        if not all(isinstance(n, (int, float)) for n in [num1, num2]):
            return self._build_response(success=False, error="Input error", details="Both 'num1' and 'num2' must be provided as numbers.")

        result: Union[int, float, str]
        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            if num2 == 0:
                return self._build_response(success=False, error="Math error", details="Cannot divide by zero.")
            result = num1 / num2
        else:
            return self._build_response(
                success=False,
                error=f"Unsupported operation: {operation}",
                details="Supported operations: add, subtract, multiply, divide."
            )

        response_data = {
            "num1": num1,
            "num2": num2,
            "operation": operation,
            "result": result,
            "message": prompt # The original prompt can be part of the successful response data
        }
        return self._build_response(success=True, data=response_data)

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Performs simple arithmetic operations (add, subtract, multiply, divide) on two numbers.",
            "operations": {
                "calculate": { # Generic operation name for this skill
                    "description": "Applies a specified arithmetic operation to two numbers.",
                    "parameters_schema": {
                        "prompt": {"type": "string", "description": "Optional descriptive text for the operation."},
                        "num1": {"type": "number", "description": "The first number."},
                        "num2": {"type": "number", "description": "The second number."},
                        "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"], "description": "The arithmetic operation to perform."}
                    },
                    "example_request_payload": {
                        "task_type": "simple_math",
                        "prompt": "Calculate 10 + 5",
                        "num1": 10,
                        "num2": 5,
                        "operation": "add"
                    }
                }
            }
        }