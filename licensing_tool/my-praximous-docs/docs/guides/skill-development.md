---
id: skill-development
title: Skill Development Guide
sidebar_label: Skill Development
---

# Praximous Skill Development Guide

Welcome to the Praximous Skill Development Guide! This document provides all the information you need to create, test, and integrate new custom Smart Skills into the Praximous ecosystem.

## 1. Introduction

### Purpose of Praximous Skills
Praximous Skills are modular, self-contained units of functionality that extend the capabilities of the Praximous system. They can perform specific tasks, interact with external APIs, process data, or provide specialized logic. The goal is to create a rich library of skills that can be orchestrated by Praximous to solve complex problems.

### Overview of the Skill Architecture
-   **`BaseSkill`**: An abstract base class (`core.skill_manager.BaseSkill`) that all skills must inherit from. It provides common functionalities like a standardized response builder (`_build_response`).
-   **`SkillManager`**: A core component (`core.skill_manager.SkillManager`) responsible for discovering, loading, and managing all available skills. It typically scans a designated `skills/` directory.
-   **Skill Invocation**: Skills are invoked via the main Praximous API endpoint (e.g., `/api/v1/process`) by specifying the skill's unique `task_type` (which corresponds to the skill's `name` attribute).

## 2. Getting Started

### Prerequisites
-   A working Python 3.9+ environment.
-   Praximous project cloned and basic dependencies installed (see `requirements.txt`).
-   Familiarity with Python, `asyncio`, and basic API concepts.
-   Understanding of Praximous core concepts (Identity, Providers, API endpoint).

### Setting up the Development Environment
1.  Ensure your Praximous instance is running or can be run locally.
2.  It's recommended to use a virtual environment for managing dependencies.

## 3. Creating a New Skill

Follow these steps to create a new skill:

### Using the Template
Start by copying `skills/template_skill.py` to a new file in the `skills/` directory.

### File Naming Conventions
Name your skill file descriptively using lowercase and underscores, ending with `_skill.py`.
*Example: `image_analysis_skill.py`*

### Class Naming Conventions
Use CamelCase for your skill class name, ending with `Skill`.
*Example: `ImageAnalysisSkill`*

### Skill `name` Attribute
Each skill class must have a `name` class attribute. This string:
-   Must be unique across all skills.
-   Should be lowercase with underscores.
-   Will be used as the `task_type` in API requests to invoke this skill.
*Example: `name: str = "image_analyzer"`*

### Implementing `__init__(self)`
If your skill requires specific initialization (e.g., loading a machine learning model, setting up an API client, reading configuration):
-   Define an `__init__` method.
-   **Crucially, call `super().__init__()` at the beginning of your `__init__` method.**
-   Load API keys or sensitive configurations from environment variables (e.g., using `os.getenv("MY_API_KEY")`). Do not hardcode them.

```python
import os
from core.logger import log
from core.skill_manager import BaseSkill # Assuming BaseSkill is here
from typing import Any, Dict, Optional # For type hints

class MyCustomSkill(BaseSkill):
    name: str = "my_custom_tool"
    my_api_key: str = None

    def __init__(self):
        super().__init__()
        self.my_api_key = os.getenv("MY_CUSTOM_SKILL_API_KEY")
        if not self.my_api_key:
            log.warning(f"{self.name}: MY_CUSTOM_SKILL_API_KEY is not set. Some operations might fail.")
        # self.client = SomeLibraryClient(api_key=self.my_api_key)
        log.info(f"{self.name} initialized.")
```

### Implementing `async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]`
This asynchronous method contains the core logic of your skill.
-   **`prompt: str`**: The primary text input to the skill. Can be used as default data if specific parameters aren't provided.
-   **`**kwargs: Any`**: A dictionary of additional parameters passed in the API request.
-   **Operations**: Use `kwargs.get("operation", "default_operation_name").lower()` to allow a single skill to perform multiple distinct actions.
-   **Parameter Validation**: Check for required parameters from `kwargs` and handle missing or invalid inputs gracefully.
-   **Standardized Response**: Use `self._build_response(success: bool, data: Optional[Dict] = None, error: Optional[str] = None, details: Optional[str] = None)` to return a consistent JSON response.
    -   `success=True`: For successful execution. `data` should contain the results.
    -   `success=False`: For errors. `error` should be a short error type, and `details` can provide more information.
