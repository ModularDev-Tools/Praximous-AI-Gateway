---
id: configuration
title: Configuration Guide
sidebar_label: Configuration
---

# Praximous Configuration

Praximous is designed to be highly configurable to adapt to your specific environment and requirements. Configuration is primarily managed through three key files:

1.  **`.env`**: For environment variables, especially sensitive data like API keys.
2.  **`config/identity.yaml`**: To define the persona and core settings of your Praximous instance.
3.  **`config/providers.yaml`**: To configure the AI model providers Praximous will use.

Let's dive into each of these.

## 1. Environment Variables (`.env` file)

The `.env` file is used to store environment-specific configurations and sensitive data, such as API keys. This file should be present in the root directory of your Praximous project and **should not be committed to version control** if it contains sensitive information.

Praximous loads variables from this file at startup.

### Common Variables:

*   **`GEMINI_API_KEY`**: Your API key for accessing Google Gemini models.
    *   Example: `GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"`
*   **`OLLAMA_API_URL`**: The base URL for your Ollama instance if you are using local models.
    *   Example (if Ollama is running on the same machine, outside Docker): `OLLAMA_API_URL="http://localhost:11434"`
    *   Example (if Praximous is running in Docker and Ollama is on the host): `OLLAMA_API_URL="http://host.docker.internal:11434"`
*   **`LOG_LEVEL`**: Sets the logging verbosity. Common values are `INFO`, `DEBUG`, `WARNING`, `ERROR`.
    *   Example: `LOG_LEVEL="INFO"`
*   **`PRAXIMOUS_PORT`**: The port on which the Praximous FastAPI application will run. Defaults to `7777` if not set.
    *   Example: `PRAXIMOUS_PORT="8000"`
*   **`GUI_ENABLED`**: Set to `true` to enable the web GUI, `false` to disable. Defaults to `true`.
    *   Example: `GUI_ENABLED="true"`

### Creating `.env`:

If you don't have one, create a file named `.env` in the root of your Praximous project and add the necessary variables.

```env
# .env Example
GEMINI_API_KEY="AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OLLAMA_API_URL="http://localhost:11434"
LOG_LEVEL="DEBUG"
PRAXIMOUS_PORT="7777"
GUI_ENABLED="true"
```

## 2. Identity Configuration (`config/identity.yaml`)

The `config/identity.yaml` file defines the "persona" and core operational parameters of your Praximous instance. This includes how it identifies itself and default behaviors.

```yaml
# config/identity.yaml Example
identity:
  name: "PraximousPrime"
  version: "0.2.0"
  description: "Your On-Premise Orchestration Layer for Enterprise AI."
  system_prompt: |
    You are PraximousPrime, an advanced AI orchestration layer.
    Your goal is to process user requests efficiently and securely, leveraging available AI models and tools.
    Be concise and helpful.
  default_model: "gemini_pro_model" # Corresponds to a 'name' in providers.yaml
  # Optional: Define default parameters for LLM interactions
  # default_llm_params:
  #   temperature: 0.7
  #   max_output_tokens: 1024
```

### Key Fields:

*   **`name`**: A custom name for your Praximous instance.
*   **`version`**: The version of your Praximous deployment.
*   **`description`**: A brief description of this instance.
*   **`system_prompt`**: A default system-level prompt that can be used to instruct LLMs on their role or persona when interacting through Praximous. Skills can override or augment this.
*   **`default_model`**: The `name` of the AI provider (from `providers.yaml`) to be used by default if a skill or request doesn't specify one.
*   **`default_llm_params`** (Optional): You can define global default parameters (like `temperature`, `max_output_tokens`) for LLM interactions. These can be overridden at the provider level in `providers.yaml` or by specific skills.

## 3. Provider Configuration (`config/providers.yaml`)

The `config/providers.yaml` file is where you define and configure the various AI model providers that Praximous can connect to. This allows Praximous to be model-agnostic and support failover.

```yaml
# config/providers.yaml Example
providers:
  - name: "gemini_pro_model"      # Unique name for this provider configuration
    type: "gemini"                 # Type of provider (e.g., "gemini", "ollama")
    model: "gemini-1.5-flash-latest" # Specific model identifier
    api_key_env: "GEMINI_API_KEY"  # Env variable for the API key
    priority: 1                    # Lower number = higher priority
    enabled: true                  # Set to false to disable this provider
    # Optional: Provider-specific parameters
    # params:
    #   temperature: 0.6

  - name: "ollama_mistral"
    type: "ollama"
    model: "mistral"               # Model name as known by Ollama
    base_url_env: "OLLAMA_API_URL" # Env variable for Ollama server URL
    priority: 2
    enabled: true
    # params:
    #   temperature: 0.8
```

### Key Fields for each provider entry:

*   **`name`**: A unique identifier for this provider configuration (e.g., `gemini_flash_creative`, `ollama_llama3_local`). This name is used in `identity.yaml`'s `default_model` or can be specified by skills.
*   **`type`**: The type of provider. Praximous uses this to determine how to interact with the service (e.g., `gemini`, `ollama`, `openai`). The `ProviderManager` must have a handler for this type.
*   **`model`**: The specific model identifier for that provider (e.g., `gemini-1.5-flash-latest`, `llama3`, `gpt-4-turbo`).
*   **`api_key_env`** (For API-based providers): The name of the environment variable (from `.env`) that holds the API key for this provider.
*   **`base_url_env`** (For self-hosted providers like Ollama): The name of the environment variable that holds the base URL for the provider's API.
*   **`priority`**: An integer indicating the selection priority. Lower numbers have higher priority. Used for default selection and failover (if the higher priority provider fails, Praximous can try the next one).
*   **`enabled`**: A boolean (`true` or `false`) to enable or disable this provider configuration without removing it.
*   **`params`** (Optional): A dictionary of provider-specific parameters (e.g., `temperature`, `max_tokens`, `top_p`) that will be used when interacting with this provider, unless overridden by a skill.

## How They Work Together

1.  Praximous starts and loads configurations from `.env`.
2.  It then reads `identity.yaml` to understand its basic operational parameters and default model.
3.  Next, it parses `providers.yaml` to know which AI providers are available, how to connect to them (using API keys/URLs from `.env`), and their priorities.
4.  When a skill needs an AI model, it can either specify a provider `name` or rely on the `default_model` from `identity.yaml`. The `ProviderManager` then uses the information from `providers.yaml` and `.env` to make the actual call to the AI service.

By carefully setting up these files, you can create a robust, secure, and flexible Praximous instance tailored to your AI orchestration needs.

This guide should provide a comprehensive overview for users looking to configure Praximous. You can further enhance it with more specific examples or advanced configuration scenarios as your project evolves.

After saving this, restart your Docusaurus server and check out the new configuration guide!
