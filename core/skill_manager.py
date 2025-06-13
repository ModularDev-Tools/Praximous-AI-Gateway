# core/skill_manager.py
import abc
import importlib
import inspect
import os
from typing import Dict, Type, Any
from typing import Optional # Added for _build_response
from core.logger import log

SKILLS_DIR = "skills"

class BaseSkill(abc.ABC):
    """
    Abstract base class for all Smart Skills.
    Each skill must define a unique `name` that corresponds to the `task_type`
    in API requests.
    """
    name: str = "base_skill" # Unique identifier for the skill, maps to task_type

    @abc.abstractmethod
    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Executes the skill's logic.

        Args:
            prompt: The primary text input or instruction for the skill.
            **kwargs: Additional data or configuration specific to the skill execution.

        Returns:
            A dictionary containing the result of the skill's execution.
        """
        pass

    def _build_response(self, success: bool, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None, details: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a standardized response dictionary for skill execution results.
        Inspired by BaseSkillTool._build_response_dict.
        """
        response = {"success": success}
        if data is not None:
            response["data"] = data
        if error is not None:
            response["error"] = error
        if details is not None:
            response["details"] = details
        return response

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Returns a dictionary describing the skill's commands or operations,
        their arguments, and a brief description.
        This method SHOULD be overridden by subclasses to provide specific capabilities.
        Example structure:
        {
            "skill_name": self.name,
            "description": "A brief description of what the skill does overall.",
            "operations": { // Or "commands" if more appropriate
                "operation_name_1": {
                    "description": "What this operation does.",
                    "parameters_schema": { ... Pydantic model or JSON schema ... },
                    "example_request_payload": { ... }
                },
            }
        }
        """
        return {"skill_name": self.name, "description": "No specific capabilities defined by this skill.", "operations": {}}

class SkillManager:
    def __init__(self):
        self.skills: Dict[str, Type[BaseSkill]] = {}
        self._discover_skills()

    def _discover_skills(self):
        log.info(f"Discovering skills in '{SKILLS_DIR}' directory...")
        if not os.path.exists(SKILLS_DIR) or not os.path.isdir(SKILLS_DIR):
            log.warning(f"Skills directory '{SKILLS_DIR}' not found. No skills will be loaded.")
            return

        for filename in os.listdir(SKILLS_DIR):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = f"{SKILLS_DIR}.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for _, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseSkill) and obj is not BaseSkill:
                            if hasattr(obj, 'name') and obj.name != BaseSkill.name:
                                self.skills[obj.name] = obj
                                log.info(f"Discovered and registered skill: '{obj.name}' from {module_name}")
                            else:
                                log.warning(f"Skill class {obj.__name__} in {module_name} is missing a unique 'name' attribute or uses the default 'base_skill'. Skipping.")
                except Exception as e:
                    log.error(f"Failed to load skill from {module_name}: {e}", exc_info=True)
        log.info(f"Skill discovery complete. {len(self.skills)} skills registered.")

    def get_skill(self, task_type: str) -> Type[BaseSkill] | None:
        return self.skills.get(task_type)

# Global instance of SkillManager, skills are discovered at import time.
skill_manager = SkillManager()