-   **Error Handling**: Wrap your logic in `try...except` blocks to catch potential exceptions and return a proper error response.

### Implementing `def get_capabilities(self) -> Dict[str, Any]`
This method describes what your skill can do. The output is used for documentation, discoverability by other systems or UIs, and potentially for dynamic prompt generation.
-   Return a dictionary with the following structure:
    ```json
    {
        "skill_name": self.name,
        "description": "A concise description of what the skill does overall.",
        "operations": {
            "operation_name_1": {
                "description": "Description of this specific operation.",
                "parameters_schema": {
                    "prompt": {"type": "string", "description": "Primary input text."},
                    "param1_name": {"type": "string", "description": "Description of param1.", "optional": False, "default": "value"},
                    "param2_name": {"type": "integer", "description": "Description of param2.", "optional": True}
                },
                "example_request_payload": {
                    "task_type": self.name,
                    "operation": "operation_name_1",
                    "prompt": "Sample prompt text",
                    "param1_name": "sample_value"
                }
            },
            "operation_name_2": {
                // ... similar structure ...
            }
        }
    }
    ```
-   `parameters_schema`: Define expected parameters, their types (`string`, `integer`, `boolean`, `number`, `array`, `object`), descriptions, and whether they are `optional` (defaults to `False` if not specified). You can also add a `default` value.

### Logging
Use the centralized logger for consistent logging:
`from core.logger import log`
*Examples: `log.info("Skill started")`, `log.error("An error occurred", exc_info=True)`*

## 4. Managing Dependencies
If your skill requires new external Python libraries:
1.  Add them to the `requirements.txt` file in the project root, preferably with a pinned version (e.g., `new_library==1.2.3`).
2.  Re-run `pip install -r requirements.txt` (or `docker-compose build` if using Docker).

## 5. Skill Registration & Discovery
Praximous's `SkillManager` is designed to automatically discover and load skills:
-   Ensure your skill's Python file (e.g., `my_custom_skill.py`) is placed directly within the `skills/` directory.
-   The `SkillManager` scans this directory on startup, imports valid skill modules, and instantiates skill classes that inherit from `BaseSkill`.

## 6. Testing Your Skill

### Unit Testing
-   Write unit tests for the core logic of your skill, especially the `execute` method for different operations and inputs.
-   Mock external dependencies (like API clients) if necessary.

### API Testing
-   Once Praximous is running, you can test your skill by sending a POST request to the `/api/v1/process` endpoint.
-   Use tools like `curl`, Postman, or a simple Python script with `httpx`.
-   **Example Request Body (JSON):**
    ```json
    {
        "task_type": "your_skill_name", // Matches skill's `name` attribute
        "operation": "your_operation_name", // Optional, if skill has multiple operations
        "prompt": "Some input text for the skill.",
        "your_custom_param": "value_for_param"
        // ... other parameters as defined in get_capabilities ...
    }
    ```

## 7. Best Practices & Security Considerations

-   **Input Validation**: Always validate and sanitize inputs received in `prompt` and `kwargs` to prevent errors and potential security issues.
-   **Secure API Key Handling**: Load API keys and sensitive credentials from environment variables. Never hardcode them.
-   **External API Calls**:
    -   Handle potential network errors, timeouts, and API rate limits gracefully.
    -   Use asynchronous HTTP clients (like `httpx`) for non-blocking I/O.
-   **Clear Code**: Write readable, maintainable code with good comments and docstrings.
-   **Idempotency**: If applicable, design operations to be idempotent (calling them multiple times with the same input produces the same result).
-   **Resource Management**: Ensure any resources (files, network connections) are properly closed or released, especially in `__init__` or long-running operations.

## 8. Example Workflow (Brief)

1.  Copy `skills/template_skill.py` to `skills/greeting_skill.py`.
2.  Rename class to `GreetingSkill`, set `name = "greeter"`.
3.  In `execute`, if `operation == "say_hello"`:
    `name_param = kwargs.get("name", "World")`
    `return self._build_response(success=True, data={"greeting": f"Hello, {name_param}!"})`
4.  Update `get_capabilities` to describe the "say_hello" operation and its "name" parameter.
5.  Test via API: `{"task_type": "greeter", "operation": "say_hello", "name": "Praximous Developer"}`.

Happy skill building!