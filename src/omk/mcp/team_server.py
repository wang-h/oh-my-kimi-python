"""
OMK Team Orchestration MCP Server.
Provides tools for coordinating multi-agent teams via tmux.
"""

import os
import json
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from omk.utils.tmux_manager import TmuxManager

mcp = FastMCP("omk_team_run")

@mcp.tool()
def delegate_to_worker(worker_index: int, task: str) -> str:
    """
    Send a task to a specific worker pane in the current tmux session.
    """
    try:
        mgr = TmuxManager()
        pane = mgr.get_current_pane()
        if not pane:
            return "Error: Not running inside tmux or could not detect pane."
        
        window = pane.window
        # Look for the worker pane. OMK convention: leader is %0 or first, 
        # workers are subsequent panes.
        # This is a simplified lookup logic.
        panes = window.panes
        if worker_index < 0 or worker_index >= len(panes):
            return f"Error: Worker index {worker_index} out of range (total panes: {len(panes)})"
        
        target_pane = panes[worker_index]
        # In OMK, we usually send an 'ask' command to the worker
        cmd = f"omk ask {json.dumps(task)}"
        mgr.send_to_pane(target_pane, cmd)
        
        return f"Task delegated to worker {worker_index}."
    except Exception as e:
        return f"Error delegating task: {e}"

@mcp.tool()
def get_team_status() -> str:
    """
    List all panes in the current window and their identifiers.
    """
    try:
        mgr = TmuxManager()
        pane = mgr.get_current_pane()
        if not pane:
            return "Not in tmux."
        
        panes_info = []
        for i, p in enumerate(pane.window.panes):
            panes_info.append({
                "index": i,
                "pane_id": p.pane_id,
                "active": p.pane_active == '1'
            })
        return json.dumps(panes_info, indent=2)
    except Exception as e:
        return f"Error getting status: {e}"

if __name__ == "__main__":
    mcp.run()
