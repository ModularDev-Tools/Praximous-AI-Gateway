# tests/test_cli_phase1.py
import pytest
import os
import yaml
import sys
from unittest.mock import patch, call
import importlib

# Assuming these are importable from the project root.
# Ensure conftest.py or pytest configuration adds project root to sys.path.
from main import init_identity, rename_system, reset_identity_config, main as main_cli_entry_func
import core.system_context # Import the module to allow reloading

# Test data
DEFAULT_IDENTITY_INPUTS = [
    "Praximous-TestCLI", # system_name
    "Test CLI Corp",     # business_name
    "CLI Testing",       # industry
    "CLI Persona",       # persona_style
    "Low",               # sensitivity_level
    "CLI Location"       # location
]

# These prompts should match what credentials_manager.py generates based on providers.yaml
GEMINI_API_KEY_PROMPT = "Google API Key for Gemini models: " # Corrected to match actual output
OLLAMA_API_URL_PROMPT = "Ollama API URL, e.g., http://localhost:11434 (or press Enter for default: 'http://localhost:11434'): " # Corrected to match actual output

API_KEY_INPUTS_FULL = [
    "test_gemini_cli_key", # For GEMINI_API_KEY
    "http://testhost:1234", # For OLLAMA_API_URL
    "done"  # To exit the "Add/update another env variable?" loop
]
API_KEY_INPUTS_OLLAMA_DEFAULT = [
    "test_gemini_cli_key_ollama_default", # For GEMINI_API_KEY
    "",  # For OLLAMA_API_URL (press Enter to use default)
    "done"  # To exit the "Add/update another env variable?" loop
]


@pytest.fixture
def temp_praximous_env(tmp_path, monkeypatch):
    """
    Sets up a temporary environment for Praximous CLI tests.
    - Changes CWD to tmp_path.
    - Creates a temporary 'config' directory.
    - Monkeypatches path constants in main.py, core.system_context.py,
      and config.credentials_manager.py to use paths within tmp_path.
    - Creates a dummy providers.yaml for API key setup simulation.
    """
    original_cwd = os.getcwd()
    monkeypatch.chdir(tmp_path)

    # Create config directory within tmp_path, as main.py expects 'config/'
    config_dir_relative = "config"
    config_dir_abs = tmp_path / config_dir_relative
    config_dir_abs.mkdir()

    # Define paths relative to the new CWD (tmp_path)
    identity_yaml_rel_path = os.path.join(config_dir_relative, "identity.yaml")
    providers_yaml_rel_path = os.path.join(config_dir_relative, "providers.yaml")
    dot_env_rel_path = ".env"

    # Monkeypatch module constants to use these relative paths
    monkeypatch.setattr("main.CONFIG_PATH", identity_yaml_rel_path)
    monkeypatch.setattr("main.CONFIG_DIR", config_dir_relative)
    monkeypatch.setattr("core.system_context.IDENTITY_CONFIG_PATH", identity_yaml_rel_path)
    monkeypatch.setattr("config.credentials_manager.PROVIDERS_CONFIG_PATH", providers_yaml_rel_path)
    monkeypatch.setattr("config.credentials_manager.ENV_PATH", dot_env_rel_path)

    # Create a dummy providers.yaml in the temp config directory
    dummy_providers_data = {
        "providers": [
            {"name": "google", "api_model_name": "gemini-1.5-flash", "env_var": "GEMINI_API_KEY", "prompt_text": "Google API Key for Gemini models", "required": True, "type": "llm"},
            {"name": "ollama", "api_model_name": "llama3", "env_var": "OLLAMA_API_URL", "prompt_text": "Ollama API URL, e.g., http://localhost:11434", "required": False, "type": "llm", "default_url": "http://localhost:11434"}
        ]
    }
    with open(providers_yaml_rel_path, 'w') as f:
        yaml.dump(dummy_providers_data, f)
    
    yield {
        "tmp_path": tmp_path, # Absolute path to temp dir
        "identity_file_path": tmp_path / identity_yaml_rel_path,
        "env_file_path": tmp_path / dot_env_rel_path,
        "config_dir_path": config_dir_abs,
        "providers_file_path": tmp_path / providers_yaml_rel_path
    }
    monkeypatch.chdir(original_cwd) # Restore CWD after test


