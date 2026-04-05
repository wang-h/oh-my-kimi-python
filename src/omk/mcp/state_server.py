"""
OMK State Management MCP Server.
Provides tools for reading and writing global and session-specific state.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP
from omk.utils import paths

mcp = FastMCP("omk_state")

def get_state_path(mode: str, session_id: Optional[str] = None) -> Path:
    """Resolve the path for a mode's state file."""
    if session_id:
        base_dir = paths.omk_state_dir() / "sessions" / session_id
    else:
        base_dir = paths.omk_state_dir()
    
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"{mode}.json"

@mcp.tool()
def state_write(mode: str, data: Dict[str, Any], session_id: Optional[str] = None) -> str:
    """
    Write state data for a specific mode (e.g., 'ralph', 'autopilot').
    """
    path = get_state_path(mode, session_id)
    try:
        # Merge with existing data if it exists
        existing = {}
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        
        existing.update(data)
        existing["_last_updated"] = str(Path().cwd()) # Marker for updates
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
        return f"Successfully updated state for '{mode}' at {path}"
    except Exception as e:
        return f"Error writing state: {e}"

@mcp.tool()
def state_read(mode: str, session_id: Optional[str] = None) -> str:
    """
    Read state data for a specific mode.
    """
    path = get_state_path(mode, session_id)
    if not path.exists():
        return f"No state found for mode '{mode}'"
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error reading state: {e}"

if __name__ == "__main__":
    mcp.run()
