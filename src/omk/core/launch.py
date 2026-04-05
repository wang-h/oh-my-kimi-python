"""
Enhanced Launcher core for oh-my-kimi (Python version).
Now integrates with the native Skill system and optimized AGENTS.md overlays.
"""

import os
import subprocess
import uuid
import sys
from pathlib import Path
from typing import List, Optional
from omk.utils import paths, config
from omk.hooks.agents_overlay import AgentsOverlayManager
from omk.core.skills import SkillManager

async def launch_kimi(args: List[str], cwd: Optional[Path] = None):
    """
    Sets up the session-scoped environment and launches the Kimi CLI.
    """
    cwd = Path(cwd) if cwd else Path.cwd()
    session_id = str(uuid.uuid4())[:8]
    
    # 1. Handle Keyword Routing (Skills)
    # If the first argument is $name, it might be a skill
    if args and args[0].startswith("$"):
        skill_name = args[0][1:]
        sm = SkillManager(project_root=cwd)
        # Check if it's a python skill
        for s in sm.list_skills():
            if s["name"] == skill_name and s["type"] == "python":
                print(f"--- [OMK] Routing to Python skill: {skill_name} ---")
                return sm.run_python_skill(skill_name, args[1:])

    # 2. Prepare Overlay
    overlay_manager = AgentsOverlayManager(cwd=cwd, session_id=session_id)
    session_agents_path = await overlay_manager.write_session_scoped_agents()
    
    # 3. Prepare Environment Variables
    env = os.environ.copy()
    
    # Load keys from config.toml [env]
    env_overrides = config.get_env_vars()
    for k, v in env_overrides.items():
        env[k] = str(v)
        
    # Inject OMK specific environment
    env["OMK_SESSION_ID"] = session_id
    env["OMK_SESSION_AGENTS_PATH"] = str(session_agents_path)
    
    # 4. Construct command
    # We use 'kimi' as the base command. 
    # If we want to be fancy, we'd add --instructions override if kimi-cli supports it.
    cmd = ["kimi"] + args
    
    print(f"--- [OMK] Launching session {session_id} ---")
    print(f"--- [OMK] Instruction Overlay: {session_agents_path} ---")
    
    try:
        # Launching as a child process
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"--- [OMK] Session {session_id} exited with code {e.returncode} ---")
    except FileNotFoundError:
        print("Error: 'kimi' executable not found. Please ensure Kimi Code CLI is installed.")
    finally:
        # Cleanup session agents if desired
        pass

if __name__ == "__main__":
    import asyncio
    asyncio.run(launch_kimi([]))
