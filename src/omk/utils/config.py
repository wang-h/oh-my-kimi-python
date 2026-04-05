"""
Configuration parser for oh-my-kimi.
Reads and parses ~/.kimi/config.toml (or fallback).
"""
import tomlkit
from typing import Dict, Any, Optional
from omk.utils import paths

def load_config() -> Dict[str, Any]:
    """
    Loads the provider config.toml.
    Returns an empty dict if the file does not exist or cannot be parsed.
    """
    config_path = paths.provider_config_path()
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            doc = tomlkit.load(f)
            return dict(doc)
    except Exception as e:
        print(f"Warning: Failed to parse {config_path}: {e}")
        return {}

def get_global_setting(key: str, default: Any = None) -> Any:
    """Retrieve a top-level setting from config.toml."""
    config = load_config()
    return config.get(key, default)

def get_mcp_servers() -> Dict[str, Any]:
    """Retrieve the [mcp_servers] section."""
    config = load_config()
    return config.get("mcp_servers", {})

def get_env_vars() -> Dict[str, Any]:
    """Retrieve the [env] section which contains API keys and overrides."""
    config = load_config()
    return config.get("env", {})

if __name__ == "__main__":
    # Debug info
    print("--- Loaded Config snippet ---")
    cfg = load_config()
    print(f"Model: {cfg.get('model')}")
    print(f"Env vars loaded: {list(get_env_vars().keys())}")
    print(f"MCP Servers loaded: {list(get_mcp_servers().keys())}")
