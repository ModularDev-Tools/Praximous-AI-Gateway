---
id: process-endpoint
title: /api/v1/process Endpoint
sidebar_label: /process Endpoint
---

# `/api/v1/process` Endpoint

The `/api/v1/process` endpoint is the primary interface for interacting with Praximous. It allows users and applications to execute Smart Skills, which can range from simple utility tasks to complex AI-driven workflows involving Large Language Models (LLMs) or other external services.

## Endpoint Details

*   **Method**: `POST`
*   **URL**: `/api/v1/process`
*   **Content-Type**: `application/json`

## Request Body Schema

The request body must be a JSON object with the following fields:

| Field                       | Type    | Required | Description                                                                                                                               |
| :-------------------------- | :------ | :------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| `task_type`                 | string  | Yes      | The unique name of the Smart Skill to execute (e.g., `default_llm_tasks`, `echo`). This corresponds to the skill's `name` attribute.         |
| `prompt`                    | string  | No       | The primary text input for the skill. Its interpretation depends on the skill.                                                            |
| `operation`                 | string  | No       | For skills that support multiple operations, this specifies which one to perform. Defaults to the skill's predefined default operation.     |
| `provider_name`             | string  | No       | Specifies a particular AI provider (from `config/providers.yaml`) to use for this request, overriding the default or skill-defined provider. |
| `stream`                    | boolean | No       | If `true`, indicates that the response should be streamed (e.g., for LLM token-by-token output). Default is `false`. (Future capability)    |
| `...other_skill_parameters` | any     | No       | Additional key-value pairs specific to the requirements of the invoked `task_type` and `operation`. Refer to the skill's capabilities.    |

### Example Request:

```json
{
  "task_type": "default_llm_tasks",
  "prompt": "Explain the concept of on-premise AI gateways in two sentences.",
  "operation": "generate_text",
  "provider_name": "gemini_pro_model"
}
```

## Response Body Schema

Praximous returns a standardized JSON response.

### Success Response (HTTP 200 OK)

| Field               | Type    | Description                                                                    |
| :------------------ | :------ | :----------------------------------------------------------------------------- |
| `success`           | boolean | Always `true` for successful operations.                                       |
| `data`              | object  | Contains the skill-specific results of the operation.                          |
| `request_id`        | string  | A unique identifier for this specific request, useful for logging and tracing. |
| `execution_time_ms` | number  | The time taken by Praximous to process the request, in milliseconds.           |
| `provider_used`     | string  | (Optional) The name of the AI provider that was ultimately used for the task.  |

#### Example Success Response:

```json
{
  "success": true,
  "data": {
    "response": "On-premise AI gateways act as secure intermediaries, allowing enterprises to leverage powerful AI models while keeping sensitive data within their own infrastructure. They enhance control, reduce external dependencies, and can manage costs effectively."
  },
  "request_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "execution_time_ms": 1234.56,
  "provider_used": "gemini_pro_model"
}
```

### Error Response (HTTP 4xx or 5xx)

| Field        | Type    | Description                                                                                                |
| :----------- | :------ | :--------------------------------------------------------------------------------------------------------- |
| `success`    | boolean | Always `false` for errors.                                                                                 |
| `error`      | string  | A short, machine-readable error type (e.g., `SkillNotFound`, `ValidationError`, `ProviderError`).            |
| `details`    | string  | A more detailed, human-readable message explaining the error.                                              |
| `request_id` | string  | (Optional) A unique identifier for this specific request, if available at the time of error.               |

#### Example Error Response (Skill Not Found):

```json
{
  "success": false,
  "error": "SkillNotFound",
  "details": "The requested skill 'non_existent_skill' could not be found.",
  "request_id": "b2c3d4e5-f6g7-8901-2345-67890abcdeff"
}
```

#### Example Error Response (Validation Error):

```json
{
  "success": false,
  "error": "ValidationError",
  "details": "Missing required parameter: 'target_language' for 'translate_text' operation in 'translation_skill'.",
  "request_id": "c3d4e5f6-g7h8-9012-3456-7890abcdef01"
}
```

## Task Type Examples

The behavior of the `/api/v1/process` endpoint is determined by the `task_type` and other parameters provided. Here are a few examples:

### 1. General LLM Task

This uses the `default_llm_tasks` skill (or a similarly configured one) to interact with a configured LLM.

**Request:**
```json
{
  "task_type": "default_llm_tasks",
  "prompt": "What are the key benefits of using Praximous?",
  "operation": "generate_text"
}
```

**Expected `data` in Response:**
```json
{
  "response": "Praximous offers benefits like enhanced data security by keeping data on-premise, resilience through provider agnosticism and failover, and extensibility via Smart Skills for complex workflow automation."
}
```

### 2. Echo Skill

A simple skill that echoes back the provided prompt or a message.

**Request:**
```json
{
  "task_type": "echo",
  "prompt": "Hello Praximous!"
}
```

**Expected `data` in Response:**
```json
{
  "echoed_message": "Hello Praximous!"
}
```

### 3. Skill with Custom Parameters

Imagine a skill named `data_analyzer` with an operation `calculate_sum`.

**Request:**
```json
{
  "task_type": "data_analyzer",
  "operation": "calculate_sum",
  "numbers": [10, 20, 30, 40]
}
```

**Expected `data` in Response:**
```json
{
  "sum": 100
}
```

:::tip Finding Skill Parameters
To discover the specific `task_type` names, available `operation`s, and required/optional parameters for each skill, you can:
*   Refer to the **Skill Development Guide** for how skills define their capabilities.
*   If available, use the `/api/v1/skills` and `/api/v1/skills/{skill_name}/capabilities` endpoints (or the GUI) to get a list of registered skills and their detailed capabilities.
:::