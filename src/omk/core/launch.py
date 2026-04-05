"""
Launcher core for oh-my-kimi (Python version).
Orchestrates environment setup, AGENTS.md injection, and Kimi CLI execution.
"""

import os
import subprocess
import uuid
from pathlib import Path
from typing import List, Optional
from omk.utils import paths, config
from omk.hooks.agents_overlay import AgentsOverlayManager

async def launch_kimi(args: List[str], cwd: Optional[Path] = None):
    """
    Sets up the session-scoped environment and launches the Kimi CLI.
    """
    cwd = cwd or Path.cwd()
    session_id = str(uuid.uuid4())[:8]
    
    # 1. Prepare Overlay
    overlay_manager = AgentsOverlayManager(cwd=cwd, session_id=session_id)
    session_agents_path = await overlay_manager.write_session_scoped_agents()
    
    # 2. Prepare Environment Variables
    env = os.environ.copy()
    
    # Load keys from config.toml [env]
    env_overrides = config.get_env_vars()
    for k, v in env_overrides.items():
        env[k] = str(v)
        
    # Inject OMK specific environment
    env["OMK_SESSION_ID"] = session_id
    env["OMK_SESSION_AGENTS_PATH"] = str(session_agents_path)
    
    # Crucially, we need to tell the underlying CLI to use our session-scoped AGENTS.md
    # For Kimi-native CLI, this often involves a specific flag or an environment override
    # depending on how it's implemented. For now, we assume it looks at a specific dir.
    
    # 3. Construct command
    # Assuming 'kimi' is the executable. We might need to resolve its path.
    cmd = ["kimi"] + args
    
    # Add flags to use the session-scoped instructions if supported
    # cmd += ["--instructions", str(session_agents_path)]
    
    print(f"--- [OMK] Launching session {session_id} ---")
    
    try:
        # Launching as a child process, inheriting stdin/stdout/stderr
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"--- [OMK] Session {session_id} exited with code {e.returncode} ---")
    except FileNotFoundError:
        print("Error: 'kimi' executable not found in PATH. Please ensure Kimi Code CLI is installed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(launch_kimi(["--version"]))
