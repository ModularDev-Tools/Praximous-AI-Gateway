# skills/template_skill.py
"""
Template for Creating a New Praximous Skill

Instructions:
1.  Rename this file to `your_skill_name_skill.py` (e.g., `image_generation_skill.py`).
2.  Rename the class `TemplateSkill` to `YourSkillNameSkill` (e.g., `ImageGenerationSkill`).
3.  Update the `name` class attribute to a unique, descriptive, lowercase_and_underscore string.
    This name will be used as the `task_type` in API requests to invoke this skill.
    (e.g., `name: str = "image_generator"`)
4.  Implement the `__init__` method if your skill requires specific initialization,
    such as loading models, API clients, or configurations. Remember to call `super().__init__()`.
5.  Implement the `execute` async method:
    -   This is the core logic of your skill.
    -   It receives `prompt: str` and `**kwargs: Any`.
    -   Use `kwargs.get("operation", "default_operation")` to handle different functionalities
        within the same skill.
    -   Access other parameters passed in `kwargs`.
    -   Use `self._build_response(success=True/False, data={}, error="", details="")`
        to return a standardized response dictionary.
    -   Use `from core.logger import log` for logging (e.g., `log.info()`, `log.error()`).
6.  Implement the `get_capabilities` method:
    -   This method should return a dictionary describing the skill, its operations,
        expected parameters, and example request payloads.
    -   This information is used for documentation, discoverability, and potentially by UIs or other systems.
7.  Add any necessary imports. If you add new external libraries, update `requirements.txt`.
8.  Ensure your skill is placed in the `skills/` directory for automatic discovery by the SkillManager.
"""
from typing import Dict, Any, Optional
from core.skill_manager import BaseSkill
from core.logger import log

# Example: If your skill needs an API key from environment variables
# import os
# MY_SERVICE_API_KEY = os.getenv("MY_SERVICE_API_KEY")

class TemplateSkill(BaseSkill):
    # 3. Update the skill name (used as task_type)
    name: str = "template_skill_placeholder"

    def __init__(self):
        super().__init__()
        # 4. Initialization logic (if any)
        # Example:
        # if not MY_SERVICE_API_KEY:
        #     log.warning(f"{self.name}: MY_SERVICE_API_KEY is not set. Some operations might fail.")
        # self.my_service_client = SomeServiceClient(api_key=MY_SERVICE_API_KEY)
        log.info(f"{self.name} initialized.")

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        # 5. Implement the core skill logic
        operation = kwargs.get("operation", "default_operation_placeholder").lower()
        # example_param = kwargs.get("example_param")

        log.info(f"{self.name} executing. Operation: '{operation}', Prompt: '{prompt[:50]}...', Args: {kwargs}")

        # Example: Check for required API key if an operation needs it
        # if operation == "some_api_dependent_operation" and not MY_SERVICE_API_KEY:
        #     return self._build_response(success=False, error="Configuration Error", details="MY_SERVICE_API_KEY is not set.")

        try:
            if operation == "default_operation_placeholder":
                # Replace with your actual logic for this operation
                response_data = {"message": f"Executed default operation with prompt: {prompt}", "params_received": kwargs}
                return self._build_response(success=True, data=response_data)
            # Add more elif blocks for other operations
            # elif operation == "another_operation":
            #     # ... logic for another_operation ...
            #     return self._build_response(success=True, data={...})
            else:
                return self._build_response(success=False, error="Unsupported Operation", details=f"Operation '{operation}' is not supported by {self.name}.")
        except Exception as e:
            log.error(f"{self.name} error during operation '{operation}': {e}", exc_info=True)
            return self._build_response(success=False, error="Internal Skill Error", details=str(e))

    def get_capabilities(self) -> Dict[str, Any]:
        # 6. Describe the skill's capabilities
        return {
            "skill_name": self.name,
            "description": "A template skill. Replace this with a meaningful description of what your skill does.",
            "operations": {
                "default_operation_placeholder": {
                    "description": "Description of the default operation.",
                    "parameters_schema": {
                        "prompt": {"type": "string", "description": "The main input or query for the skill."},
                        # "example_param": {"type": "string", "optional": True, "description": "An example optional parameter."}
                    },
                    "example_request_payload": {"task_type": self.name, "operation": "default_operation_placeholder", "prompt": "Hello from template"}
                }
                # Add descriptions for other operations here
            }
        }

# To make this skill discoverable, ensure it's in the 'skills' directory
# and that SkillManager in your core application is set up to scan this directory.