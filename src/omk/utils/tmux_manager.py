"""
Tmux management utilities for oh-my-kimi (Python version).
Handles session orchestration, pane splitting, and layout management using libtmux.
"""

import os
import time
import libtmux
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

class TmuxManager:
    def __init__(self):
        self.server = libtmux.Server()

    def get_current_pane(self) -> Optional[libtmux.Pane]:
        """Detect the current tmux pane if running inside tmux."""
        tmux_pane_id = os.getenv("TMUX_PANE")
        if not tmux_pane_id:
            return None
        
        try:
            for session in self.server.sessions:
                for window in session.windows:
                    for pane in window.panes:
                        if pane.pane_id == tmux_pane_id:
                            return pane
        except Exception:
            pass
        return None

    def ensure_in_tmux(self):
        """Check if the process is running inside tmux."""
        if not os.getenv("TMUX"):
            raise RuntimeError("This command must be run inside a tmux session.")

    def create_team_layout(self, worker_count: int, task: str):
        """
        Creates and initializes the team layout.
        Ensures workers are started with the correct environment.
        """
        pane = self.get_current_pane()
        if not pane:
            raise RuntimeError("Could not detect current tmux pane.")

        window = pane.window
        # 1. Clear window - OMK convention is to have a dedicated window for team
        # (For now, we just split from current)

        # 2. Split for Workers
        worker_panes = []
        # First split creates the right stack
        right_root = window.split_window(vertical=False, attach=False)
        worker_panes.append(right_root)

        # Subsequent workers split the right column
        for i in range(1, worker_count):
            new_worker = right_root.split_window(vertical=True, attach=False)
            worker_panes.append(new_worker)

        # 3. Apply Layout
        window.select_layout("main-vertical")
        window.cmd("set-window-option", "main-pane-width", "55%") # Slightly more for leader
        window.select_layout("main-vertical")

        # 4. HUD pane at the bottom
        hud_pane = window.split_window(vertical=True, full=True, size=2, attach=False)
        
        # 5. Initialize Workers
        # We need to make sure 'omk' command is available in workers.
        # We'll use the absolute path to the venv python to be safe.
        python_bin = "/Users/hao/codex/oh-my-kimi-python/venv/bin/python3"
        main_py = "/Users/hao/codex/oh-my-kimi-python/src/omk/main.py"
        
        for i, w_pane in enumerate(worker_panes):
            # Command to launch worker agent
            worker_cmd = f"export PYTHONPATH=$PYTHONPATH:/Users/hao/codex/oh-my-kimi-python/src; {python_bin} {main_py} ask 'You are Worker-{i+1}. Your task: {task}'"
            w_pane.send_keys(worker_cmd, enter=True)

        # 6. Initialize HUD
        hud_cmd = f"export PYTHONPATH=$PYTHONPATH:/Users/hao/codex/oh-my-kimi-python/src; {python_bin} {main_py} hud --watch"
        hud_pane.send_keys(hud_cmd, enter=True)

        return {
            "leader": pane,
            "workers": worker_panes,
            "hud": hud_pane
        }

    def send_to_pane(self, pane: libtmux.Pane, text: str, enter: bool = True):
        pane.send_keys(text, enter=enter)