def test_init_identity_creates_files_and_prompts_for_keys(temp_praximous_env, caplog):
    """Test Phase 1: Interactive CLI for identity and API key setup."""
    env_paths = temp_praximous_env
    identity_file = env_paths["identity_file_path"]
    env_file = env_paths["env_file_path"]

    all_inputs = DEFAULT_IDENTITY_INPUTS + API_KEY_INPUTS_FULL
    
    with patch('builtins.input', side_effect=all_inputs) as mock_input:
        init_identity()

    assert identity_file.exists()
    with open(identity_file, 'r') as f:
        identity_data = yaml.safe_load(f)
    
    assert identity_data['system_name'] == DEFAULT_IDENTITY_INPUTS[0]
    assert identity_data['business_name'] == DEFAULT_IDENTITY_INPUTS[1]
    assert identity_data['industry'] == DEFAULT_IDENTITY_INPUTS[2]
    assert identity_data['persona_style'] == DEFAULT_IDENTITY_INPUTS[3]
    assert identity_data['sensitivity_level'] == DEFAULT_IDENTITY_INPUTS[4]
    assert identity_data['location'] == DEFAULT_IDENTITY_INPUTS[5]

    assert env_file.exists()
    with open(env_file, 'r') as f:
        env_content = f.read()
    assert f"GEMINI_API_KEY={API_KEY_INPUTS_FULL[0]}" in env_content
    assert f"OLLAMA_API_URL={API_KEY_INPUTS_FULL[1]}" in env_content

    # Check that input was called for all identity fields and API keys
    # Prompts for identity:
    identity_prompts = [
        "System Name (e.g. Praximous-Acme): ", "Business Name: ", "Industry: ",
        "Persona Style (tone): ", "Sensitivity Level (Low/Medium/High): ", "Location: "
    ]
    # Prompts for API keys (order matters based on providers.yaml)
    api_key_prompts = [GEMINI_API_KEY_PROMPT, OLLAMA_API_URL_PROMPT]
    
    # Add the prompt for the "done" loop
    expected_prompts_in_order = [call(p) for p in identity_prompts + api_key_prompts + ["Add/update another env variable? (yes/no/done): "]]
    mock_input.assert_has_calls(expected_prompts_in_order)
    assert mock_input.call_count == len(all_inputs)

    expected_log_config_path = os.path.join('config', 'identity.yaml')
    assert f"Identity configuration saved to {expected_log_config_path}" in caplog.text
    # Correct the expected log message to match actual output from credentials_manager.py
    assert f"Environment variables saved to .env" in caplog.text

def test_init_identity_uses_ollama_default_url(temp_praximous_env, caplog):
    """Test Phase 1: API key setup with default for Ollama."""
    env_paths = temp_praximous_env
    env_file = env_paths["env_file_path"]
    all_inputs = DEFAULT_IDENTITY_INPUTS + API_KEY_INPUTS_OLLAMA_DEFAULT

    with patch('builtins.input', side_effect=all_inputs):
        init_identity()

    assert env_file.exists()
    with open(env_file, 'r') as f:
        env_content = f.read()
    assert f"GEMINI_API_KEY={API_KEY_INPUTS_OLLAMA_DEFAULT[0]}" in env_content
    assert f"OLLAMA_API_URL=http://localhost:11434" in env_content # Check default
    # Correct the expected log message based on credentials_manager.py
    assert f"Environment variables saved to .env" in caplog.text

def test_rename_system_success(temp_praximous_env, caplog):
    """Test Phase 1: Renaming the system."""
    env_paths = temp_praximous_env
    identity_file = env_paths["identity_file_path"]

    initial_identity_data = {"system_name": "OldSystem", "business_name": "OldCorp"}
    with open(identity_file, 'w') as f:
        yaml.dump(initial_identity_data, f)

    new_name = "Praximous-Renamed"
    rename_system(new_name)

    assert identity_file.exists()
    with open(identity_file, 'r') as f:
        updated_identity_data = yaml.safe_load(f)
    
    assert updated_identity_data['system_name'] == new_name
    assert updated_identity_data['business_name'] == "OldCorp"
    expected_log_path = os.path.join('config', 'identity.yaml')
    assert f"System renamed from 'OldSystem' to '{new_name}' in '{expected_log_path}'." in caplog.text

def test_rename_system_no_identity_file(temp_praximous_env, caplog):
    """Test Phase 1: Renaming when identity.yaml doesn't exist."""
    env_paths = temp_praximous_env
    identity_file = env_paths["identity_file_path"]
    assert not identity_file.exists()

    rename_system("AnyName")
    assert not identity_file.exists()
    expected_log_path = os.path.join('config', 'identity.yaml')
    assert f"Identity configuration file '{expected_log_path}' not found. Cannot rename." in caplog.text


def test_reset_identity_success(temp_praximous_env, caplog):
    """Test Phase 1: Resetting identity with user confirmation."""
    env_paths = temp_praximous_env
    identity_file = env_paths["identity_file_path"]

    with open(identity_file, 'w') as f:
        yaml.dump({"system_name": "ToDelete"}, f)
    assert identity_file.exists()

    with patch('builtins.input', return_value='yes') as mock_input:
        reset_identity_config()
    
    expected_prompt_path = os.path.join('config', 'identity.yaml')
    mock_input.assert_called_once_with(f"Are you sure you want to reset the identity by deleting '{expected_prompt_path}'? (yes/no): ")
    assert not identity_file.exists()
    assert f"Identity configuration file '{expected_prompt_path}' has been removed." in caplog.text

