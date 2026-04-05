"""
Path utilities for oh-my-kimi (Python version).
Resolves provider home/config, skills, prompts, agents, and OMK state.
"""

import os
from pathlib import Path
from typing import Optional, List, Union

PRIMARY_PROVIDER_HOME_ENV = "KIMI_HOME"
PRIMARY_PROVIDER_HOME_DIRNAME = ".kimi"
LEGACY_PROVIDER_HOME_ENV = "CODEX_HOME"
LEGACY_PROVIDER_HOME_DIRNAME = ".codex"

def get_home_dir() -> Path:
    """Get the user's home directory safely."""
    return Path.home()

def provider_home() -> Path:
    """
    Canonical provider home directory (~/.kimi/) with legacy CODEX_HOME fallback.
    Prioritizes .kimi if it exists, otherwise falls back to .codex.
    """
    # 1. Check environment variables
    if os.getenv(PRIMARY_PROVIDER_HOME_ENV):
        return Path(os.environ[PRIMARY_PROVIDER_HOME_ENV])
    if os.getenv(LEGACY_PROVIDER_HOME_ENV):
        return Path(os.environ[LEGACY_PROVIDER_HOME_ENV])

    # 2. Check existence in home directory
    primary_home = get_home_dir() / PRIMARY_PROVIDER_HOME_DIRNAME
    legacy_home = get_home_dir() / LEGACY_PROVIDER_HOME_DIRNAME

    return primary_home if primary_home.exists() else legacy_home

def legacy_codex_home() -> Path:
    """Legacy Codex home directory (~/.codex/) or CODEX_HOME."""
    env_home = os.getenv(LEGACY_PROVIDER_HOME_ENV)
    return Path(env_home) if env_home else get_home_dir() / LEGACY_PROVIDER_HOME_DIRNAME

def provider_config_path() -> Path:
    """Canonical provider config file path (~/.kimi/config.toml)."""
    return provider_home() / "config.toml"

def provider_prompts_dir() -> Path:
    """Canonical provider prompts directory (~/.kimi/prompts/)."""
    return provider_home() / "prompts"

def provider_agents_dir(home_dir: Optional[Union[str, Path]] = None) -> Path:
    """Canonical provider native agents directory (~/.kimi/agents/)."""
    base = Path(home_dir) if home_dir else provider_home()
    return base / "agents"

def project_provider_root_dir(project_root: Optional[Union[str, Path]] = None) -> Path:
    """Project-level provider root (.kimi/ or .codex/)."""
    root = Path(project_root) if project_root else Path.cwd()
    primary_project = root / PRIMARY_PROVIDER_HOME_DIRNAME
    legacy_project = root / LEGACY_PROVIDER_HOME_DIRNAME
    return primary_project if primary_project.exists() else legacy_project

def provider_user_skills_dir() -> Path:
    """User-level provider skills directory (~/.kimi/skills/)."""
    return provider_home() / "skills"

def project_provider_skills_dir(project_root: Optional[Union[str, Path]] = None) -> Path:
    """Project-level provider skills directory (.kimi/skills/)."""
    return project_provider_root_dir(project_root) / "skills"

# Backward-compatible aliases (matching npm version's legacy support)
def codex_home() -> Path:
    return legacy_codex_home()

def user_skills_dir() -> Path:
    return provider_user_skills_dir()

def project_skills_dir(project_root: Optional[Union[str, Path]] = None) -> Path:
    return project_provider_skills_dir(project_root)

# OMK specific runtime paths
def omk_runtime_root(project_root: Optional[Union[str, Path]] = None) -> Path:
    """The .omk directory for runtime logs and state."""
    root = Path(project_root) if project_root else Path.cwd()
    return root / ".omk"

def omk_state_dir(project_root: Optional[Union[str, Path]] = None) -> Path:
    return omk_runtime_root(project_root) / "state"

def omk_logs_dir(project_root: Optional[Union[str, Path]] = None) -> Path:
    return omk_runtime_root(project_root) / "logs"

if __name__ == "__main__":
    # Quick debug info
    print(f"Provider Home: {provider_home()}")
    print(f"User Skills: {user_skills_dir()}")
    print(f"Project Root: {project_provider_root_dir()}")
