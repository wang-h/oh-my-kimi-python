"""
OMK Project Memory MCP Server.
Provides tools for persistent project-level memory (tech stack, decisions, etc).
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from mcp.server.fastmcp import FastMCP
from omk.utils import paths

mcp = FastMCP("omk_memory")

def get_memory_path(cwd: Optional[str] = None) -> Path:
    """Resolve the path for project memory."""
    base_dir = paths.omk_runtime_root(Path(cwd) if cwd else None)
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "project-memory.json"

@mcp.tool()
def memory_write(
    tech_stack: Optional[str] = None,
    conventions: Optional[str] = None,
    directives: Optional[List[Dict[str, str]]] = None,
    cwd: Optional[str] = None
) -> str:
    """
    Update project memory.
    directives should be a list of {'directive': '...', 'priority': 'high|medium|low'}
    """
    path = get_memory_path(cwd)
    try:
        data = {}
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        if tech_stack: data["techStack"] = tech_stack
        if conventions: data["conventions"] = conventions
        if directives: data["directives"] = directives
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return f"Project memory updated at {path}"
    except Exception as e:
        return f"Error updating memory: {e}"

@mcp.tool()
def memory_read(cwd: Optional[str] = None) -> str:
    """
    Read project memory.
    """
    path = get_memory_path(cwd)
    if not path.exists():
        return "No project memory found."
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error reading memory: {e}"

if __name__ == "__main__":
    mcp.run()