def test_reset_identity_cancel(temp_praximous_env, caplog):
    """Test Phase 1: Cancelling identity reset."""
    env_paths = temp_praximous_env
    identity_file = env_paths["identity_file_path"]
    
    with open(identity_file, 'w') as f:
        yaml.dump({"system_name": "ToKeep"}, f)
    assert identity_file.exists()

    with patch('builtins.input', return_value='no'):
        reset_identity_config()
        
    assert identity_file.exists() 
    assert "Identity reset cancelled." in caplog.text

def test_system_context_loading_and_display_name(temp_praximous_env):
    """Test Phase 1: SystemContext loading and display_name derivation."""
    env_paths = temp_praximous_env
    identity_file = env_paths["identity_file_path"]

    # Test case 1: system_name and business_name
    identity_content1 = {"system_name": "Praximous", "business_name": "Acme Solutions Inc."}
    with open(identity_file, 'w') as f: yaml.dump(identity_content1, f)
    reloaded_sc_module1 = importlib.reload(core.system_context)
    sc1 = reloaded_sc_module1.SystemContext()
    assert sc1.system_name == "Praximous"
    assert sc1.business_name == "Acme Solutions Inc."
    assert sc1.display_name == "Praximous-AcmeSolutions"

    # Test case 2: system_name already contains a hyphen
    identity_content2 = {"system_name": "Praximous-Retail", "business_name": "Retail Giant LLC"}
    with open(identity_file, 'w') as f: yaml.dump(identity_content2, f)
    reloaded_sc_module2 = importlib.reload(core.system_context)
    sc2 = reloaded_sc_module2.SystemContext()
    assert sc2.display_name == "Praximous-Retail"

    # Test case 3: Only system_name
    identity_content3 = {"system_name": "MyPraxi"}
    with open(identity_file, 'w') as f: yaml.dump(identity_content3, f)
    reloaded_sc_module3 = importlib.reload(core.system_context)
    sc3 = reloaded_sc_module3.SystemContext()
    assert sc3.display_name == "MyPraxi"

    # Test case 4: No identity file exists
    if identity_file.exists(): os.remove(identity_file)
    reloaded_sc_module4 = importlib.reload(core.system_context)
    sc4 = reloaded_sc_module4.SystemContext()
    assert sc4.system_name == "Praximous-Unconfigured"
    assert sc4.display_name == "Praximous-Unconfigured"


def test_main_cli_init_arg(temp_praximous_env, monkeypatch, caplog):
    """Test Phase 1: `python main.py --init` CLI command."""
    monkeypatch.setattr(sys, "argv", ["main.py", "--init"])
    all_inputs = DEFAULT_IDENTITY_INPUTS + API_KEY_INPUTS_FULL
    with patch('builtins.input', side_effect=all_inputs) as mock_input:
        main_cli_entry_func()

    expected_log_config_path = os.path.join('config', 'identity.yaml')
    assert f"Identity configuration saved to {expected_log_config_path}" in caplog.text
    assert f"Environment variables saved to .env" in caplog.text # ENV_PATH is monkeypatched to ".env"
    assert mock_input.call_count == len(all_inputs)

def test_main_cli_rename_arg(temp_praximous_env, monkeypatch, caplog):
    """Test Phase 1: `python main.py --rename` CLI command."""
    env_paths = temp_praximous_env
    identity_file = env_paths["identity_file_path"]
    
    with open(identity_file, 'w') as f: yaml.dump({"system_name": "OriginalName"}, f)

    new_cli_name = "Praximous-ViaCLI"
    monkeypatch.setattr(sys, "argv", ["main.py", "--rename", new_cli_name])
    main_cli_entry_func()

    assert f"System renamed from 'OriginalName' to '{new_cli_name}'" in caplog.text
    with open(identity_file, 'r') as f: data = yaml.safe_load(f)
    assert data["system_name"] == new_cli_name

def test_main_cli_reset_arg(temp_praximous_env, monkeypatch, caplog):
    """Test Phase 1: `python main.py --reset-identity` CLI command."""
    env_paths = temp_praximous_env
    identity_file = env_paths["identity_file_path"]

    with open(identity_file, 'w') as f: yaml.dump({"system_name": "ToBeReset"}, f)
    
    monkeypatch.setattr(sys, "argv", ["main.py", "--reset-identity"])
    with patch('builtins.input', return_value='yes'):
        main_cli_entry_func()

    expected_log_path = os.path.join('config', 'identity.yaml')
    assert f"Identity configuration file '{expected_log_path}' has been removed." in caplog.text
    assert not identity_file.exists()